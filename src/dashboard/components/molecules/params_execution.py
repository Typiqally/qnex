import dash_mantine_components as dmc
from dash import State, Input, Output

from src.backend.registry import SIMULATOR_REGISTRY


def create_params_execution(app):
    @app.callback(
        Output('simulation-results', 'data'),
        Input('btn-simulation-run', 'n_clicks'),
        Input('select-simulator', 'value'),
        State('input-qasm', 'value'),
        Input('input-shots', 'value'),
        Input('noise-model', 'data'),
        prevent_initial_call=True
    )
    def display_values(_, simulator_ref, qasm_str, shots, current_noise_model):
        # Check if the simulator exists in the SIMULATOR_REGISTRY
        simulator = SIMULATOR_REGISTRY.get(simulator_ref, None)

        if not simulator:
            # Return an empty array if simulator does not exist
            return []

        # Load the current circuit
        simulator.load_circuit(qasm_str)

        # Simulate the circuit with ideal and noisy conditions
        results_ideal, results_noisy = simulator.simulate(shots or 1, current_noise_model)

        # Return the processed results
        return {
            'ideal': results_ideal,
            'noisy': results_noisy,
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
