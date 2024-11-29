import base64
from io import BytesIO

import plotly.graph_objects as go
from dash import Output, Input, dcc
from qiskit import qasm3
from qiskit.visualization import circuit_drawer


def create_visualizatioh_circuit_diagram(app):
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor="#1e1e1e",  # Set background color
        plot_bgcolor="#1e1e1e",  # Set plot area background color
        margin={'t': 24, 'b': 24, 'l': 36, 'r': 36},
        xaxis=dict(
            zerolinecolor="#333333",
            gridcolor="#333333",  # Set grid color to light gray
            range=[0, 1],
            tickfont_color="#fff",
        ),
        yaxis=dict(
            zerolinecolor="#333333",
            gridcolor="#333333",  # Set grid color to light gray
            range=[-1, 0],
            tickfont_color="#fff",
        ),
        dragmode='pan'  # Set the default interaction mode to pan
    )

    @app.callback(
        Output('visualization-circuit-diagram', 'figure'),
        Input('input-qasm', 'value')
    )
    def update_diagram(qasm):
        try:
            # Load the circuit from QASM
            circuit = qasm3.loads(qasm)
            # circuit = insert_save_statevectors(circuit)

            # Draw the circuit with customized style
            circuit_fig = circuit_drawer(circuit, output='mpl', style={
                'name': 'iqp-dark',
                'backgroundcolor': '#1e1e1e'  # Set the background color
            })

            # Remove padding by adjusting the figure layout
            circuit_fig.tight_layout(pad=0)

            # Save to a buffer
            buffer = BytesIO()
            circuit_fig.savefig(buffer, bbox_inches='tight', pad_inches=0)  # bbox_inches='tight' helps minimize padding
            buffer.seek(0)

            fig.update_layout(
                images=[
                    dict(
                        source=f'data:image/png;base64,{base64.b64encode(buffer.read()).decode()}',
                        xref="x",
                        yref="y",
                        x=0,
                        y=0,
                        sizex=1,
                        sizey=1,
                        xanchor="left",
                        yanchor="bottom",
                        layer="above",
                    )
                ],
                xaxis=dict(range=[0, 1]),
                yaxis=dict(range=[0, 1]),
            )

            # Return the image as a base64-encoded PNG
            return fig
        except qasm3.QASM3ImporterError:
            # Provide fallback image in case of error
            return fig
        except Exception as e:
            # Catch other potential errors
            print(f"Error generating circuit diagram: {e}")
            return fig

    return dcc.Graph(id='visualization-circuit-diagram', figure=fig)
