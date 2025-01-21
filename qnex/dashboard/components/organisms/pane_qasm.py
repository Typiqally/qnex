import dash_mantine_components as dmc

from qnex.dashboard.components.molecules.qasm_input import create_qasm_input


def create_pane_qasm(app):
    return dmc.Container(
        dmc.Stack([
            dmc.Title("OpenQASM", order=4),
            dmc.Text(
                [
                    "For designing quantum circuits, you can use various quantum circuit designer tools such as ",
                    dmc.Anchor(
                        "IBM Composer",
                        href="https://quantum.ibm.com/composer/",
                        target="_blank",
                    ),
                    " and ",
                    dmc.Anchor(
                        "The Quantum Laend Quantum Circuit Simulator",
                        href="https://thequantumlaend.de/quantum-circuit-designer/",
                        target="_blank",
                    ),
                ],
                size="sm"
            ),
            create_qasm_input(app),
            dmc.Divider(variant="solid"),
        ]),
        pt="sm",
        w="30rem",
    )
