from qnex.backend.base_simulator import BaseSimulator
from qnex.backend.qiskit.qiskit_simulator import QiskitSimulator

SIMULATOR_REGISTRY: dict[str, BaseSimulator] = {
    "qiskit": QiskitSimulator(),
    # "Cirq": CirqSimulator(),
    # "PennyLane": PennyLaneSimulator(),
    # "Custom": CustomSimulator()
}