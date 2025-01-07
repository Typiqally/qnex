import dash_mantine_components as dmc

from src.dashboard.styling import default_border


def create_toolbar():
    return dmc.Flex(
        [
            dmc.Group(
                [
                    dmc.Title("QNEX", order=4),
                    dmc.Text("v1.0")
                ],
                gap="xs"
            )
        ],
        p="sm",
        direction={"base": "column", "sm": "row"},
        gap={"base": "sm", "sm": "lg"},
        align={"base": "center"},
        style={"border-bottom": default_border},
    )
