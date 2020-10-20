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
    response = connection.recv(2048).rstrip()
    connection.close()
    print(response)

if __name__ == "__main__":
    main()