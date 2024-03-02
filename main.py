import quantum_teleportation.quantum_data_teleporter as qc


def main():
    # file_path = "data/text.txt"  # Path to the text file
    # quantum_comm = qc.QuantumDataTeleporter(file_path=file_path, shots=2, noise_model=True)
    # received_data, is_data_match = quantum_comm.run_simulation()

    # print(f"Sent Data == Received Data: {is_data_match}")

    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus vel pharetra orci. Phasellus vestibulum sagittis justo, sed rutrum nunc commodo nec. Vivamus molestie posuere ipsum et laoreet. Morbi quis ligula ac lectus tempor imperdiet porttitor et justo. Nam eget massa ac enim placerat rhoncus id a lacus. Proin dolor ligula, porta sed neque sed, efficitur pretium leo. Pellentesque a feugiat ipsum. Donec tellus libero, pellentesque eu volutpat laoreet, fermentum nec nisl. Praesent porta purus vitae posuere molestie. Proin iaculis dictum ultricies. Interdum et malesuada fames ac ante ipsum primis in faucibus. Suspendisse fringilla sed turpis eleifend porta. Fusce sed tortor nisi. Maecenas tincidunt eros in dolor ultrices, at aliquet nisi volutpat. Sed vestibulum vitae tellus nec maximus. Etiam pharetra iaculis interdum. Interdum et malesuada fames ac ante ipsum primis in faucibus."
    quantum_comm = qc.QuantumDataTeleporter(
        text_to_send=text,
        shots=-1,
        noise_model=True,
        logs=True,
        compression="adaptive",  # compression can be "brotli" or "adaptive" or False
    )
    received_data, is_data_match = quantum_comm.run_simulation()

    print(f"Sent Data = {text}")
    print(f"Received Data = {received_data}")

    print(f"Sent Data == Received Data: {is_data_match}")


if __name__ == "__main__":
    main()
