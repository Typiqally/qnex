import dash_mantine_components as dmc
from dash import dcc

from qnex.dashboard.components.molecules.params_execution import create_params_execution
from qnex.dashboard.components.molecules.params_noise import create_params_noise
from qnex.dashboard.components.molecules.params_simulation import create_params_simulation


def create_pane_simulation(app):
    return dmc.Container(
        dmc.Stack([
            dcc.Store(id='simulation-results'),
            dcc.Store(id='simulation-noisy-results'),
            create_params_simulation(),
            dmc.Divider(variant="solid"),
            create_params_noise(app),
            dmc.Divider(variant="solid"),
            create_params_execution(app)
        ]),
        pt="sm",
        w="30rem",
    )
