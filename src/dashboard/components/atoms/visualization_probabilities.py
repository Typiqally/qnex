import plotly.graph_objects as go
from dash import Input, Output, dcc
from plotly.graph_objs.bar.marker import Pattern


def create_visualization_probabilities(app):
    # Create a Plotly bar chart
    fig = go.Figure()

    # Layout for the chart
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
            range=[0, 100],
        ),
        xaxis_title="Computational basis states",
        yaxis_title="Probability (%)",
        barmode='group',  # Group bars together
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
        Output('visualization-probabilities', 'figure'),
        Input('simulation-results', 'data'),
        Input('input-visualize-shot', 'value'),
        Input('select-state-vector', 'value')
    )
    def update_data(simulation_results, selected_shot, selected_state_vector):
        if selected_state_vector is None:
            fig.update_traces(selector=dict(name="Ideal"), y=[])
            fig.update_traces(selector=dict(name="Noisy"), y=[])

            return fig

        selected_shot_index = selected_shot - 1

        # Extract ideal and noisy state vectors
        probabilities_ideal = simulation_results['ideal'][selected_state_vector][selected_shot_index]['probabilities']
        probabilities_noisy = simulation_results['noisy'][selected_state_vector][selected_shot_index]['probabilities']

        fig.update_layout(
            title=f"Probabilities for shot #{selected_shot}<br>"
                  f"<sup>Measurement probabilities for each quantum basis state.</sup>"
        )

        fig.update_traces(
            selector=dict(name="Ideal"),
            x=simulation_results['basis_states'],
            y=probabilities_ideal
        )
        fig.update_traces(
            selector=dict(name="Noisy"),
            x=simulation_results['basis_states'],
            y=probabilities_noisy
        )

        return fig

    return dcc.Graph(id='visualization-probabilities', figure=fig)
