import socket
import json

def main():
    example = {
        "type": "register",
        "node": "company_server_1",
        "node_port": 12345,
        "path": "/asd"
    }

    data = json.dumps(example)
    connection = socket.create_connection(("backup_server", 12345))
    connection.sendall(bytes(data, encoding='utf-8'))
    response = connection.recv(2048).rstrip()
    print(response)

if __name__ == "__main__":
    main()