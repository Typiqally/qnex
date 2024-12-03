import dash_mantine_components as dmc
from dash import dcc, Output, Input, State, ALL, ctx

from src.backend.base_simulator import NoiseModelType
from src.backend.registry import SIMULATOR_REGISTRY


def create_probability_slider(component_id_index: str, label: str, value: int = 0):
    return dmc.Grid(
        [
            dmc.GridCol(dmc.Text(label, size="sm"), span=4),
            dmc.GridCol(
                dmc.Slider(
                    id={"type": "noise-param", "index": component_id_index},
                    value=value,
                    marks=[
                        {"value": 0, "label": "0%"},
                        {"value": 50, "label": "50%"},
                        {"value": 100, "label": "100%"},
                    ],
                    w="100%"
                ),
                span="auto"
            )
        ]
    )


def create_switch(component_id_index: str, label: str, value: bool = False):
    return dmc.Flex(
        [
            dmc.Text(label, size="sm"),
            dmc.Switch(
                id={"type": "noise-param", "index": component_id_index},
                checked=value
            ),
        ],
        justify="space-between"
    )


# TODO: This is so ugly, should find a nicer way for this
NOISE_PARAMS_COMPONENT_MAP = {
    NoiseModelType.DEPOLARIZING: lambda noise_params: create_probability_slider(
        "depolarizing",
        "Depolarizing Probability",
        noise_params.get("depolarizing", 0)
    ),
    NoiseModelType.AMPLITUDE_DAMPING: lambda noise_params: create_probability_slider(
        "amplitude-damping",
        "Amplitude Damping",
        noise_params.get("amplitude-damping", 0)
    ),
    NoiseModelType.PHASE_DAMPING: lambda noise_params: create_probability_slider(
        "phase-damping",
        "Phase Damping",
        noise_params.get("phase-damping", 0)
    ),
    NoiseModelType.READOUT_ERROR: lambda noise_params: create_probability_slider(
        "readout-error",
        "Readout Error Probability",
        noise_params.get("readout-error", 0)
    ),
    NoiseModelType.BIT_FLIP: lambda noise_params: create_probability_slider("bit-flip", "Bit Flip Probability", noise_params.get("bit-flip", 0)),
    NoiseModelType.PHASE_FLIP: lambda noise_params: create_probability_slider("phase-flip", "Phase Flip Probability", noise_params.get("phase-flip", 0)),
    NoiseModelType.THERMAL_RELAXATION: lambda noise_params: create_switch(
        "thermal-relaxation",
        "Thermal Relaxation",
        noise_params.get("thermal-relaxation", False)
    )
}


def create_params_noise(app):
    profile_manager = app.server.profile_manager

    @app.callback(
        Output('select-noise-profile', 'data'),
        Output('select-noise-profile', 'value'),
        Input('btn-noise-profile-save', 'n_clicks'),
        State('noise-profile-name', 'value'),
        State('noise-params', 'data')
    )
    def save_noise_profile(_, profile_name, noise_params):
        if profile_name is None:
            return profile_manager.list_profiles(), None

        profile_manager.save_profile(profile_name, noise_params)

        return profile_manager.list_profiles(), profile_name

    @app.callback(
        Output('select-noise-profile', 'data', allow_duplicate=True),
        Output('select-noise-profile', 'value', allow_duplicate=True),
        Input('btn-noise-profile-delete', 'n_clicks'),
        State('select-noise-profile', 'value'),
        prevent_initial_call=True
    )
    def delete_noise_profile(_, selected_profile):
        if selected_profile is None:
            return profile_manager.list_profiles(), None

        profile_manager.delete_profile(selected_profile)

        return profile_manager.list_profiles(), None

    @app.callback(
        Output('noise-params', 'data'),
        Output('noise-profile-name', 'value'),
        Input('select-noise-profile', 'value'),
        prevent_initial_call=True
    )
    def update_noise_profiles(selected_profile):
        if selected_profile is None:
            return {}, None

        profile = profile_manager.load_profile(selected_profile)

        return profile, selected_profile

    @app.callback(
        Output('select-gate', 'data'),
        Input('select-simulator', 'value'),
        Input("input-qasm", "value"),
    )
    def update_select_gate_data(simulator_ref, qasm_str):
        # Check if the simulator exists in the SIMULATOR_REGISTRY
        simulator = SIMULATOR_REGISTRY.get(simulator_ref, None)

        if not simulator:
            # Return an empty array if simulator does not exist
            return []

        # Load the current circuit
        simulator.load_circuit(qasm_str)

        # Get the gates from the simulator
        supported_gates = simulator.supported_gates()
        used_gates = simulator.used_gates()

        # Return the gates as a list of dicts with "value" and "label" keys
        return [{"value": gate_ref, "label": supported_gates[gate_ref].display_name} for gate_ref in used_gates]

    @app.callback(
        Output('noise-gate-params', 'children'),
        Input('select-gate', 'value'),
        Input('select-simulator', 'value'),
        State("noise-params", 'data'),
    )
    def update_gate_noise_params_children(gate_ref, simulator_ref, current_noise_params):
        # Check if the simulator exists in the SIMULATOR_REGISTRY
        simulator = SIMULATOR_REGISTRY.get(simulator_ref, None)

        if not simulator or not gate_ref:
            # Return an empty array if simulator does not existF
            return []

        gates = simulator.supported_gates()
        gate_info = gates[gate_ref]

        gate_noise_params_components = [
            NOISE_PARAMS_COMPONENT_MAP[noise_model](current_noise_params.get(gate_ref, {}))
            for noise_model in gate_info.noise_models
        ]

        other_components = [
            dmc.Alert(id="noise-gate-description", color="blue", children=gate_info.description),
            dmc.NumberInput(
                id={"type": "noise-param", "index": "gate-time"},
                label="Gate time",
                description="Execution time in microseconds",
                value=current_noise_params.get("gate-time", 50),
                rightSection="µs"
            ),
            dmc.Grid(
                [
                    dmc.GridCol(
                        dmc.NumberInput(
                            id={"type": "noise-param", "index": "t1"},
                            label="Relaxation Time (T1)",
                            value=current_noise_params.get("t1", 30),
                            rightSection="µs"),
                        span=6
                    ),
                    dmc.GridCol(
                        dmc.NumberInput(
                            id={"type": "noise-param", "index": "t2"},
                            label="Dephasing Time (T2)",
                            value=current_noise_params.get("t2", 20),
                            rightSection="µs"
                        ),
                        span=6)
                ]
            )
        ]

        return other_components + gate_noise_params_components

    @app.callback(
        Output("noise-params", "data", allow_duplicate=True),
        Input('select-gate', 'value'),
        Input({"type": "noise-param", "index": ALL}, "value"),
        Input({"type": "noise-param", "index": ALL}, "checked"),
        State("noise-params", "data"),
        prevent_initial_call=True,
    )
    def update_dynamic_params(gate_ref, values, checked_values, current_noise_params):
        current_noise_params = current_noise_params or {}

        if not gate_ref:
            return current_noise_params

        noise_gate_params = {}

        for input_item, param_checked in zip(ctx.inputs_list[1], checked_values):
            param_id = input_item["id"]["index"]  # Get the name of the index
            param_value = input_item.get("value", None)  # Get the value of the input

            if param_value is None:
                param_value = param_checked

            noise_gate_params[param_id] = param_value

        current_noise_params[gate_ref] = noise_gate_params

        return current_noise_params

    return dmc.Stack([
        dcc.Store(id='noise-params'),
        dmc.Title("Noise profile", order=4),
        dmc.Grid(
            [
                dmc.GridCol(
                    dmc.Select(
                        label="Profile",
                        placeholder="Select a profile",
                        id="select-noise-profile",
                        data=[]
                    ),
                    span=8
                ),
                dmc.GridCol(
                    dmc.Button(
                        "Delete",
                        id="btn-noise-profile-delete",
                        color="red"
                    ),
                    span=4
                )
            ],
            align="flex-end",
        ),
        dmc.Grid(
            [
                dmc.GridCol(
                    dmc.TextInput(
                        id="noise-profile-name",
                        label="Profile name"
                    ),
                    span=8
                ),
                dmc.GridCol(
                    dmc.Button(
                        "Save",
                        id="btn-noise-profile-save"
                    ),
                    span=4
                )
            ],
            align="flex-end",
        ),
        dmc.Divider(),
        dmc.Title("Noise model editor", order=4),
        dmc.Select(
            label="Gate",
            placeholder="Select a gate",
            description="Select a gate to configure its noise parameters",
            id="select-gate",
            data=[]
        ),
        dmc.Stack(
            id="noise-gate-params",
            children=[],
            gap="xl"
        )
    ])
