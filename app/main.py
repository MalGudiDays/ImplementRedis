import socket  # noqa: F401


def main():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=False)
    connecton, _ = server_socket.accept()
    connecton.sendall(b"+OK\r\n")


if __name__ == "__main__":
    main()
