import dash_mantine_components as dmc

from src.dashboard.styling import default_border


def create_toolbar():
    return dmc.Flex(
        [
            dmc.Title("QC Noise Visualization", order=4),
        ],
        p="sm",
        direction={"base": "column", "sm": "row"},
        gap={"base": "sm", "sm": "lg"},
        align={"base": "center"},
        justify={"base": "space-between"},
        style={"border-bottom": default_border},
    )
