def padd_to_specific_size(bytes_data, size):
    if len(bytes_data) > size:
        raise ValueError("Final size should be larger than data size to padd.")
    return bytes("0" * (size - len(bytes_data)) + bytes_data, encoding='utf-8')
