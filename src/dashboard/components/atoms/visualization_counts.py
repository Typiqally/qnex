from dash import Input, Output, dcc
import plotly.graph_objects as go
from plotly.graph_objs.bar.marker import Pattern


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
        Output('visualization-counts', 'figure'),
        Input('simulation-results', 'data'),
        Input('select-state-vector', 'value'),
        Input('input-visualize-shot', 'value')
    )
    def update_data(simulation_results, selected_state_vector, selected_shot):
        if selected_state_vector is None:
            fig.update_traces(selector=dict(name="Ideal"), y=[])
            fig.update_traces(selector=dict(name="Noisy"), y=[])

            return fig

        # Extract ideal and noisy state vectors
        selected_shot_index = selected_shot - 1

        # TODO: This is currently a bit ugly, need to find better alternative for this
        if selected_state_vector == list(simulation_results['ideal'].keys())[-1]:
            counts_ideal = [simulation_results['ideal_counts'].get(state, 0) for state in simulation_results['basis_states']]
            counts_noisy = [simulation_results['noisy_counts'].get(state, 0) for state in simulation_results['basis_states']]
        else:
            counts_ideal = simulation_results['ideal'][selected_state_vector][selected_shot_index]['counts']
            counts_noisy = simulation_results['noisy'][selected_state_vector][selected_shot_index]['counts']

        fig.update_traces(
            selector=dict(name="Ideal"),
            x=simulation_results['basis_states'],
            y=counts_ideal
        )
        fig.update_traces(
            selector=dict(name="Noisy"),
            x=simulation_results['basis_states'],
            y=counts_noisy
        )

        return fig

    return dcc.Graph(id='visualization-counts', figure=fig)
