import dash_mantine_components as dmc
from dash import Output, Input

from src.backend.registry import SIMULATOR_REGISTRY
from src.dashboard.components.atoms.visualization_circuit_diagram import create_visualization_circuit_diagram
from src.dashboard.components.atoms.visualization_counts import create_visualization_shots
from src.dashboard.components.atoms.visualization_fidelity import create_visualization_fidelity
from src.dashboard.components.atoms.visualization_probabilities import create_visualization_probabilities


def create_visualizations(app):
    @app.callback(
        Output('select-state-vector', 'data'),
        Input('select-simulator-backend', 'value'),
        Input('simulation-results', 'data'),
        prevent_initial_call=True
    )
    def update_state_vector_select_data(simulator_ref, simulator_results):
        # Check if the simulator exists in the SIMULATOR_REGISTRY
        simulator = SIMULATOR_REGISTRY.get(simulator_ref, None)

        if not simulator:
            # Return an empty array if simulator does not exist
            return []

        supported_ops = simulator.supported_operations()
        used_ops = ["init"] + simulator.used_operations()

        simulator_results_ideal = simulator_results['ideal']
        sv_keys = [key for key in simulator_results_ideal.keys() if key.startswith('sv')]

        return [
            {
                "label": f"{i + 1}: {supported_ops[op].long_name if op != 'init' and op in supported_ops else ('Initialization Step' if op == 'init' else f'Unknown op ({op})')}",
                "value": sv}
            for i, (op, sv) in enumerate(zip(used_ops, sv_keys))
        ]

    @app.callback(
        Output('select-state-vector', 'value'),
        Input('select-state-vector', 'value'),
        Input('simulation-results', 'data'),
        prevent_initial_call=True
    )
    def update_state_vector_select_value(current_state_vector, simulator_results):
        if current_state_vector is not None:
            return current_state_vector

        simulator_results_ideal = simulator_results['ideal']
        sv_keys = [key for key in simulator_results_ideal.keys() if key.startswith('sv')]

        return sv_keys[0]

    @app.callback(
        Output('input-visualize-shot', 'max'),
        Output('input-visualize-shot', 'marks'),
        Input('input-shots', 'value')
    )
    def update_visualize_shot_max(shots):
        shots = shots or 1
        marks = [
            {"value": 0, "label": "1"},
            {"value": shots - 1, "label": str(shots)},
        ]

        return shots, marks

    return dmc.Stack(
        [
            dmc.Title("Visualization", order=4),
            dmc.Stack(
                [
                    create_visualization_fidelity(app),
                    create_visualization_circuit_diagram(app),
                ],
                gap="0"
            ),
            dmc.Stack([
                dmc.Flex(
                    [
                        dmc.Select(
                            id='select-state-vector',
                            label='Which state vectors to include in visualization?',
                            placeholder='Select state vectors',
                            data=[],
                            w='100%'
                        ),
                        dmc.Stack(
                            [
                                dmc.Text("Which execution/shot to visualize?", size="sm"),
                                dmc.Slider(
                                    id='input-visualize-shot',
                                    min=1,
                                    max=100,
                                    value=1
                                ),
                            ],
                            w='100%'
                        ),
                    ],
                    gap='md'
                ),
                dmc.Grid(
                    [
                        dmc.GridCol(
                            create_visualization_shots(app),
                            span=6
                        ),
                        dmc.GridCol(
                            create_visualization_probabilities(app),
                            span=6
                        )
                    ],
                    gutter='md'
                )
            ])
        ],
        h="100%",
        w="100%",
        p="sm",
        style={'background-color': 'rgb(250,250,250)'},
    )
