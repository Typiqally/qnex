import dash_mantine_components as dmc

from dash import dcc
from src.dashboard.components.molecules.params_execution import create_params_execution
from src.dashboard.components.molecules.params_noise import create_params_noise
from src.dashboard.components.molecules.params_simulation import create_params_simulation
from src.dashboard.styling import default_border


def create_pane_params(app):
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
