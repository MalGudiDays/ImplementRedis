import socket  # noqa: F401


def main():
    with socket.create_server(("localhost", 6379), reuse_port=False) as server_socket:
        while True:
            connecton, _ = server_socket.accept()
            while connecton.recv(1024):
                response = b"+PONG\r\n"
                connecton.send(response)


if __name__ == "__main__":
    main()
