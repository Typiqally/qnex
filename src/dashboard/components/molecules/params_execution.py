import dash_mantine_components as dmc
from dash import State, Input, Output
from dash_iconify import DashIconify

from src.backend.registry import SIMULATOR_REGISTRY


def create_params_execution(app):
    @app.long_callback(
        Output('simulation-results', 'data'),
        Input('btn-simulation-run', 'n_clicks'),
        State('select-simulator-backend', 'value'),
        State('input-qasm', 'value'),
        State('input-shots', 'value'),
        State('input-seed', 'value'),
        State('noise-model', 'data'),
        prevent_initial_call=True,
        running=[
            (Output("btn-simulation-run", "loading"), True, False),
            (Output("btn-simulation-cancel", "disabled"), False, True),
        ],
        cancel=[Input("btn-simulation-cancel", "n_clicks")],
    )
    def display_values(_, simulator_ref, qasm_str, shots, seed, noise_model):
        # Check if the simulator exists in the SIMULATOR_REGISTRY
        simulator = SIMULATOR_REGISTRY.get(simulator_ref, None)

        if not simulator:
            # Return an empty array if simulator does not exist
            return []

        if not seed:
            seed = None

        # Load the current circuit
        simulator.load_circuit(qasm_str)

        # Simulate the circuit with ideal and noisy conditions
        results_ideal, results_noisy = simulator.simulate(shots or 1, seed, noise_model)

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
            max=8192,
        ),
        dmc.NumberInput(
            id='input-seed',
            label="Randomization seed",
            description="Seed used by the simulator to generate results, leave empty for random",
            placeholder="Choose random seed",
            value=None,
            min=1,
            max=99999,
        ),
        dmc.Flex(
            children=[
                dmc.Button('Run', id="btn-simulation-run", color='lime', fullWidth=True),
                dmc.ActionIcon(
                    DashIconify(icon="clarity:close-line", width=20),
                    color="red",
                    size="lg",
                    disabled=True,
                    variant="filled",
                    id="btn-simulation-cancel",
                )
            ],
            gap="md",
        )

    ])
