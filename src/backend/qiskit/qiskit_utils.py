from qiskit import QuantumCircuit
from qiskit.converters import dag_to_circuit, circuit_to_dag
from qiskit.quantum_info import Statevector

from src.utils.complex_utils import serialize_complex_array, deserialize_complex_array


def serialize_statevector(statevector):
    return serialize_complex_array(statevector.data)


def deserialize_statevector(state):
    return Statevector(deserialize_complex_array(state))


def insert_save_statevectors(circuit: QuantumCircuit, prefix='sv') -> QuantumCircuit:
    debug_circuit = circuit.copy_empty_like()
    debug_circuit.save_statevector(f"{prefix}_{0}", pershot=True)

    for index, instruction in enumerate(circuit.data):
        debug_circuit.append(instruction)
        debug_circuit.save_statevector(f"{prefix}_{index + 1}", pershot=True)

    return debug_circuit
