from qiskit import QuantumCircuit


def insert_save_statevectors(circuit: QuantumCircuit, prefix='sv') -> QuantumCircuit:
    debug_circuit = circuit.copy_empty_like()
    debug_circuit.save_statevector(f"{prefix}_{0}", pershot=True)

    for index, instruction in enumerate(circuit.data):
        debug_circuit.append(instruction)
        debug_circuit.save_statevector(f"{prefix}_{index + 1}", pershot=True)

    return debug_circuit
