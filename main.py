import quantum_teleportation.quantum_data_teleporter as qc


def main():
    # file_path = "data/text.txt"  # Path to the text file
    # quantum_comm = qc.QuantumDataTeleporter(file_path=file_path, shots=2, noise_model=True)
    # received_data, is_data_match = quantum_comm.run_simulation()

    # print(f"Sent Data == Received Data: {is_data_match}")

    text = "abc"
    quantum_comm = qc.QuantumDataTeleporter(
        file_path="data/text.txt", noise_model=False, logs=True, shots=1
    )
    received_data, is_data_match = quantum_comm.run_simulation()

    print(f"Sent Data = {text}")
    print(f"Received Data = {received_data}")

    print(f"Sent Data == Received Data: {is_data_match}")


if __name__ == "__main__":
    main()
