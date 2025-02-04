from qiskit.circuit import *
import time
from qiskit_aer import AerSimulator
from qiskit.compiler import transpile #type:ignore
from qiskit import QuantumCircuit

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

    simulator = AerSimulator()
    binary_str = ""
    start_time = time.time()

    for idx in range(num_circuits):
        if idx % 100 == 0:
            print(f"time taken for {idx}: {time.time() - start_time}")
        if idx % 1000 == 0:
            print(f"time taken for {idx}: {time.time() - start_time}")
        qc = QuantumCircuit(qubits_per_circuit, qubits_per_circuit)
        qc.h(range(qubits_per_circuit))
        qc.measure(range(qubits_per_circuit), range(qubits_per_circuit))

        
        tqc = transpile(qc, simulator)
        
        job = simulator.run(tqc, shots=1)
        result = job.result()
        counts = result.get_counts(qc)

        for key in counts:
            binary_str += "".join(str(int(bit)) for bit in key)

    print(f"Total time taken: {time.time() - start_time}")

    if len(binary_str) < num_bits:
        binary_str = binary_str.zfill(num_bits)
    return binary_str[:num_bits]