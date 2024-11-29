import dash_mantine_components as dmc
import numpy as np
from dash import Input, Output, dcc
import plotly.graph_objects as go

from src.utils.complex_utils import deserialize_complex_array


def compute_fidelity(sv1, sv2):
    # Ensure both state vectors are normalized
    sv1 = sv1 / np.linalg.norm(sv1)
    sv2 = sv2 / np.linalg.norm(sv2)

    # Compute the inner product and then square its magnitude to get fidelity
    fidelity = np.abs(np.vdot(sv1, sv2)) ** 2
    return fidelity


def create_visualization_fidelity(app):
    # Create Plotly heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=[],  # Initial empty data
            colorscale='rdbu',
            colorbar=dict(
                title='Mean Difference',
                tickvals=[0, 0.5, 1],
                ticktext=['0', '0.5', '1'],
                tickmode='array',
                orientation='h',
            ),
            zmin=0,
            zmax=1
        )
    )

    # Update layout with titles and labels
    fig.update_layout(
        plot_bgcolor='#1e1e1e',  # Dark background
        paper_bgcolor='#1e1e1e',  # Dark paper background
        font_color='#ffffff',
        transition={'duration': 400, 'easing': "cubic-in-out"},
        height=164,
        margin={'t': 24, 'b': 24, 'l': 36, 'r': 36},
        xaxis=dict(
            zerolinecolor="#333333",
            gridcolor="#333333",  # Set grid color to light gray
            tickfont_color="#fff",
        ),
        yaxis=dict(
            zerolinecolor="#333333",
            gridcolor="#333333",  # Set grid color to light gray
            tickfont_color="#fff",
        ),
    )

    @app.callback(
        Output('visualization-fidelity', 'figure'),
        Input('simulation-results', 'data'),
        Input('select-state-vector', 'value'),
        prevent_initial_call=True
    )
    def update_data(simulation_results, state_vector):
        # Extract state vector keys and compute mean fidelity differences
        sv_keys = [key for key in simulation_results['ideal'] if key.startswith('sv')]

        mean_differences = [
            np.mean([compute_fidelity(deserialize_complex_array(sv_ideal), deserialize_complex_array(sv_noisy)) for sv_ideal, sv_noisy in
                     zip(simulation_results['ideal'][sv_name], simulation_results['noisy'][sv_name])])
            for sv_name in sv_keys
        ]



        # Reshape the mean differences for a row-based heatmap (1xN)
        mean_differences = np.array(mean_differences).reshape(1, -1)

        # Update the figure trace with new data
        fig.update_traces(z=mean_differences )

        fig.update_layout(
            xaxis={'tickmode': 'array', 'tickvals': np.arange(len(mean_differences[0])), 'ticktext': sv_keys},
            yaxis={'tickvals': []},
        )

        return fig

    return dmc.Stack(
        [
            dmc.Title('Fidelity', order=4),
            dcc.Graph(id='visualization-fidelity', figure=fig),
        ]
    )
