import dash_mantine_components as dmc
import numpy as np
from dash import Input, Output, dcc
import plotly.graph_objects as go

from src.backend.qiskit.qiskit_utils import deserialize_statevector


def create_visualization_probabilities(app):
    # Create a Plotly bar chart
    fig = go.Figure()

    # Layout for the chart
    fig.update_layout(
        xaxis_title="Computational basis states",
        yaxis_title="Probability (%)",
        xaxis=dict(
            zerolinecolor="#333333",
            gridcolor="#333333",  # Set grid color to light gray
            tickfont_color="#fff",
        ),
        yaxis=dict(
            zerolinecolor="#333333",
            gridcolor="#333333",  # Set grid color to light gray
            tickfont_color="#fff",
            range=[0, 100]
        ),
        barmode='group',  # Group bars together
        height=384,  # Set chart height
        plot_bgcolor='#1e1e1e',  # Dark background
        paper_bgcolor='#1e1e1e',  # Dark paper background,
        font_color='#ffffff',
        transition={'duration': 400, 'easing': "cubic-in-out"},
        margin={'t': 24, 'b': 24, 'l': 36, 'r': 36},
    )

    # Add Ideal series (blue bars)
    fig.add_trace(go.Bar(
        name='Ideal',
        marker_color='blue'
    ))

    # Add Noisy series (red bars)
    fig.add_trace(go.Bar(
        name='Noisy',
        marker_color='red'
    ))

    @app.callback(
        Output('visualization-probabilities', 'figure'),
        Input('simulation-results', 'data'),
        Input('input-visualize-shot', 'value'),
        Input('select-state-vector', 'value'),
        prevent_initial_call=True
    )
    def update_data(simulation_results, selected_shot, state_vector):
        if state_vector is None:
            fig.update_traces(selector=dict(name="Ideal"), y=[])
            fig.update_traces(selector=dict(name="Noisy"), y=[])

            return fig

        # Extract ideal and noisy state vectors
        state_vectors_ideal = simulation_results['ideal'][state_vector]
        state_vectors_noisy = simulation_results['noisy'][state_vector]
        probabilities_ideal = deserialize_statevector(state_vectors_ideal[selected_shot]).probabilities() * 100
        probabilities_noisy = deserialize_statevector(state_vectors_noisy[selected_shot]).probabilities() * 100

        # Determine the number of qubits
        num_results = len(state_vectors_ideal[0])  # Assuming state_vectors_ideal[0] exists and has correct size
        num_qubits = int(np.log2(num_results))

        # Generate binary combinations for results
        basis_states = [format(i, f'0{num_qubits}b') for i in range(num_results)]

        fig.update_traces(
            selector=dict(name="Ideal"),
            x=basis_states,
            y=probabilities_ideal
        )
        fig.update_traces(
            selector=dict(name="Noisy"),
            x=basis_states,
            y=probabilities_noisy
        )

        return fig

    return dmc.Stack(
        [
            dmc.Title('Probabilities', order=4),
            dcc.Graph(id='visualization-probabilities', figure=fig),
        ]
    )
