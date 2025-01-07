import dash_mantine_components as dmc

from src.dashboard.components.molecules.qasm_input import create_qasm_input
from src.dashboard.styling import default_border


def create_pane_qasm(app):
    return dmc.Container(
        dmc.Stack([
            dmc.Title("OpenQASM", order=4),
            create_qasm_input(app),
            dmc.Divider(variant="solid"),
        ]),
        pt="sm",
        w="30rem",
    )
