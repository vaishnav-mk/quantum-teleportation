from qiskit.circuit import *
import time
from qiskit_aer import AerSimulator
from qiskit.compiler import transpile
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

        # Transpile the circuit for the chosen simulator
        tqc = transpile(qc, simulator)
        # Run the circuit using the backend's run method
        job = simulator.run(tqc, shots=1)
        result = job.result()
        counts = result.get_counts(qc)
        # Append the bitstring (the ordering may need to be adjusted depending on your preference)
        for key in counts:
            binary_str += "".join(str(int(bit)) for bit in key)

    print(f"Total time taken: {time.time() - start_time}")
    # Ensure the binary string has at least num_bits characters
    if len(binary_str) < num_bits:
        binary_str = binary_str.zfill(num_bits)
    return binary_str[:num_bits]