import dash_mantine_components as dmc
from dash import Dash, _dash_renderer

from src.dashboard.components.organisms.pane_params import create_pane_params
from src.dashboard.components.organisms.pane_qasm import create_pane_qasm
from src.dashboard.components.organisms.pane_visualizations import create_visualizations
from src.dashboard.components.organisms.toolbar import create_toolbar

# Dash Mantine Components is based on REACT 18. You must set the env variable REACT_VERSION=18.2.0 before starting up the app.
_dash_renderer._set_react_version("18.2.0")

# Define external scripts
external_scripts = [
    # # Add the Tailwind CDN url hosting the files with the utility classes
    # {'src': 'https://cdn.tailwindcss.com'},
    'https://fonts.googleapis.com/css2?family=Poiret+One&display=swap',
]

# Initialize Dash app
app = Dash(__name__, external_scripts=external_scripts + dmc.styles.ALL)

# https://stackoverflow.com/questions/69258350/difficulty-getting-custom-google-font-working-for-plotly-dash-app
app.css.config.serve_locally = True

app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    theme={
        "primaryColor": "blue",
        "fontFamily": "'Inter', sans-serif",
    },
    children=dmc.Container(
        dmc.Stack(
            [
                # Add toolbar
                create_toolbar(),

                # TODO: Notification stuff
                # dmc.Affix(children=[
                #     dmc.NotificationProvider(),
                #     html.Div(id="notifications-container")
                # ], position={"bottom": 20, "right": 20}),

                # Main content area
                dmc.Flex(
                    [
                        create_pane_qasm(app),
                        create_visualizations(app),
                        create_pane_params(app),
                    ],
                    h="100%"
                ),
            ],
            gap=0,
            h="100%"
        ),
        h="100vh",
        fluid=True
    )
)

if __name__ == '__main__':
    app.run_server(debug=True)
