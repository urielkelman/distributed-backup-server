import socket
import json

def main():
    example = {
        "type": "backup",
        "path": "/files",
        "server_alias": "backup-server"
    }

    data = json.dumps(example)
    connection = socket.create_connection(("company_server_1", 12345))
    connection.sendall(bytes(data, encoding='utf-8'))
    continue_reading = True
    buffer = 0x1
    while continue_reading:
        b = connection.recv(2048).rstrip()
        if len(b) < 2048:
            continue_reading = False
        buffer += b[1:]
        print("Readed bytes: ", len(b[1:]))

    print("Total", len(buffer[1:]))
    connection.close()

if __name__ == "__main__":
    main()