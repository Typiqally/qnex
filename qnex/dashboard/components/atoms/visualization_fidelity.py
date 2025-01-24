import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, dcc, State

from qnex.backend.registry import SIMULATOR_REGISTRY
from qnex.utils.quantum import compute_quantum_fidelity


def create_visualization_fidelity(app):
    # Create Plotly heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=[],  # Initial empty data
            colorscale='rdbu',
            colorbar=dict(
                title='Mean Fidelity',
                tickvals=[0, 0.5, 1],
                ticktext=['0', '0.5', '1'],
                tickmode='array',
                orientation='h',
                thickness=10,
            ),
            zmin=0,
            zmax=1
        )
    )

    # Update layout with titles and labels
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='black',
        xaxis=dict(
            zerolinecolor="#ebebeb",
            gridcolor="#ebebeb",
            tickfont_color="black",
        ),
        yaxis=dict(
            zerolinecolor="#ebebeb",
            gridcolor="#ebebeb",
            tickfont_color="black",
        ),
        margin={'t': 100, 'b': 24, 'l': 36, 'r': 36},
        height=140,
        title="Quantum State Fidelity<br><sup>Measures similarity between ideal and noisy quantum states</sup>",
    )

    @app.callback(
        Output('visualization-fidelity', 'figure'),
        Input('select-simulator-backend', 'value'),
        Input('simulation-results', 'data'),
        State('input-qasm', 'value')
    )
    def update_data(simulator_ref, simulation_results, qasm_str):
        # Check if the simulator exists in the SIMULATOR_REGISTRY
        simulator = SIMULATOR_REGISTRY.get(simulator_ref, None)

        if simulator is None or simulation_results is None:
            # Return an empty array if simulator does not exist
            return fig

        # Extract state vector keys and compute mean fidelity differences
        sv_keys = list(simulation_results['ideal'].keys())

        supported_ops = simulator.supported_operations()
        used_ops = ["init"] + simulator.used_operations(qasm_str)

        tick_text = [
            'Init' if op == 'init' else (supported_ops[op].short_name if op in supported_ops else f"?")
            for (op, sv) in zip(used_ops, sv_keys)
        ]

        mean_differences = [
            np.mean([compute_quantum_fidelity(sv_ideal['state_vector'], sv_noisy['state_vector']) for sv_ideal, sv_noisy in
                     zip(simulation_results['ideal'][sv_name], simulation_results['noisy'][sv_name])])
            for sv_name in sv_keys
        ]

        mean_differences = np.array(mean_differences).reshape(1, -1)

        fig.update_traces(z=mean_differences)
        fig.update_layout(
            xaxis={
                'tickmode': 'array',
                'tickvals': np.arange(len(mean_differences)),
                'ticktext': tick_text
            },
            yaxis={'tickvals': []},
        )

        return fig

    return dcc.Graph(id='visualization-fidelity', figure=fig)
