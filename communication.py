import quantum_teleportation.quantum_data_teleporter as qc
import quantum_teleportation.bb84 as bb84

def main():
    """
    Demonstrates the usage of the QuantumDataTeleporter class and BB84 protocol.
    """
    protocol_choice = "2"  # input("Choose the protocol (1: Normal Teleporter, 2: BB84): ")
    text = "a"

    if protocol_choice == "1":
        # Normal Teleporter
        quantum_comm = qc.QuantumDataTeleporter(text_to_send=text, shots=1, noise_model=True)
        received_data, is_data_match = quantum_comm.run_simulation()
    elif protocol_choice == "2":
        # BB84 Protocol
        res = bb84.BB84Protocol(text, compression=False, noise_model=True, shots=1, output_path="output")
        received_data, is_data_match = res.run_protocol()
    else:
        print("Invalid choice. Exiting...")
        return

    print(f"Sent Data = {text}")
    print(f"Received Data = {received_data}")
    print(f"Sent Data == Received Data: {is_data_match}")

if __name__ == "__main__":
    main()