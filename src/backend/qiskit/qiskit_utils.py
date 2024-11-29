from qiskit import QuantumCircuit
from qiskit.converters import dag_to_circuit, circuit_to_dag
from qiskit.quantum_info import Statevector

from src.utils.complex_utils import serialize_complex_array, deserialize_complex_array


def serialize_statevector(statevector):
    return serialize_complex_array(statevector.data)


def deserialize_statevector(state):
    return Statevector(deserialize_complex_array(state))


def insert_save_statevectors(circuit: QuantumCircuit, prefix='sv') -> QuantumCircuit:
    dag = circuit_to_dag(circuit)
    dag_draft = dag.copy_empty_like()

    for index, layer in enumerate(dag.layers()):
        circuit = dag_to_circuit(layer["graph"])
        circuit.save_statevector(f"{prefix}_{index}", pershot=True)

        layer["graph"] = circuit_to_dag(circuit)

        dag_draft.compose(layer["graph"])

    return dag_to_circuit(dag_draft)