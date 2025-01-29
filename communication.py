import quantum_teleportation.quantum_data_teleporter as qc

def main():
    """
    Demonstrates the usage of the QuantumDataTeleporter class.
    """

    # Example usage with a string *and BB84*
    print("\n*** Example usage with a string + BB84 ***")
    text = "abc"  # Text to send
    quantum_comm = qc.QuantumDataTeleporter(
        text_to_send=text, 
        shots=1, 
        noise_model=True,
        use_bb84=True,           # <---- Turn on BB84
        num_bb84_qubits=64       # <---- Number of qubits in BB84
    )
    received_data, is_data_match = quantum_comm.run_simulation()

    print(f"Sent Data = {text}")
    print(f"Received Data = {received_data}")
    print(f"Sent Data == Received Data: {is_data_match}")

    # (Optionally keep your old file-based example, or remove it.)
    # ...
    

if __name__ == "__main__":
    main()