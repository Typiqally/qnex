import base64
import json

import dash_mantine_components as dmc
from dash import dcc, Output, Input, State, ALL, ctx

from src.backend.registry import SIMULATOR_REGISTRY
from src.backend.types import NoiseParameterType


def create_probability_slider(noise_param: NoiseParameterType, value: int = 0):
    return dmc.Grid(
        [
            dmc.GridCol(
                dmc.Tooltip(
                    [
                        dmc.Text(noise_param.display_name, size="sm"),
                    ],
                    label=noise_param.description,
                    position="right",
                    multiline=True,
                    color="gray",
                    offset=3
                ),
                span=4
            ),
            dmc.GridCol(
                dmc.NumberInput(
                    id={"type": "noise-param", "index": noise_param.value},
                    value=value,
                    min=0,
                    max=100,
                    rightSection="%",
                ),
                span="auto"
            ),
        ],
        gutter="md"
    )


def create_switch(noise_param: NoiseParameterType, value: bool = False):
    return dmc.Flex(
        [
            dmc.Tooltip(
                [
                    dmc.Text(noise_param.display_name, size="sm")
                ],
                label=noise_param.description,
                position="right",
                multiline=True,
                color="gray",
                offset=3
            ),
            dmc.Switch(
                id={"type": "noise-param", "index": noise_param.value},
                checked=value
            ),
        ],
        justify="space-between"
    )


# TODO: This is so ugly, should find a nicer way for this
NOISE_PARAM_COMPONENT_MAP = {
    NoiseParameterType.DEPOLARIZING: lambda noise_model: create_probability_slider(
        NoiseParameterType.DEPOLARIZING,
        noise_model.get("depolarizing", 0)
    ),
    NoiseParameterType.AMPLITUDE_DAMPING: lambda noise_model: create_probability_slider(
        NoiseParameterType.AMPLITUDE_DAMPING,
        noise_model.get("amplitude_damping", 0)
    ),
    NoiseParameterType.PHASE_DAMPING: lambda noise_model: create_probability_slider(
        NoiseParameterType.PHASE_DAMPING,
        noise_model.get("phase_damping", 0)
    ),
    NoiseParameterType.READOUT_ERROR: lambda noise_model: create_probability_slider(
        NoiseParameterType.READOUT_ERROR,
        noise_model.get("readout_error", 0)
    ),
    NoiseParameterType.BIT_FLIP: lambda noise_model: create_probability_slider(
        NoiseParameterType.BIT_FLIP,
        noise_model.get("bit_flip", 0)
    ),
    NoiseParameterType.PHASE_FLIP: lambda noise_model: create_probability_slider(
        NoiseParameterType.PHASE_FLIP, noise_model.get("phase_flip", 0)),
    NoiseParameterType.THERMAL_RELAXATION: lambda noise_model: create_switch(
        NoiseParameterType.THERMAL_RELAXATION,
        noise_model.get("thermal_relaxation", False)
    )
}


def create_params_noise(app):
    @app.callback(
        Output('download-noise-model-export', 'data'),
        Input('btn-noise-model-export', 'n_clicks'),
        State('noise-model', 'data'),
        prevent_initial_call=True,
    )
    def export_noise_profile(_, noise_model):
        return dcc.send_string(json.dumps(noise_model), "noise_model.json")

    @app.callback(
        Output('noise-model', 'data'),
        Input('import-noise-model', 'contents'),
        prevent_initial_call=True,
    )
    def import_noise_model(contents_encoded):
        try:
            b64_part = contents_encoded.split(',')[1]
            contents_decoded = base64.b64decode(b64_part).decode('utf-8')

            return json.loads(contents_decoded)
        except Exception as e:
            raise e

    @app.callback(
        Output('select-gate', 'data'),
        Output('input-qasm', 'error'),
        Input('select-simulator-backend', 'value'),
        Input("input-qasm", "value"),
    )
    def update_select_gate_data(simulator_ref, qasm_str):
        # Check if the simulator exists in the SIMULATOR_REGISTRY
        simulator = SIMULATOR_REGISTRY.get(simulator_ref, None)

        if not simulator:
            # Return an empty array if simulator does not exist
            return []

        # Load the current circuit
        try:
            simulator.load_circuit(qasm_str)
        except Exception as e:
            return [], "QASM could not be interpreted, please validate for issues."

        # Get the gates from the simulator
        supported_gates = simulator.supported_gates()
        used_gates = simulator.used_gates()

        # Return the gates as a list of dicts with "value" and "label" keys
        return [{"value": gate_ref, "label": supported_gates[gate_ref].display_name} for gate_ref in used_gates]

    @app.callback(
        Output('noise-gate-params', 'children'),
        Input('select-gate', 'value'),
        Input('select-simulator', 'value'),
        State("noise-model", 'data'),
    )
    def update_gate_noise_model_children(gate_ref, simulator_ref, current_noise_model):
        # Check if the simulator exists in the SIMULATOR_REGISTRY
        simulator = SIMULATOR_REGISTRY.get(simulator_ref, None)

        if not simulator or not gate_ref:
            # Return an empty array if simulator does not existF
            return []

        gates = simulator.supported_operations()
        gate_info = gates[gate_ref]

        gate_noise_model_components = [
            NOISE_PARAM_COMPONENT_MAP[noise_param](current_noise_model.get(gate_ref, {}))
            for noise_param in gate_info.supported_noise_params
        ]

        other_components = [
            dmc.Alert(id="noise-gate-description", color="blue", children=gate_info.description),
            dmc.NumberInput(
                id={"type": "noise-param", "index": "gate_time"},
                label="Gate time",
                description="Execution time in nanoseconds",
                value=current_noise_model.get("gate_time", 50),
                rightSection="ns"
            ),
            dmc.Grid(
                [
                    dmc.GridCol(
                        dmc.NumberInput(
                            id={"type": "noise-param", "index": "t1"},
                            label="Relaxation Time (T1)",
                            value=current_noise_model.get("t1", 30),
                            rightSection="ns"),
                        span=6
                    ),
                    dmc.GridCol(
                        dmc.NumberInput(
                            id={"type": "noise-param", "index": "t2"},
                            label="Dephasing Time (T2)",
                            value=current_noise_model.get("t2", 20),
                            rightSection="ns"
                        ),
                        span=6)
                ]
            )
        ]

        return other_components + gate_noise_model_components

    @app.callback(
        Output("noise-model", "data", allow_duplicate=True),
        Input('select-gate', 'value'),
        Input({"type": "noise-param", "index": ALL}, "value"),
        Input({"type": "noise-param", "index": ALL}, "checked"),
        State("noise-model", "data"),
        prevent_initial_call=True,
    )
    def update_dynamic_params(gate_ref, values, checked_values, current_noise_model):
        current_noise_model = current_noise_model or {}

        if not gate_ref:
            return current_noise_model

        noise_gate_params = {}

        for input_item, param_checked in zip(ctx.inputs_list[1], checked_values):
            param_id = input_item["id"]["index"]  # Get the name of the index
            param_value = input_item.get("value", None)  # Get the value of the input

            if param_value is None:
                param_value = param_checked

            noise_gate_params[param_id] = param_value

        current_noise_model[gate_ref] = noise_gate_params

        return current_noise_model

    return dmc.Stack([
        dcc.Store(id='noise-model'),
        dcc.Download(id="download-noise-model-export"),
        dmc.Title("Noise model", order=4),
        dmc.Group(
            [
                dcc.Upload(
                    id="import-noise-model",
                    children=[
                        dmc.Button(
                            "Import",
                            color="gray",
                            w="100%"
                        )
                    ],
                ),
                dmc.Button(
                    "Export",
                    id="btn-noise-model-export"
                )
            ],
            grow=True
        ),
        dmc.Divider(label="Model editor", variant="dashed"),
        dmc.Select(
            label="Gate",
            placeholder="Select a gate",
            description="Select a gate to configure its noise parameters, only used gates are shown",
            id="select-gate",
            data=[]
        ),
        dmc.Stack(
            id="noise-gate-params",
            children=[],
            gap="xl"
        )
    ])
