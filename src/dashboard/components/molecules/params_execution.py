import dash_mantine_components as dmc
import qiskit.qasm3
from dash import State, Input, Output
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, amplitude_damping_error, phase_damping_error, pauli_error, ReadoutError

from src.utils.qiskit_utils import insert_save_statevectors, serialize_statevector


def create_noise_model(noise_params) -> NoiseModel:
    # Initialize noise model
    noise_model = NoiseModel()

    # Example slider values (scale to probability, clamped between 0 and 1)
    p_depol = max(0, min(noise_params['noise_depolarizing'] / 100, 1))
    p_amp_damp = max(0, min(noise_params['noise_amplitude_damping'] / 100, 1))
    p_phase_damp = max(0, min(noise_params['noise_phase_damping'] / 100, 1))
    p_bit_flip = max(0, min(noise_params['noise_bit_flip'] / 100, 1))
    p_phase_flip = max(0, min(noise_params['noise_phase_flip'] / 100, 1))
    p_readout_error = max(0, min(noise_params['noise_readout_error'] / 100, 1))

    # Compute remaining probability for identity (I) operator
    remaining_probability = max(0, 1 - (p_bit_flip + p_phase_flip))

    # Define combined single-qubit errors (Pauli errors)
    error_ops = []
    if p_bit_flip > 0:
        error_ops.append(('X', p_bit_flip))
    if p_phase_flip > 0:
        error_ops.append(('Z', p_phase_flip))
    if remaining_probability > 0:
        error_ops.append(('I', remaining_probability))

    # Create a Pauli error if there are valid operators
    if error_ops:
        bit_phase_error = pauli_error(error_ops)
    else:
        raise ValueError("No valid error operators with non-zero probability")

    # Compose with depolarizing error for single-qubit gates
    bit_phase_error = bit_phase_error.compose(depolarizing_error(p_depol, 1))

    # Create other noise errors
    amp_damp_error = amplitude_damping_error(p_amp_damp)
    phase_damp_error = phase_damping_error(p_phase_damp)
    readout_error = ReadoutError([[1 - p_readout_error, p_readout_error], [p_readout_error, 1 - p_readout_error]])

    # Apply combined errors to all single-qubit gates
    single_qubit_gates = ['u1', 'u2', 'u3', 'x', 'y', 'z', 'h', 's', 'sdg', 't', 'tdg', 'rx', 'ry', 'rz']
    combined_single_qubit_error = bit_phase_error.compose(amp_damp_error).compose(phase_damp_error)
    noise_model.add_all_qubit_quantum_error(combined_single_qubit_error, single_qubit_gates)

    # Apply depolarizing error to two-qubit gates
    two_qubit_gates = ['cx', 'cz', 'cy', 'swap', 'rzz']
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p_depol, 2), two_qubit_gates)

    # Apply readout error to all qubits
    noise_model.add_all_qubit_readout_error(readout_error)

    return noise_model


def create_params_execution(app):
    @app.callback(
        Output('simulation-results', 'data'),
        Input('btn-simulation-run', 'n_clicks'),
        State('input-qasm', 'value'),
        Input('input-shots', 'value'),
        Input('noise-params', 'data'),
        prevent_initial_call=True
    )
    def display_values(_, qasm, shots, noise_params):
        # Load the QASM into a quantum circuit
        circuit = qiskit.qasm3.loads(qasm)

        # Insert instructions to save statevectors in the circuit
        circuit_monitor = insert_save_statevectors(circuit)

        # Simulate the circuit with ideal and noisy conditions
        ideal_simulator = AerSimulator()
        noisy_simulator = AerSimulator(noise_model=create_noise_model(noise_params))

        result_ideal = ideal_simulator.run(circuit_monitor, shots=shots, memory=True).result()
        result_noisy = noisy_simulator.run(circuit_monitor, shots=shots, memory=True).result()

        # Helper function to process results
        def process_results(results):
            return {
                name: [serialize_statevector(sv) for sv in value] if name.startswith('sv') else value
                for name, value in results.data(0).items()
            }

        # Return the processed results
        return {
            'ideal': process_results(result_ideal),
            'noisy': process_results(result_noisy),
        }

    return dmc.Stack([
        dmc.Title("Execution", order=4),
        dmc.NumberInput(
            id='input-shots',
            label="Execution iterations (shots)",
            description="How many times the loaded quantum circuit is simulated",
            value=100,
            min=1,
            max=10000,
        ),
        dmc.Button('Run', id="btn-simulation-run", color='lime')
    ])