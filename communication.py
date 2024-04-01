import quantum_teleportation.quantum_data_teleporter as qc
import quantum_teleportation.bb84 as bb84

def main():
    """
    Demonstrates the usage of the QuantumDataTeleporter class and BB84 protocol.
    """

    protocol_choice = input("Choose the protocol (1: Normal Teleporter, 2: BB84): ")

    text = 'Elevate your tech journey at SRM Next Tech Lab — where innovation meets collaboration. Dive into specialized domains, experiment freely, and fuel your curiosity in a vibrant, visually pleasing space. Join us now!'

    if protocol_choice == "1":
        # Normal Teleporter
        quantum_comm = qc.QuantumDataTeleporter(text_to_send=text, shots=1, noise_model=True)
        received_data, is_data_match = quantum_comm.run_simulation()

    elif protocol_choice == "2":
        # BB84 Protocol
        encoded_data, key_bits, base_bits = bb84.bb84_protocol(text)
        received_data = bb84.decode_bb84(encoded_data, key_bits, base_bits)
        is_data_match = received_data == text

    else:
        print("Invalid choice. Exiting...")
        return

    print(f"Sent Data = {text}")
    print(f"Received Data = {received_data}")
    print(f"Sent Data == Received Data: {is_data_match}")

if __name__ == "__main__":
    main()