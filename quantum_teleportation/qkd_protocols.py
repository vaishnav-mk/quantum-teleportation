# File: quantum_teleportation/qkd_protocols.py

import hashlib
import logging
import random

logger = logging.getLogger("qkd_protocols")

class BB84Protocol:
    def __init__(
        self,
        alice_key: list[int],
        bob_key: list[int],
        alice_bases: list[str],
        bob_bases: list[str],
        eavesdrop: bool = False,
        eavesdrop_intensity: float = 0.1,  # Fraction of bits attacked by Eve.
        logs: bool = True,
    ):
        """
        Initialize the BB84 post-processing protocol.

        Args:
            alice_key (list[int]): Raw key bits from Alice.
            bob_key (list[int]): Raw key bits from Bob.
            alice_bases (list[str]): Alice’s chosen bases.
            bob_bases (list[str]): Bob’s chosen bases.
            eavesdrop (bool): Whether to simulate an eavesdropper.
            eavesdrop_intensity (float): Fraction of bits Eve interferes with.
            logs (bool): Whether to log detailed actions.
        """
        self.alice_key = alice_key
        self.bob_key = bob_key
        self.alice_bases = alice_bases
        self.bob_bases = bob_bases
        self.eavesdrop = eavesdrop
        self.eavesdrop_intensity = eavesdrop_intensity
        self.logs = logs

    def simulate_classical_communication(self):
        """
        Simulate the classical communication in BB84 where Alice and Bob publicly share their bases.
        Only bits where their bases match are kept.
        """
        if self.logs:
            logger.info("Simulating classical communication: Exchanging bases...")
        
        sifted_alice = []
        sifted_bob = []
        for i, (a_basis, b_basis) in enumerate(zip(self.alice_bases, self.bob_bases)):
            if a_basis == b_basis:
                sifted_alice.append(self.alice_key[i])
                sifted_bob.append(self.bob_key[i])
            else:
                if self.logs:
                    logger.debug(f"Discarding bit index {i} due to mismatched bases: {a_basis} vs {b_basis}")
        if self.logs:
            logger.info(f"Sifted key length: {len(sifted_alice)}")
        self.alice_key = sifted_alice
        self.bob_key = sifted_bob

    def simulate_eavesdropper(self):
        """
        Simulate an intercept-resend attack. With a probability defined by eavesdrop_intensity,
        flip bits in Bob's key.
        """
        if not self.eavesdrop:
            return

        if self.logs:
            logger.info("Simulating Eve's intercept-resend attack...")
        attacked_bob_key = []
        for bit in self.bob_key:
            if random.random() < self.eavesdrop_intensity:
                attacked_bit = 1 - bit
                attacked_bob_key.append(attacked_bit)
                if self.logs:
                    logger.debug(f"Eve attacked bit: {bit} -> {attacked_bit}")
            else:
                attacked_bob_key.append(bit)
        self.bob_key = attacked_bob_key

    def error_reconciliation(self):
        """
        Perform a simple error reconciliation using parity checks.
        The key is divided into blocks, and blocks with mismatching parity are discarded.
        """
        if self.logs:
            logger.info("Performing error reconciliation using simple parity checks...")
        block_size = 8  # Example block size.
        reconciled_alice = []
        reconciled_bob = []
        num_blocks = len(self.alice_key) // block_size

        for i in range(num_blocks):
            block_a = self.alice_key[i * block_size : (i + 1) * block_size]
            block_b = self.bob_key[i * block_size : (i + 1) * block_size]
            parity_a = sum(block_a) % 2
            parity_b = sum(block_b) % 2
            if parity_a == parity_b:
                reconciled_alice.extend(block_a)
                reconciled_bob.extend(block_b)
            else:
                if self.logs:
                    logger.debug(f"Discarding block {i} due to parity mismatch.")
        self.alice_key = reconciled_alice
        self.bob_key = reconciled_bob
        if self.logs:
            logger.info(f"Key length after error reconciliation: {len(self.alice_key)}")

    def privacy_amplification(self):
        """
        Apply privacy amplification via a simple hashing method.
        The final key length is shortened based on the estimated error (mismatch) rate.
        """
        if self.logs:
            logger.info("Performing privacy amplification...")
        mismatches = sum(1 for a, b in zip(self.alice_key, self.bob_key) if a != b)
        total = len(self.alice_key)
        error_rate = mismatches / total if total > 0 else 0
        if self.logs:
            logger.info(f"Estimated error rate: {error_rate * 100:.2f}%")
        final_key_length = int(total * (1 - error_rate))
        if final_key_length <= 0:
            if self.logs:
                logger.error("Error rate too high. No secure key can be distilled.")
            return "", ""

        # Convert the keys to strings.
        alice_key_str = "".join(str(bit) for bit in self.alice_key)
        bob_key_str = "".join(str(bit) for bit in self.bob_key)

        # Hash the keys using SHA-256 and convert the hash to a binary string.
        alice_hash = hashlib.sha256(alice_key_str.encode()).hexdigest()
        bob_hash = hashlib.sha256(bob_key_str.encode()).hexdigest()
        alice_hash_bin = bin(int(alice_hash, 16))[2:].zfill(256)
        bob_hash_bin = bin(int(bob_hash, 16))[2:].zfill(256)

        final_alice_key = alice_hash_bin[:final_key_length]
        final_bob_key = bob_hash_bin[:final_key_length]

        if self.logs:
            logger.info(f"Final key length after privacy amplification: {len(final_alice_key)}")
        return final_alice_key, final_bob_key

    def process(self):
        """
        Execute the full post-processing: classical communication, eavesdropper simulation,
        error reconciliation, and privacy amplification.
        
        Returns:
            tuple: (final_alice_key, final_bob_key)
        """
        self.simulate_classical_communication()
        self.simulate_eavesdropper()
        self.error_reconciliation()
        final_alice, final_bob = self.privacy_amplification()
        return final_alice, final_bob