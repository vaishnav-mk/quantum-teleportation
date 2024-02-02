def text_from_file(file_path: str) -> str:
    """
    Reads text data from a file.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: Text content of the file.

    Raises:
        FileNotFoundError: If the file is not found.
    """
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None


def convert_text_to_binary(text: str) -> str:
    """
    Converts text to binary.

    Args:
        text (str): Input text.

    Returns:
        str: Binary representation of the input text.
    """
    binary_result = "".join(format(ord(char), "08b") for char in text)
    return binary_result


def convert_binary_to_text(binary_str: str) -> str:
    """
    Converts binary to text.

    Args:
        binary_str (str): Binary input.

    Returns:
        str: Text representation of the binary input.
    """
    binary_chunks = [binary_str[i : i + 8] for i in range(0, len(binary_str), 8)]
    text = "".join(chr(int(chunk, 2)) for chunk in binary_chunks)
    return text


def bit_flipper(bits: str) -> str:
    """
    Flips bits in the input.

    Args:
        bits (str): Input bit string.

    Returns:
        str: Flipped bit string.
    """
    return "".join(["1" if x == "0" else "0" for x in bits])
