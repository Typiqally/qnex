import base64
from io import BytesIO

import dash.html
from dash import Output, Input
from qiskit import qasm3
from qiskit.visualization import circuit_drawer


def create_circuit_diagram(app):
    @app.callback(
        Output('qasm-circuit-diagram', 'src'),
        Input('input-qasm', 'value')
    )
    def update_diagram(qasm):
        try:
            # Load the circuit from QASM
            circuit = qasm3.loads(qasm)

            # Draw the circuit with customized style
            fig = circuit_drawer(circuit, output='mpl', style={
                'name': 'iqp-dark',
                'backgroundcolor': '#242424'  # Set the background color
            })

            # Remove padding by adjusting the figure layout
            fig.tight_layout(pad=0)

            # Save to a buffer
            buffer = BytesIO()
            fig.savefig(buffer, bbox_inches='tight', pad_inches=0)  # bbox_inches='tight' helps minimize padding
            buffer.seek(0)

            # Encode image as base64
            img_str = base64.b64encode(buffer.read()).decode()

            # Return the image as a base64-encoded PNG
            return f'data:image/png;base64,{img_str}'

        except qasm3.QASM3ImporterError:
            # Provide fallback image in case of error
            return 'assets/error.png'
        except Exception as e:
            # Catch other potential errors
            print(f"Error generating circuit diagram: {e}")
            return 'assets/error.png'

    return dash.html.Img(id='qasm-circuit-diagram', style={'width': 'fit-content'})
