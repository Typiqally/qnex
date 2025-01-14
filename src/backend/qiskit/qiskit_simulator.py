import random
from typing import Optional

import numpy as np
from natsort import natsorted
from qiskit import qasm3, qasm2
from qiskit_aer import QasmSimulator
from qiskit_aer.noise import NoiseModel, pauli_error, amplitude_damping_error, phase_damping_error, depolarizing_error, thermal_relaxation_error

from src.backend.base_simulator import BaseSimulator
from src.backend.qiskit.qiskit_utils import insert_save_statevectors
from src.backend.types import NoiseParameterType, Gate, StatevectorResult, SimulationResult
from src.utils.complex_utils import serialize_complex_array


class QiskitSimulator(BaseSimulator):
    def __init__(self):
        self.simulator = QasmSimulator()

    def load_circuit(self, qasm_str: str):
        # Check the QASM version in the input string
        if "OPENQASM 3.0;" in qasm_str:
            # Parse the QASM string as qasm3
            circuit = qasm3.loads(qasm_str)
        else:
            # Parse the QASM string as qasm2 (default or assumed version)
            circuit = qasm2.loads(qasm_str)

        # Insert save statevectors into the circuit
        return circuit

    def create_noise_model(self, noise_model: dict) -> NoiseModel:
        model = NoiseModel()
        supported_gates = self.supported_operations()

        for gate_ref, noise_model_gate in noise_model.items():
            quantum_errors = []
            gate = supported_gates[gate_ref]

            print(f"Applying noise to gate: {gate}, {noise_model_gate}")

            # TODO: Not functioning correctly, using bit flip for now
            # if gate_ref == "measure":
            #     # Handle readout error separately for the "measure" gate
            #     readout_error_prob = noise_model_gate.get(NoiseParameterType.READOUT_ERROR.value, 0) / 100
            #     readout_error = ReadoutError([
            #         [1 - readout_error_prob, readout_error_prob],
            #         [readout_error_prob, 1 - readout_error_prob],
            #     ])
            #
            #     model.add_all_qubit_readout_error(readout_error)

            gate_time = noise_model_gate.get('gate_time', 0)
            t1 = noise_model_gate.get('t1', 30)  # Default T1 if not provided
            t2 = noise_model_gate.get('t2', 20)  # Default T2 if not provided

            # Check for each noise model type and apply corresponding noise
            for noise_type in NoiseParameterType:
                error = None

                if noise_type in gate.supported_noise_params:
                    noise_param_value = noise_model_gate.get(noise_type.value, None)

                    if noise_type == NoiseParameterType.THERMAL_RELAXATION:
                        if noise_param_value:
                            error = thermal_relaxation_error(t1, t2, gate_time)
                    else:
                        try:
                            noise_prob = float(noise_param_value or 0) / 100
                        except ValueError:
                            noise_prob = 0

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
        normalized_prob = max(min(prob, 1), 0)

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

    def simulate(self, qasm_str: str, shots: int, seed: Optional[int], noise_params: dict) -> SimulationResult:
        # Loaded
        circuit = insert_save_statevectors(self.load_circuit(qasm_str))

        num_qubits = circuit.num_qubits
        num_outcomes = 2 ** num_qubits
        basis_states = [format(i, f'0{num_qubits}b') for i in range(num_outcomes)]

        # Ensure that seed is the same for both simulator runs
        if seed is None:
            seed = random.randint(1, 99999)

        noise_model = self.create_noise_model(noise_params)

        print(f"Executing simulation with seed {seed} and noise model", noise_model)

        result_ideal = self.simulator.run(circuit, shots=shots, seed_simulator=seed).result()
        result_noisy = self.simulator.run(circuit, shots=shots, seed_simulator=seed, noise_model=noise_model).result()

        result_ideal_svs = {name: data for name, data in natsorted(result_ideal.data(0).items()) if name.startswith('sv')}
        result_noisy_svs = {name: data for name, data in natsorted(result_noisy.data(0).items()) if name.startswith('sv')}

        def process_result(results):
            processed = {}

            for name, data in results.items():
                processed[name] = []

                for sv in data:
                    sv.seed(seed)
                    sample_counts = sv.sample_counts(shots)

                    counts = np.array([sample_counts.get(key, 0) for key in basis_states])
                    probabilities = sv.probabilities() * 100

                    processed[name].append(StatevectorResult(serialize_complex_array(sv.data), counts, probabilities))

            return processed

        return SimulationResult(basis_states, process_result(result_ideal_svs), process_result(result_noisy_svs))

    def supported_operations(self):
        return {
            "id": Gate(
                short_name="I",
                long_name="I (Identity)",
                description="No-op (does nothing)",
                supported_noise_params=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.PHASE_DAMPING,
                                        NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "x": Gate(
                short_name="X",
                long_name="X (Pauli-X)",
                description="Bit-flip gate",
                supported_noise_params=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.PHASE_DAMPING,
                                        NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "y": Gate(
                short_name="Y",
                long_name="Y (Pauli-Y)",
                description="Combination of X and Z rotations",
                supported_noise_params=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.PHASE_DAMPING,
                                        NoiseParameterType.AMPLITUDE_DAMPING,
                                        NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "z": Gate(
                short_name="Z",
                long_name="Z (Pauli-Z)",
                description="Phase-flip gate",
                supported_noise_params=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.PHASE_DAMPING,
                                        NoiseParameterType.AMPLITUDE_DAMPING,
                                        NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "h": Gate(
                short_name="H",
                long_name="H (Hadamard)",
                description="Creates superposition states",
                supported_noise_params=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.PHASE_DAMPING,
                                        NoiseParameterType.AMPLITUDE_DAMPING,
                                        NoiseParameterType.DEPOLARIZING, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "s": Gate(
                short_name="S",
                long_name="S (Phase)",
                description="π/2 phase shift",
                supported_noise_params=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "sdg": Gate(
                short_name="SDG",
                long_name="S-dagger",
                description="Inverse of Phase gate",
                supported_noise_params=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "t": Gate(
                short_name="T",
                long_name="T (π/4)",
                description="π/4 phase shift",
                supported_noise_params=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "tdg": Gate(
                short_name="TDG",
                long_name="T-dagger",
                description="Inverse of T-gate",
                supported_noise_params=[NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "rx": Gate(
                short_name="RX",
                long_name="RX",
                description="Rotation around X-axis by θ radians",
                supported_noise_params=[NoiseParameterType.BIT_FLIP, NoiseParameterType.AMPLITUDE_DAMPING, NoiseParameterType.DEPOLARIZING,
                                        NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "ry": Gate(
                short_name="RY",
                long_name="RY",
                description="Rotation around Y-axis by θ radians",
                supported_noise_params=[NoiseParameterType.BIT_FLIP, NoiseParameterType.AMPLITUDE_DAMPING, NoiseParameterType.DEPOLARIZING,
                                        NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "rz": Gate(
                short_name="RZ",
                long_name="RZ",
                description="Rotation around Z-axis by θ radians",
                supported_noise_params=[NoiseParameterType.BIT_FLIP, NoiseParameterType.AMPLITUDE_DAMPING, NoiseParameterType.DEPOLARIZING,
                                        NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "cx": Gate(
                short_name="CNOT",
                long_name="CX (CNOT)",
                description="Entangles two qubits (Controlled-NOT)",
                supported_noise_params=[NoiseParameterType.DEPOLARIZING],
                num_qubits=2
            ),
            "cz": Gate(
                short_name="CZ",
                long_name="CZ (Controlled-Z)",
                description="Controlled-Z gate",
                supported_noise_params=[NoiseParameterType.DEPOLARIZING, NoiseParameterType.PHASE_FLIP],
                num_qubits=2
            ),
            "swap": Gate(
                short_name="SWAP",
                long_name="SWAP",
                description="Swaps the states of two qubits",
                supported_noise_params=[NoiseParameterType.DEPOLARIZING, NoiseParameterType.BIT_FLIP],
                num_qubits=2
            ),
            "ccx": Gate(
                short_name="CCX",
                long_name="CCX (Toffoli)",
                description="Three-qubit controlled-controlled-NOT",
                supported_noise_params=[NoiseParameterType.DEPOLARIZING, NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP],
                num_qubits=3
            ),
            "ccz": Gate(
                short_name="CCZ",
                long_name="CCZ",
                description="Three-qubit controlled-controlled-Z",
                supported_noise_params=[NoiseParameterType.DEPOLARIZING, NoiseParameterType.BIT_FLIP, NoiseParameterType.PHASE_FLIP],
                num_qubits=3
            ),
            "u": Gate(
                short_name="U",
                long_name="Unitary",
                description="Unitary gate",
                supported_noise_params=[NoiseParameterType.PHASE_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "u1": Gate(
                short_name="U1",
                long_name="U1",
                description="Phase gate (equivalent to RZ)",
                supported_noise_params=[NoiseParameterType.PHASE_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "u2": Gate(
                short_name="U2",
                long_name="U2",
                description="General single-qubit gate (π rotation)",
                supported_noise_params=[NoiseParameterType.PHASE_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "u3": Gate(
                short_name="U3",
                long_name="U3",
                description="General single-qubit gate (arbitrary rotation)",
                supported_noise_params=[NoiseParameterType.AMPLITUDE_DAMPING, NoiseParameterType.PHASE_FLIP, NoiseParameterType.THERMAL_RELAXATION],
                num_qubits=1
            ),
            "measure": Gate(
                short_name="M",
                long_name="M (Measurement)",
                description="Reads the qubit state into classical memory",
                supported_noise_params=[NoiseParameterType.BIT_FLIP],
                num_qubits=1
            ),
            "barrier": Gate(
                short_name="B",
                long_name="Barrier",
                description="Prevents simplification and optimization across the barrier",
                supported_noise_params=[],
                num_qubits=-1
            )
        }

    def used_operations(self, qasm_str: str):
        circuit = self.load_circuit(qasm_str)

        # Define the blacklist of gates to exclude
        blacklist = ['save_statevector']

        # Extract all gate names, excluding those in the blacklist
        used_gates = [
            op[0].name for op in circuit.data if op[0].name not in blacklist
        ]

        return used_gates
