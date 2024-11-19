import dash_mantine_components as dmc
from dash import dcc, Output, Input


def create_slider(id: str, label: str):
    return dmc.Grid(
        [
            dmc.GridCol(dmc.Text(label, size="sm"), span=4),
            dmc.GridCol(
                dmc.Slider(
                    id=id,
                    value=50,
                    marks=[
                        {"value": 0, "label": "0%"},
                        {"value": 25, "label": "25%"},
                        {"value": 50, "label": "50%"},
                        {"value": 75, "label": "75%"},
                        {"value": 100, "label": "100%"},
                    ],
                    w="100%"
                ),
                span="auto"
            )
        ]
    )


def create_params_noise(app):
    @app.callback(
        Output('noise-params', 'data'),
        Input('noise-dp', 'value'),
        Input('noise-a', 'value'),
        Input('noise-p', 'value'),
        Input('noise-bf', 'value'),
        Input('noise-pf', 'value'),
        Input('noise-r', 'value'),
    )
    def update_store(noise_dp, noise_a, noise_p, noise_bf, noise_pf, noise_r):
        return {
            'noise_depolarizing': noise_dp,
            'noise_amplitude_damping': noise_a,
            'noise_phase_damping': noise_p,
            'noise_bit_flip': noise_bf,
            'noise_phase_flip': noise_pf,
            'noise_readout_error': noise_r,
        }

    return dmc.Stack([
        dcc.Store(id='noise-params'),
        dmc.Title("Noise", order=4),
        dmc.Select(
            label="Profile",
            placeholder="Select a profile",
            id="profile-select",
            data=[
                {"value": "ibmq_lima", "label": "ibmq_lima"},
                {"value": "ibmq_ourense", "label": "ibmq_ourense"},
                {"value": "ibmq_belem", "label": "ibmq_belem"},
                {"value": "ibmq_manila", "label": "ibmq_manila"},
                {"value": "ibmq_quito", "label": "ibmq_quito"},
                {"value": "ibmq_jakarta", "label": "ibmq_jakarta"},
            ]
        ),
        dmc.Divider(),
        dmc.Title("General noise", order=4),
        dmc.Stack(
            [
                create_slider("noise-r", "Readout Error Probability"),
            ],
            gap="xl"
        ),
        dmc.Divider(),
        dmc.Title("Gate noise", order=4),
        dmc.Select(
            label="Gate",
            placeholder="Select a gate",
            id="gate-select",
            data=[
                {"value": "x", "label": "X (Pauli-X)"},
                {"value": "y", "label": "Y (Pauli-Y)"},
                {"value": "z", "label": "Z (Pauli-Z)"},
                {"value": "h", "label": "H (Hadamard)"},
                {"value": "s", "label": "S (Phase)"},
                {"value": "t", "label": "T (π/8)"},
                {"value": "cx", "label": "CX (CNOT)"},
                {"value": "cy", "label": "CY (Controlled-Y)"},
                {"value": "cz", "label": "CZ (Controlled-Z)"},
                {"value": "swap", "label": "SWAP"},
                {"value": "ccx", "label": "CCX (Toffoli)"},
                {"value": "u3", "label": "U3 (Universal 3-parameter rotation)"},
                {"value": "u2", "label": "U2 (2-parameter rotation)"},
                {"value": "rz", "label": "RZ (Rotation around Z-axis)"},
                {"value": "rx", "label": "RX (Rotation around X-axis)"},
                {"value": "ry", "label": "RY (Rotation around Y-axis)"},
                {"value": "m", "label": "M (Measurement)"}
            ]
        ),
        dmc.Stack(
            [
                create_slider("noise-dp", "Depolarizing Probability"),
                create_slider("noise-a", "Amplitude Damping Probability"),
                create_slider("noise-p", "Phase Damping Probability"),
                create_slider("noise-bf", "Bit Flip Probability"),
                create_slider("noise-pf", "Phase Flip Probability"),
            ],
            gap="xl"
        )
    ])
