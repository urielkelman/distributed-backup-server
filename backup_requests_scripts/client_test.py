import socket
import json

def main():
    example = {
        "type": "backup",
        "path": "/files",
        "server_alias": "backup-server"
    }

    data = json.dumps(example)
    bytes_data = bytes(data, encoding='utf-8')
    data_length = len(bytes_data)
    connection = socket.create_connection(("company_server_1", 12345))
    connection.sendall(bytes("0" * (1024 - len(str(data_length))) + str(data_length), encoding='utf-8'))
    connection.sendall(bytes_data)
    sirve_o_no = connection.recv(100).rstrip().decode('utf-8')
    print("s", sirve_o_no)
    if sirve_o_no == "No sirve":
        print(sirve_o_no)
    else:
        continue_reading = True
        buffer = bytes(0)
        while continue_reading:
            b = connection.recv(2048).rstrip()
            if len(b) < 2048:
                continue_reading = False
            buffer += b[1:]

        print("Total", len(buffer[1:]))
        with open("backup.tar.gz", "wb") as backup_file:
            backup_file.write(buffer)

    connection.close()

if __name__ == "__main__":
    main()