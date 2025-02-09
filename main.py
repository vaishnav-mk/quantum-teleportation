import quantum_teleportation.quantum_data_teleporter as qc

def main():
    text = "NextTechLab is Goated"
    quantum_comm = qc.QuantumDataTeleporter(
        text_to_send=text,
        shots=10,
        noise_model=True,  # Set to True to enable noise (and eavesdropper simulation).
        logs=True,
        compression="adaptive",  # Options: "adaptive", "brotli", or False.
        protocol="bb84",         # Options: "bb84", "b92", "e91".
        output_path="output",
    )
    final_alice_key, final_bob_key = quantum_comm.run_simulation()

    print(f"Final Alice Key: {final_alice_key}")
    print(f"Final Bob Key: {final_bob_key}")
    print(f"Keys match: {final_alice_key == final_bob_key}")

if __name__ == "__main__":
    main()