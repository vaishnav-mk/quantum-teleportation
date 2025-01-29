# bb84_utils.py

import random
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute, BasicAer
from typing import Tuple

def run_bb84_protocol(num_qubits: int = 16) -> Tuple[str, str]:
    """
    Run a simplified local BB84 protocol simulation (Alice & Bob together in code).
    Returns: (alice_key, bob_key) after sifting (matching bases).
    """
    # STEP 1: Alice randomly chooses bits & bases
    alice_bits  = [random.randint(0, 1) for _ in range(num_qubits)]
    # 0 = computational (Z), 1 = hadamard (X)
    alice_bases = [random.randint(0, 1) for _ in range(num_qubits)]

    # Create circuit
    q = QuantumRegister(num_qubits, name="q")
    c = ClassicalRegister(num_qubits, name="c")
    bb84_circ = QuantumCircuit(q, c)

    # Encode each qubit
    for i in range(num_qubits):
        if alice_bits[i] == 1:
            bb84_circ.x(q[i])
        if alice_bases[i] == 1:
            bb84_circ.h(q[i])

    # STEP 2: Bob randomly chooses bases
    bob_bases = [random.randint(0, 1) for _ in range(num_qubits)]

    # Bob measures in those random bases
    for i in range(num_qubits):
        if bob_bases[i] == 1:
            bb84_circ.h(q[i])  # measure in X-basis
        bb84_circ.measure(q[i], c[i])

    # Execute once; measure each qubit exactly once
    backend = BasicAer.get_backend("qasm_simulator")
    result = execute(bb84_circ, backend=backend, shots=1).result()
    measured_key = list(result.get_counts().keys())[0]  # e.g. '010110'
    measured_key = measured_key[::-1]  # Qiskit bit order is reversed

    # STEP 3: Sift the key by matching bases
    alice_sifted = []
    bob_sifted = []
    for i in range(num_qubits):
        if alice_bases[i] == bob_bases[i]:
            # same basis → keep the bit
            alice_sifted.append(str(alice_bits[i]))  
            bob_sifted.append(str(measured_key[i]))

    # Convert to string
    alice_key = "".join(alice_sifted)
    bob_key   = "".join(bob_sifted)

    return alice_key, bob_key