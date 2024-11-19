import dash_mantine_components as dmc
from dash import dcc


def create_params_simulation():
    return dmc.Stack([
        dmc.Title("Simulation", order=4),
        dmc.Select(
            label="Backend",
            placeholder="Select one",
            id="simulator-select",
            value="qiskit",
            required=True,
            data=[
                {"value": "qiskit", "label": "IBM Qiskit"},
                {"value": "cirq", "label": "Google Cirq"},
                {"value": "quantumsim", "label": "QuantumSim"},
            ]
        ),
    ])
