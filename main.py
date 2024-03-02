import quantum_teleportation.quantum_data_teleporter as qc


def main():
    # file_path = "data/text.txt"  # Path to the text file
    # quantum_comm = qc.QuantumDataTeleporter(file_path=file_path, shots=2, noise_model=True)
    # received_data, is_data_match = quantum_comm.run_simulation()

    # print(f"Sent Data == Received Data: {is_data_match}")

    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec diam nunc, condimentum vel lectus sit amet, bibendum vehicula magna. Nullam volutpat, odio sed euismod pretium, est ipsum dapibus augue, euismod fringilla augue nisi feugiat augue. Vestibulum magna urna, dignissim a dapibus ut, bibendum et orci. Aenean a urna vitae turpis pretium molestie ut in dolor. Nam ut erat quis odio interdum varius. Vivamus at ipsum quis libero volutpat volutpat. Mauris in tellus maximus, viverra leo quis, laoreet tellus. Mauris imperdiet bibendum leo a sagittis. Phasellus et tortor quis felis maximus finibus vel eget turpis. Nullam ac ex quis sem iaculis tempor. Suspendisse ac metus eu risus facilisis lacinia. Aliquam pellentesque libero lorem, sit amet condimentum sapien fermentum eget. Morbi dignissim, libero ut tempor placerat, ligula massa blandit diam, id molestie ligula ex non elit. Cras vitae dolor id dui porta efficitur ac ut leo. Aliquam finibus justo in rhoncus mollis. Nullam quis efficitur tortor. Etiam non porta ex. Aliquam metus sapien, luctus at odio vel, rutrum pharetra augue. Phasellus non dapibus tellus. Integer non massa luctus, eleifend ante sed, tempus arcu. Nunc consectetur ut arcu a bibendum."
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
