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


def convert_text_to_binary_with_filter(text: str) -> tuple[str, str]:
    """
    Converts text to binary, excluding characters that are out of ASCII bounds.

    Args:
        text (str): Input text.

    Returns:
        Tuple[str, str]: Binary representation of the filtered text and the new filtered text.
    """
    filtered_text = []
    binary_result = []

    for char in text:
        if ord(char) < 256:  # ASCII values that fit in 8 bits
            binary_char = format(ord(char), "08b")
            binary_result.append(binary_char)
            filtered_text.append(char)
        else:
            print(f"Character {char} is out of ASCII bounds and will be excluded.")

    binary_result_str = "".join(binary_result)
    filtered_text_str = "".join(filtered_text)

    print(f"Filtered Text: {filtered_text_str}, Binary: {binary_result_str}")
    return binary_result_str, filtered_text_str


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
