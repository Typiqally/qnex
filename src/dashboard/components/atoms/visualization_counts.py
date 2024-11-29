import copy

import dash_mantine_components as dmc
import numpy as np
from dash import Input, Output, dcc
import plotly.graph_objects as go

from src.backend.qiskit.qiskit_utils import deserialize_statevector


def create_visualization_shots(app):
    fig = go.Figure()
    fig.update_layout(
        xaxis_title="Computational basis states",
        yaxis_title="Counts",
        barmode='group',  # Group bars together
        height=384,  # Set chart height
        plot_bgcolor='#1e1e1e',  # Dark background
        paper_bgcolor='#1e1e1e',  # Dark paper background,
        font_color='#ffffff',
        transition={'duration': 400, 'easing': "cubic-in-out"},
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

    fig.add_trace(go.Bar(
        name='Ideal',
        marker_color='blue'
    ))

    fig.add_trace(go.Bar(
        name='Noisy',
        marker_color='red'
    ))

    @app.callback(
        Output('visualization-shots', 'figure'),
        Input('simulation-results', 'data'),
        Input('select-state-vector', 'value')
    )
    def update_data(simulation_results, state_vector):
        if state_vector is None:
            fig.update_traces(selector=dict(name="Ideal"), y=[])
            fig.update_traces(selector=dict(name="Noisy"), y=[])

            return fig

        # Extract ideal and noisy state vectors
        state_vectors_ideal = simulation_results['ideal'][state_vector]
        state_vectors_noisy = simulation_results['noisy'][state_vector]

        # Calculate probabilities from state vectors
        def calculate_totals(state_vectors):
            return (np.abs([deserialize_statevector(s) for s in state_vectors]) ** 2).sum(axis=0)

        totals_ideal = calculate_totals(state_vectors_ideal)
        totals_noisy = calculate_totals(state_vectors_noisy)

        # Determine the number of qubits
        num_results = len(state_vectors_ideal[0])  # Assuming state_vectors_ideal[0] exists and has correct size
        num_qubits = int(np.log2(num_results))

        # Generate binary combinations for results
        basis_states = [format(i, f'0{num_qubits}b') for i in range(num_results)]

        fig.update_traces(
            selector=dict(name="Ideal"),
            x=basis_states,
            y=totals_ideal
        )
        fig.update_traces(
            selector=dict(name="Noisy"),
            x=basis_states,
            y=totals_noisy
        )

        return fig

    return dmc.Stack(
        [
            dmc.Title('Shots', order=4),
            dcc.Graph(id='visualization-shots', figure=fig),
        ]
    )
