import dash_mantine_components as dmc
from dash import dcc

default_qasm_circuit = """OPENQASM 3.0;
include "stdgates.inc";
bit[2] meas;
qubit[2] q;
h q[0];
cx q[0], q[1];
barrier q[0], q[1];
meas[0] = measure q[0];
meas[1] = measure q[1];
"""

def create_qasm_input(app):
    return dmc.Stack([
        dcc.Store(id='qasm'),
        dmc.Title("OpenQASM", order=4),
        dmc.Textarea(
            id='input-qasm',
            label="Enter valid script",
            autosize=True,
            minRows=20,
            value=default_qasm_circuit
        )
    ])
