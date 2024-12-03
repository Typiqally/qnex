import dash_mantine_components as dmc
from dash import Output, Input

from src.dashboard.components.atoms.visualization_circuit_diagram import create_visualizatioh_circuit_diagram
from src.dashboard.components.atoms.visualization_counts import create_visualization_shots
from src.dashboard.components.atoms.visualization_fidelity import create_visualization_fidelity
from src.dashboard.components.atoms.visualization_probabilities import create_visualization_probabilities
from src.dashboard.components.atoms.visualization_qsphere import create_visualization_qsphere


def create_visualizations(app):
    @app.callback(
        Output('select-state-vector', 'data'),
        Input('simulation-results', 'data'),
        prevent_initial_call=True
    )
    def update_state_vector_select(simulator_results):
        simulator_results_ideal = simulator_results['ideal']
        sv_keys = [key for key in simulator_results_ideal.keys() if key.startswith('sv')]

        return sv_keys

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
            dmc.Stack(
                [
                    dmc.Title("Quantum Circuit", order=4),
                    create_visualizatioh_circuit_diagram(app),
                ],
                p="sm"
            ),
            dmc.Divider(variant="solid", my="none"),
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
                        ),
                        dmc.GridCol(
                            create_visualization_qsphere(app),
                            span=6
                        ),
                        dmc.GridCol(
                            create_visualization_fidelity(app),
                            span=6
                        )
                    ],
                    gutter='md'
                )
            ], p="sm")
        ],
        h="100%",
        w="100%"
    )
