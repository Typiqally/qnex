import numpy as np
from qiskit import QuantumCircuit
from qiskit.converters import dag_to_circuit, circuit_to_dag
from qiskit.quantum_info import Statevector


def serialize_statevector(statevector):
    # Convert to a regular array with real and imaginary parts
    real_parts = np.real(statevector.data).tolist()
    imag_parts = np.imag(statevector.data).tolist()

    return [(r, i) for r, i in zip(real_parts, imag_parts)]


def deserialize_statevector(state):
    complex_array = [complex(r, i) for r, i in state]
    return Statevector(complex_array)


def insert_save_statevectors(circuit: QuantumCircuit, prefix='sv') -> QuantumCircuit:
    dag = circuit_to_dag(circuit)
    dag_draft = dag.copy_empty_like()

    for index, layer in enumerate(dag.layers()):
        circuit = dag_to_circuit(layer["graph"])
        circuit.save_statevector(f"{prefix}_{index}", pershot=True)

        layer["graph"] = circuit_to_dag(circuit)

        dag_draft.compose(layer["graph"])

    return dag_to_circuit(dag_draft)
