from qiskit import QuantumCircuit, Aer, execute
from qiskit_aer import AerSimulator
import numpy as np
import time

def qrng(num_bits: int) -> str:
    """
    Generates random bits using a quantum circuit.

    Args:
        num_bits (int): Number of random bits to generate.

    Returns:
        str: Random bits string.
    """

    qubits_per_circuit = 28

    num_circuits = (num_bits + qubits_per_circuit - 1) // qubits_per_circuit
    # print(f"Number of circuits: {num_circuits}")

    simulator = AerSimulator()
    binary_str = ""

    start_time = time.time()
    for _ in range(num_circuits):
        if _ % 100 == 0:
            print(f"time taken for {_}: {time.time() - start_time}")
        if _ % 1000 == 0:
            print(f"time taken for {_}: {time.time() - start_time}")
        qc = QuantumCircuit(qubits_per_circuit, qubits_per_circuit)
        qc.h(range(qubits_per_circuit))
        qc.measure(range(qubits_per_circuit), range(qubits_per_circuit))

        # print(qc)

        result = execute(qc, simulator, shots=1).result()
        counts = result.get_counts(qc)

        binary_str += "".join([str(int(key)) for key in counts.keys()])

    print(f"Time taken for qRNG: {time.time() - start_time}")
    if len(binary_str) < num_bits:
        binary_str = binary_str.zfill(num_bits)

    return binary_str[:num_bits]
