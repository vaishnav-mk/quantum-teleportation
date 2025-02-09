import math
import random

def binary_search_error(alice_block, bob_block, offset):
    """
    Recursively locate the index of a single error in a block.
    Assumes that the parity of the block is mismatched (i.e. odd number of errors).
    Returns the absolute index (relative to the full key) of the detected error.
    """
    if len(alice_block) == 1:
        return offset  # base case: single bit block, error must be here
    mid = len(alice_block) // 2
    left_alice = alice_block[:mid]
    left_bob = bob_block[:mid]
    # Compute parities for left half
    if sum(left_alice) % 2 != sum(left_bob) % 2:
        # Error is in left half; search recursively
        return binary_search_error(left_alice, left_bob, offset)
    else:
        # Error is in right half; adjust offset accordingly
        return binary_search_error(alice_block[mid:], bob_block[mid:], offset + mid)

def cascade_reconciliation_full(alice_key, bob_key, qber_estimate, max_passes=4):
    """
    Implements a full-fledged Cascade error-reconciliation protocol.
    
    Parameters:
        alice_key (list[int]): The correct key bits as a list (0s and 1s).
        bob_key   (list[int]): The noisy key bits as a list.
        qber_estimate (float): An estimate of the quantum bit error rate (e.g., 0.03 for 3%).
        max_passes (int): Number of Cascade passes to run (typically 4 or more).
    
    Returns:
        list[int]: Bob's corrected key after Cascade reconciliation.
    
    The algorithm works as follows:
      1. For pass 1, the block size k1 is chosen as k1 = ceil(0.73 / qber_estimate).
      2. For pass i, the block size is set to block_size = k1 * 2^(i-1) (but no larger than the key length).
      3. For each pass, if i > 1, the key is randomly permuted (with the permutation later inverted).
      4. Each block is examined: if the parity of Alice’s block and Bob’s block differ, 
         a recursive binary search is performed to locate the error and Bob’s bit is flipped.
      5. After all passes, a confirmation phase runs several rounds of random subset parity checks.
         If any mismatch is found, an additional pass (with the last pass’s block size) is applied.
    """
    n = len(alice_key)
    # If no errors are expected, just return Bob's key
    if qber_estimate <= 0:
        return bob_key.copy()
    
    # Determine initial block size k1 (following literature recommendations)
    k1 = max(1, int(math.ceil(0.73 / qber_estimate)))
    corrected = bob_key.copy()
    
    # Run Cascade passes
    for pass_num in range(1, max_passes + 1):
        # Determine block size for this pass; block size doubles each pass (capped at n)
        block_size = k1 * (2 ** (pass_num - 1))
        block_size = min(block_size, n)
        
        # For passes after the first, perform a random permutation
        if pass_num > 1:
            indices = list(range(n))
            random.shuffle(indices)
            permuted_alice = [alice_key[i] for i in indices]
            permuted_bob = [corrected[i] for i in indices]
        else:
            indices = list(range(n))
            permuted_alice = alice_key[:]
            permuted_bob = corrected[:]
        
        # Process each block in the permuted key
        for start in range(0, n, block_size):
            end = min(start + block_size, n)
            block_a = permuted_alice[start:end]
            block_b = permuted_bob[start:end]
            if sum(block_a) % 2 != sum(block_b) % 2:
                # Parity mismatch: run binary search to locate a single error in this block
                error_index = binary_search_error(block_a, block_b, start)
                # Correct Bob's bit in the permuted key
                block_pos = error_index - start
                permuted_bob[block_pos] = 1 - permuted_bob[block_pos]
                # Note: In a full interactive protocol, the correction would cause cascade effects.
                # Here, corrections will propagate through later passes.
        
        # If we permuted, invert the permutation to update the corrected key
        if pass_num > 1:
            # Create an inverse permutation mapping: inv[i] gives the original position of permuted index i.
            inv_indices = [0] * n
            for i, idx in enumerate(indices):
                inv_indices[idx] = i
            new_corrected = [0] * n
            for i in range(n):
                new_corrected[i] = permuted_bob[inv_indices[i]]
            corrected = new_corrected
        else:
            corrected = permuted_bob
    
    return corrected

def cascade_full(alice_key, bob_key, qber_estimate, max_passes=4, confirm_rounds=20):
    """
    Runs the full Cascade protocol including the final confirmation phase.
    
    After running the main Cascade passes, the algorithm performs a series of random subset parity
    checks. If a mismatch is detected, it applies an additional reconciliation pass (with the block
    size used in the last pass) and resets the confirmation counter.
    
    Parameters:
        alice_key (list[int]): Alice’s correct key (list of bits).
        bob_key (list[int]): Bob’s initial (noisy) key (list of bits).
        qber_estimate (float): Estimated error rate.
        max_passes (int): Maximum number of Cascade passes.
        confirm_rounds (int): Number of consecutive successful random subset parity checks needed.
    
    Returns:
        list[int]: Bob's final corrected key.
    """
    corrected = cascade_reconciliation_full(alice_key, bob_key, qber_estimate, max_passes)
    
    # Confirmation phase: run several rounds of random subset parity checks.
    rounds = 0
    subset_size = max(1, int(0.05 * len(alice_key)))  # e.g., 5% of bits per check
    while rounds < confirm_rounds:
        subset = random.sample(range(len(alice_key)), subset_size)
        parity_alice = sum(alice_key[i] for i in subset) % 2
        parity_bob = sum(corrected[i] for i in subset) % 2
        if parity_alice != parity_bob:
            # Mismatch found; run an additional pass (using block size of last pass)
            block_size = min(len(alice_key), int(math.ceil(0.73 / qber_estimate)) * (2 ** (max_passes - 1)))
            # In this additional pass, use a permutation for safety
            indices = list(range(len(alice_key)))
            random.shuffle(indices)
            permuted_alice = [alice_key[i] for i in indices]
            permuted_bob = [corrected[i] for i in indices]
            # Process each block in the permuted key
            for start in range(0, len(alice_key), block_size):
                end = min(start + block_size, len(alice_key))
                block_a = permuted_alice[start:end]
                block_b = permuted_bob[start:end]
                if sum(block_a) % 2 != sum(block_b) % 2:
                    error_index = binary_search_error(block_a, block_b, start)
                    block_pos = error_index - start
                    permuted_bob[block_pos] = 1 - permuted_bob[block_pos]
            # Invert permutation
            inv_indices = [0] * len(alice_key)
            for i, idx in enumerate(indices):
                inv_indices[idx] = i
            new_corrected = [0] * len(alice_key)
            for i in range(len(alice_key)):
                new_corrected[i] = permuted_bob[inv_indices[i]]
            corrected = new_corrected
            rounds = 0  # reset counter after a correction pass
        else:
            rounds += 1
    return corrected