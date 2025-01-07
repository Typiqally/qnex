from natsort import natsorted
from qiskit import qasm3, qasm2
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, pauli_error, amplitude_damping_error, phase_damping_error, depolarizing_error, thermal_relaxation_error

from src.backend.base_simulator import BaseSimulator
from src.backend.qiskit.qiskit_utils import insert_save_statevectors, serialize_statevector
from src.backend.types import NoiseParameterType, Gate


class QiskitSimulator(BaseSimulator):
    def __init__(self):
        self.circuit = None
        self.simulator = AerSimulator()

    def load_circuit(self, qasm_str: str):
        # Check the QASM version in the input string
        if "OPENQASM 3.0;" in qasm_str:
            # Parse the QASM string as qasm3
            circuit = qasm3.loads(qasm_str)
        else:
            # Parse the QASM string as qasm2 (default or assumed version)
            circuit = qasm2.loads(qasm_str)

        # Insert save statevectors into the circuit
        self.circuit = insert_save_statevectors(circuit)

    def create_noise_model(self, noise_model: dict) -> NoiseModel:
        model = NoiseModel()
        supported_gates = self.supported_gates()

        for gate_ref, noise_model_gate in noise_model.items():
            quantum_errors = []
            gate = supported_gates[gate_ref]

            print(f"Applying noise to gate: {gate}, {noise_model_gate}")

            if gate_ref == "measure":
                # Handle readout error separately for the "measure" gate
                readout_error_prob = noise_model_gate.get('readout-error', 0) / 100
                readout_error = ReadoutError([
                    [1 - readout_error_prob, readout_error_prob],
                    [readout_error_prob, 1 - readout_error_prob],
                ])
                model.add_all_qubit_readout_error(readout_error)
                continue

            gate_time = noise_model_gate.get('gate-time', 0)
            t1 = noise_model_gate.get('t1', 30)  # Default T1 if not provided
            t2 = noise_model_gate.get('t2', 20)  # Default T2 if not provided

            if not t2 <= 2 * t1:
                raise Exception("")

            # Check for each noise model type and apply corresponding noise
            noise_types = {
                NoiseParameterType.BIT_FLIP: 'bit-flip',
                NoiseParameterType.PHASE_FLIP: 'phase-flip',
                NoiseParameterType.AMPLITUDE_DAMPING: 'amplitude-damping',
                NoiseParameterType.PHASE_DAMPING: 'phase-damping',
                NoiseParameterType.DEPOLARIZING: 'depolarizing',
                NoiseParameterType.THERMAL_RELAXATION: 'thermal-relaxation',
            }

            for noise_type, param_key in noise_types.items():
                if noise_type in gate.noise_models:
                    error = None

                    noise_param = noise_model_gate.get(param_key, None)

                    if noise_type == NoiseParameterType.THERMAL_RELAXATION:
                        if noise_param:
                            error = thermal_relaxation_error(t1, t2, gate_time)
                    else:
                        noise_prob = noise_model_gate.get(param_key, 0) / 100

                        if noise_prob > 0:
                            error = self._create_noise_error(noise_type, noise_prob, gate.num_qubits)

                    if error:
                        quantum_errors.append(error)

            # Combine quantum errors and add to the noise model
            if quantum_errors:
                combined_error = quantum_errors[0]
                for quantum_error in quantum_errors[1:]:
                    combined_error = combined_error.compose(quantum_error)

                model.add_all_qubit_quantum_error(combined_error, [gate_ref])

        return model

    def _create_noise_error(self, noise_type: NoiseParameterType, prob: float, num_qubits: int):
        """Helper method to create the correct error for a given noise type and probability."""
        normalized_prob = max(min(round(prob, 2), 1), 0)

        if noise_type == NoiseParameterType.BIT_FLIP:
            return pauli_error([('X', normalized_prob), ('I', 1 - normalized_prob)])
        elif noise_type == NoiseParameterType.PHASE_FLIP:
            return pauli_error([('Z', normalized_prob), ('I', 1 - normalized_prob)])
        elif noise_type == NoiseParameterType.AMPLITUDE_DAMPING:
            return amplitude_damping_error(normalized_prob)
        elif noise_type == NoiseParameterType.PHASE_DAMPING:
            return phase_damping_error(normalized_prob)
        elif noise_type == NoiseParameterType.DEPOLARIZING:
            return depolarizing_error(normalized_prob, num_qubits)

        return None

    def simulate(self, shots: int, seed: Optional[int], noise_model_params: dict):
        # Ensure that seed is the same for both simulator runs
        if seed is None:
            seed = random.randint(1, 10000)

        noise_model = self.create_noise_model(noise_model_params)
        # noise_model = NoiseModel.from_backend(FakeSantiagoV2())

        # Apply noise model if provided
        result_ideal = self.simulator.run(self.circuit, shots=shots, memory=True, seed_simulator=seed).result()
        result_noisy = self.simulator.run(self.circuit, shots=shots, memory=True, seed_simulator=seed, noise_model=noise_model).result()

        # TODO: Move utility function
        def process_results(results):
            return {
                name: [serialize_statevector(sv) for sv in value] if name.startswith('sv') else value
                for name, value in natsorted(results.data(0).items())
            }

        return process_results(result_ideal), process_results(result_noisy)

    def supported_gates(self):
        return {
            "id": Gate(
                name="I (Identity)",
                description="No-op (does nothing)",
                supported_noise_model=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.PHASE_DAMPING, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "x": Gate(
                name="X (Pauli-X)",
                description="Bit-flip gate",
                supported_noise_model=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.PHASE_DAMPING, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "y": Gate(
                name="Y (Pauli-Y)",
                description="Combination of X and Z rotations",
                supported_noise_model=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.PHASE_DAMPING, NoiseParameterType.AMPLITUDE_DAMPING,
                                        NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "z": Gate(
                name="Z (Pauli-Z)",
                description="Phase-flip gate",
                supported_noise_model=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.PHASE_DAMPING, NoiseParameterType.AMPLITUDE_DAMPING,
                                        NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "h": Gate(
                name="H (Hadamard)",
                description="Creates superposition states",
                supported_noise_model=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.PHASE_DAMPING, NoiseParameterType.AMPLITUDE_DAMPING,
                                        NoiseParameterType.DEPOLARIZING, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "s": Gate(
                name="S (Phase)",
                description="π/2 phase shift",
                supported_noise_model=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "sdg": Gate(
                name="S-dagger",
                description="Inverse of Phase gate",
                supported_noise_model=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "t": Gate(
                name="T (π/4)",
                description="π/4 phase shift",
                supported_noise_model=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "tdg": Gate(
                name="T-dagger",
                description="Inverse of T-gate",
                supported_noise_model=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "rx": Gate(
                name="RX",
                description="Rotation around X-axis by θ radians",
                supported_noise_model=[NoiseParameterType.AMPLITUDE_DAMPING, NoiseParameterType.BIT_FLIP],
                num_qubits=1
            ),
            "ry": Gate(
                name="RY",
                description="Rotation around Y-axis by θ radians",
                supported_noise_model=[NoiseParameterType.AMPLITUDE_DAMPING, NoiseParameterType.BIT_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "rz": Gate(
                name="RZ",
                description="Rotation around Z-axis by θ radians",
                supported_noise_model=[NoiseParameterType.PHASE_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "cx": Gate(
                name="CX (CNOT)",
                description="Entangles two qubits (Controlled-NOT)",
                supported_noise_model=[NoiseParameterType.DEPOLARIZING],
                num_qubits=2
            ),
            "cz": Gate(
                name="CZ (Controlled-Z)",
                description="Controlled-Z gate",
                supported_noise_model=[NoiseParameterType.DEPOLARIZING, NoiseParameterType.PHASE_FLIP],
                num_qubits=2
            ),
            "swap": Gate(
                name="SWAP",
                description="Swaps the states of two qubits",
                supported_noise_model=[NoiseParameterType.DEPOLARIZING, NoiseParameterType.BIT_FLIP],
                num_qubits=2
            ),
            "ccx": Gate(
                name="CCX (Toffoli)",
                description="Three-qubit controlled-controlled-NOT",
                supported_noise_model=[NoiseParameterType.DEPOLARIZING, NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP],
                num_qubits=3
            ),
            "u1": Gate(
                name="U1",
                description="Phase gate (equivalent to RZ)",
                supported_noise_model=[NoiseParameterType.PHASE_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "u2": Gate(
                name="U2",
                description="General single-qubit gate (π rotation)",
                supported_noise_model=[NoiseParameterType.PHASE_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "u3": Gate(
                name="U3",
                description="General single-qubit gate (arbitrary rotation)",
                supported_noise_model=[NoiseParameterType.AMPLITUDE_DAMPING, NoiseParameterType.PHASE_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "measure": Gate(
                name="M (Measurement)",
                description="Reads the qubit state into classical memory",
                supported_noise_model=[NoiseParameterType.READOUT_ERROR],
                num_qubits=1
            )
        }

    def used_gates(self):
        # If there's no circuit, return an empty list
        if not self.circuit:
            return []

        # Define the blacklist of gates to exclude
        blacklist = ['barrier', 'save_statevector']

        # Extract all gate names, excluding those in the blacklist
        used_gates = [
            op[0].name for op in self.circuit.data if op[0].name not in blacklist
        ]

        # Remove duplicates and return the list
        return list(set(used_gates))
