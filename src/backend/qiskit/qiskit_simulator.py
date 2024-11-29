from natsort import natsorted
from qiskit import qasm3
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, pauli_error, amplitude_damping_error, phase_damping_error, depolarizing_error, thermal_relaxation_error

from src.backend.base_simulator import BaseSimulator, NoiseModelType, Gate
from src.backend.qiskit.qiskit_utils import insert_save_statevectors, serialize_statevector


class QiskitSimulator(BaseSimulator):
    def __init__(self):
        self.circuit = None

    def load_circuit(self, qasm_str: str):
        # Insert instructions to save statevectors in the circuit
        self.circuit = insert_save_statevectors(qasm3.loads(qasm_str))

    def create_noise_model(self, noise_params: dict) -> NoiseModel:
        noise_model = NoiseModel()
        supported_gates = self.supported_gates()

        for gate_ref, noise_params_gate in noise_params.items():
            quantum_errors = []
            gate = supported_gates[gate_ref]

            print(f"Applying noise to gate: {gate}, {noise_params_gate}")

            if gate_ref == "measure":
                # Handle readout error separately for the "measure" gate
                readout_error_prob = noise_params_gate.get('readout-error', 0) / 100
                readout_error = ReadoutError([
                    [1 - readout_error_prob, readout_error_prob],
                    [readout_error_prob, 1 - readout_error_prob],
                ])
                noise_model.add_all_qubit_readout_error(readout_error)
                continue

            # Check for each noise model type and apply corresponding noise
            noise_types = {
                NoiseModelType.BIT_FLIP: 'bit-flip',
                NoiseModelType.PHASE_FLIP: 'phase-flip',
                NoiseModelType.AMPLITUDE_DAMPING: 'amplitude-damping',
                NoiseModelType.PHASE_DAMPING: 'phase-damping',
                NoiseModelType.DEPOLARIZING: 'depolarizing',
                NoiseModelType.THERMAL_RELAXATION: 'thermal-relaxation',
            }

            for noise_type, param_key in noise_types.items():
                if noise_type in gate.noise_models:
                    error = None
                    if noise_type == NoiseModelType.THERMAL_RELAXATION:
                        thermal_relaxation_params = noise_params_gate.get(param_key, None)

                        if thermal_relaxation_params["enabled"]:
                            error = self._create_thermal_relaxation_error(thermal_relaxation_params)
                    else:
                        noise_prob = noise_params_gate.get(param_key, 0) / 100

                        if noise_prob > 0:
                            error = self._create_noise_error(noise_type, noise_prob, gate.num_qubits)

                    if error:
                        quantum_errors.append(error)

            # Combine quantum errors and add to the noise model
            if quantum_errors:
                combined_error = quantum_errors[0]
                for quantum_error in quantum_errors[1:]:
                    combined_error = combined_error.compose(quantum_error)

                noise_model.add_all_qubit_quantum_error(combined_error, [gate_ref])

        return noise_model

    def _create_noise_error(self, noise_type: NoiseModelType, prob: float, num_qubits: int):
        """Helper method to create the correct error for a given noise type and probability."""
        normalized_prob = max(min(round(prob, 2), 1), 0)

        if noise_type == NoiseModelType.BIT_FLIP:
            return pauli_error([('X', normalized_prob), ('I', 1 - normalized_prob)])
        elif noise_type == NoiseModelType.PHASE_FLIP:
            return pauli_error([('Z', normalized_prob), ('I', 1 - normalized_prob)])
        elif noise_type == NoiseModelType.AMPLITUDE_DAMPING:
            return amplitude_damping_error(normalized_prob)
        elif noise_type == NoiseModelType.PHASE_DAMPING:
            return phase_damping_error(normalized_prob)
        elif noise_type == NoiseModelType.DEPOLARIZING:
            return depolarizing_error(normalized_prob, num_qubits)
        return None

    def _create_thermal_relaxation_error(self, thermal_relaxation_params: dict):
        """Helper method to create thermal relaxation error using Qiskit's thermal_relaxation_error."""
        gate_time = thermal_relaxation_params.get('gate-time', 0)
        t1 = thermal_relaxation_params.get('t1', 30)  # Default T1 if not provided
        t2 = thermal_relaxation_params.get('t2', 20)  # Default T2 if not provided

        if not t2 <= 2 * t1:
            raise Exception("")

        # Generate the thermal relaxation error
        return thermal_relaxation_error(t1, t2, gate_time)

    def simulate(self, shots: int, noise_params: dict):
        ideal_simulator = AerSimulator()
        noisy_simulator = AerSimulator(noise_model=self.create_noise_model(noise_params))

        # Apply noise model if provided
        result_ideal = ideal_simulator.run(self.circuit, shots=shots, memory=True).result()
        result_noisy = noisy_simulator.run(self.circuit, shots=shots, memory=True).result()

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
                noise_models=[NoiseModelType.BIT_FLIP, NoiseModelType.PHASE_FLIP, NoiseModelType.PHASE_DAMPING, NoiseModelType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "x": Gate(
                name="X (Pauli-X)",
                description="Bit-flip gate",
                noise_models=[NoiseModelType.BIT_FLIP, NoiseModelType.PHASE_FLIP, NoiseModelType.PHASE_DAMPING, NoiseModelType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "y": Gate(
                name="Y (Pauli-Y)",
                description="Combination of X and Z rotations",
                noise_models=[NoiseModelType.BIT_FLIP, NoiseModelType.PHASE_FLIP, NoiseModelType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "z": Gate(
                name="Z (Pauli-Z)",
                description="Phase-flip gate",
                noise_models=[NoiseModelType.BIT_FLIP, NoiseModelType.PHASE_FLIP, NoiseModelType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "h": Gate(
                name="H (Hadamard)",
                description="Creates superposition states",
                noise_models=[NoiseModelType.BIT_FLIP, NoiseModelType.PHASE_FLIP, NoiseModelType.PHASE_DAMPING, NoiseModelType.AMPLITUDE_DAMPING,
                              NoiseModelType.DEPOLARIZING, NoiseModelType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "s": Gate(
                name="S (Phase)",
                description="π/2 phase shift",
                noise_models=[NoiseModelType.BIT_FLIP, NoiseModelType.PHASE_FLIP, NoiseModelType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "sdg": Gate(
                name="S-dagger",
                description="Inverse of Phase gate",
                noise_models=[NoiseModelType.BIT_FLIP, NoiseModelType.PHASE_FLIP, NoiseModelType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "t": Gate(
                name="T (π/4)",
                description="π/4 phase shift",
                noise_models=[NoiseModelType.BIT_FLIP, NoiseModelType.PHASE_FLIP, NoiseModelType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "tdg": Gate(
                name="T-dagger",
                description="Inverse of T-gate",
                noise_models=[NoiseModelType.BIT_FLIP, NoiseModelType.PHASE_FLIP, NoiseModelType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "rx": Gate(
                name="RX",
                description="Rotation around X-axis by θ radians",
                noise_models=[NoiseModelType.AMPLITUDE_DAMPING, NoiseModelType.BIT_FLIP],
                num_qubits=1
            ),
            "ry": Gate(
                name="RY",
                description="Rotation around Y-axis by θ radians",
                noise_models=[NoiseModelType.AMPLITUDE_DAMPING, NoiseModelType.BIT_FLIP, NoiseModelType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "rz": Gate(
                name="RZ",
                description="Rotation around Z-axis by θ radians",
                noise_models=[NoiseModelType.PHASE_FLIP, NoiseModelType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "cx": Gate(
                name="CX (CNOT)",
                description="Entangles two qubits (Controlled-NOT)",
                noise_models=[NoiseModelType.DEPOLARIZING],
                num_qubits=2
            ),
            "cz": Gate(
                name="CZ (Controlled-Z)",
                description="Controlled-Z gate",
                noise_models=[NoiseModelType.DEPOLARIZING, NoiseModelType.PHASE_FLIP],
                num_qubits=2
            ),
            "swap": Gate(
                name="SWAP",
                description="Swaps the states of two qubits",
                noise_models=[NoiseModelType.DEPOLARIZING, NoiseModelType.BIT_FLIP],
                num_qubits=2
            ),
            "ccx": Gate(
                name="CCX (Toffoli)",
                description="Three-qubit controlled-controlled-NOT",
                noise_models=[NoiseModelType.DEPOLARIZING, NoiseModelType.BIT_FLIP, NoiseModelType.PHASE_FLIP],
                num_qubits=3
            ),
            "u1": Gate(
                name="U1",
                description="Phase gate (equivalent to RZ)",
                noise_models=[NoiseModelType.PHASE_FLIP, NoiseModelType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "u2": Gate(
                name="U2",
                description="General single-qubit gate (π rotation)",
                noise_models=[NoiseModelType.PHASE_FLIP, NoiseModelType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "u3": Gate(
                name="U3",
                description="General single-qubit gate (arbitrary rotation)",
                noise_models=[NoiseModelType.AMPLITUDE_DAMPING, NoiseModelType.PHASE_FLIP, NoiseModelType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "measure": Gate(
                name="M (Measurement)",
                description="Reads the qubit state into classical memory",
                noise_models=[NoiseModelType.READOUT_ERROR],
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
