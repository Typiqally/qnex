import numpy as np
from dash import Input, Output, dcc
import plotly.graph_objects as go
from plotly.graph_objs.bar.marker import Pattern

from src.backend.qiskit.qiskit_utils import deserialize_statevector


def create_visualization_shots(app):
    fig = go.Figure()
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
        xaxis_title="Computational basis states",
        yaxis_title="Counts",
        barmode='group',  # Group bars together
        title="Counts<br><sup>Measurement counts for each quantum basis state from circuit execution.</sup>",
        height=384,  # Set chart height
        margin={'t': 50, 'b': 24, 'l': 36, 'r': 36},
    )

    # Add Ideal series (blue bars)
    fig.add_trace(go.Bar(
        name='Ideal',
        marker=dict(color='blue')
    ))

    # Add Noisy series (red bars)
    fig.add_trace(go.Bar(
        name='Noisy',
        marker=dict(color='red', pattern=Pattern(shape='/')),
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

    return dcc.Graph(id='visualization-shots', figure=fig)
