import dash_mantine_components as dmc

from src.dashboard.components.molecules.qasm_input import create_qasm_input
from src.dashboard.styling import default_border


def create_pane_qasm(app):
    return dmc.Container(
        dmc.Stack([
            create_qasm_input(app),
            dmc.Divider(variant="solid"),
        ]),
        style={"border-right": default_border},
        pt="sm",
        w="30rem",
    )
