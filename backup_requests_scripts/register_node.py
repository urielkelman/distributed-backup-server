import socket
import json

def padd_to_specific_size(bytes_data, size):
    if len(bytes_data) > size:
        raise ValueError("Final size should be larger than data size to padd.")
    return bytes("0" * (size - len(bytes_data)) + bytes_data, encoding='utf-8')

def main():
    example = {
        "type": "register",
        "node": "company_server_1",
        "node_port": 12345,
        "path": "/asd",
        "frequency": 1
    }

    BYTES_AMOUNT_REQUEST_SIZE_INDICATION = 20

    data = json.dumps(example)
    connection = socket.create_connection(("backup_server", 12345))
    data_bytes = bytes(data, encoding='utf-8')
    padded_data_bytes_size = padd_to_specific_size(str(len(data_bytes)), BYTES_AMOUNT_REQUEST_SIZE_INDICATION)
    connection.sendall(padded_data_bytes_size)
    print("Going to send {} bytes".format(len(data_bytes)))
    connection.sendall(data_bytes)
    response = connection.recv(2048).rstrip()
    print(response)

if __name__ == "__main__":
    main()