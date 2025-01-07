import base64
from io import BytesIO

import plotly.graph_objects as go
from dash import Output, Input, dcc
from qiskit import qasm3, qasm2
from qiskit.visualization import circuit_drawer


def create_visualization_circuit_diagram(app):
    fig = go.Figure()
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='black',
        xaxis=dict(
            zerolinecolor="#ebebeb",
            gridcolor="#ebebeb",
            tickfont_color="black",
            range=[0, 1],
        ),
        yaxis=dict(
            zerolinecolor="#ebebeb",
            gridcolor="#ebebeb",
            tickfont_color="black",
            range=[-1, 0],
        ),
        margin={'t': 50, 'b': 24, 'l': 36, 'r': 36},
        height=350,
        title="Circuit Diagram",
        dragmode='pan'  # Set the default interaction mode to pan
    )

    @app.callback(
        Output('visualization-circuit-diagram', 'figure'),
        Input('input-qasm', 'value')
    )
    def update_diagram(qasm_str):
        try:
            # Load the circuit from QASM
            if "OPENQASM 3.0;" in qasm_str:
                # Parse the QASM string as qasm
                circuit = qasm3.loads(qasm_str)
            else:
                # Parse the QASM string as qasm3 (default or assumed version)
                circuit = qasm2.loads(qasm_str)

            # Draw the circuit with customized style
            circuit_fig = circuit_drawer(circuit, output='mpl', style={
                'backgroundcolor': '#00000000',
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
        except (qasm3.QASM3ImporterError, qasm2.QASM2ParseError) as e:
            # Provide fallback image in case of error
            return fig
        except Exception as e:
            # Catch other potential errors
            print(f"Error generating circuit diagram: {e}")
            return fig

    return dcc.Graph(id='visualization-circuit-diagram', figure=fig)
