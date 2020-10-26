import json
import socket

BYTES_AMOUNT_REQUEST_SIZE_INDICATION = 20


def padd_to_specific_size(bytes_data, size):
    if len(bytes_data) > size:
        raise ValueError("Final size should be larger than data size to padd.")
    return bytes("0" * (size - len(bytes_data)) + bytes_data, encoding='utf-8')


def main():
    query = bytes(json.dumps({
        "type": "query"
    }), encoding='utf-8')

    connection = socket.create_connection(("backup_server", 12347))
    padded_data_bytes_size = padd_to_specific_size(str(len(query)), BYTES_AMOUNT_REQUEST_SIZE_INDICATION)
    connection.sendall(padded_data_bytes_size)
    connection.sendall(query)

    response_size = int(connection.recv(BYTES_AMOUNT_REQUEST_SIZE_INDICATION).decode('utf-8'))
    print("Going to receive response of {} bytes".format(response_size))
    readed = ""
    while len(readed) < response_size:
        readed += connection.recv(response_size).decode('utf-8')

    query_result = json.loads(readed)
    print("Result: ")
    print(query_result)


if __name__ == "__main__":
    main()
