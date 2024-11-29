from src.backend.base_simulator import BaseSimulator
from src.backend.qiskit.qiskit_simulator import QiskitSimulator

SIMULATOR_REGISTRY: dict[str, BaseSimulator] = {
    "qiskit": QiskitSimulator(),
    # "Cirq": CirqSimulator(),
    # "PennyLane": PennyLaneSimulator(),
    # "Custom": CustomSimulator()
}