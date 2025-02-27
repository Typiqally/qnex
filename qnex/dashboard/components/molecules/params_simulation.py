import dash_mantine_components as dmc


def create_params_simulation():
    return dmc.Stack([
        dmc.Title("Simulation", order=4),
        dmc.Select(
            label="Backend",
            placeholder="Select one",
            id="select-simulator-backend",
            value="qiskit",
            required=True,
            data=[
                {"value": "qiskit", "label": "IBM Qiskit"},
                # TODO: Support more backends
                # {"value": "cirq", "label": "Google Cirq"},
                # {"value": "quantumsim", "label": "QuantumSim"},
            ]
        ),
    ])
