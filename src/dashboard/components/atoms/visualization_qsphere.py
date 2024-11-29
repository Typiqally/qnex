import dash_mantine_components as dmc
import numpy as np
from dash import Input, Output, dcc
import plotly.graph_objects as go


def statevector_to_bloch(statevector):
    # Flattening and ensuring the statevector is a 1D array
    statevector = np.array(statevector).flatten()

    # Normalize the statevector (it should already be normalized, but let's ensure it)
    statevector = statevector / np.linalg.norm(statevector)

    # Extract alpha and beta for a single qubit
    alpha = statevector[0] + 1j * statevector[1]  # Real and Imaginary parts of statevector[0]
    beta = statevector[2] + 1j * statevector[3]  # Real and Imaginary parts of statevector[1]

    # Calculate theta and phi
    theta = 2 * np.arccos(np.abs(alpha))  # Inclination
    phi = np.angle(beta)  # Azimuthal angle (angle of beta)

    return theta, phi


def create_visualization_qsphere(app):
    # @app.callback(
    #     Output('visualization-qsphere', 'figure'),
    #     Input('simulation-results', 'data'),
    #     Input('select-state-vector', 'value'),
    #     prevent_initial_call=True
    # )
    # def update_data(simulation_results, state_vector):
    # Reduced resolution for faster rendering
    u = np.linspace(0, 2 * np.pi, 30)  # Reduce number of points
    v = np.linspace(0, np.pi, 15)  # Reduce number of points
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))

    # Flatten the coordinates for plotting
    x = x.flatten()
    y = y.flatten()
    z = z.flatten()

    # Create the wireframe by connecting points along u and v directions
    edges_u = []
    edges_v = []

    # Create edges along u direction (latitudinal)
    for i in range(len(u)):
        for j in range(len(v) - 1):
            edges_u.append([i * len(v) + j, i * len(v) + (j + 1)])

    # Create edges along v direction (longitudinal)
    for j in range(len(v)):
        for i in range(len(u) - 1):
            edges_v.append([i * len(v) + j, (i + 1) * len(v) + j])

    # Create the wireframe plot
    fig = go.Figure()

    # Add wireframe edges
    for edge in edges_u + edges_v:
        fig.add_trace(go.Scatter3d(
            x=[x[edge[0]], x[edge[1]]],
            y=[y[edge[0]], y[edge[1]]],
            z=[z[edge[0]], z[edge[1]]],
            mode='lines',
            line=dict(color='grey', width=2),
            showlegend=False
        ))

    # Update layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(showbackground=False),
            yaxis=dict(showbackground=False),
            zaxis=dict(showbackground=False)
        ),
        plot_bgcolor='#1e1e1e',  # Dark background
        paper_bgcolor='#1e1e1e',  # Dark paper background,
        font_color='#ffffff',
        transition={'duration': 400, 'easing': "cubic-in-out"},
        margin={'t': 24, 'b': 24, 'l': 36, 'r': 36}
    )

    return dmc.Stack(
        [
            dmc.Title('Q-Sphere', order=4),
            dcc.Graph(id='visualization-qsphere', figure=fig),
        ]
    )
