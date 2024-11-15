import socket
import threading  # noqa: F401

def handle_connection(connection):
    while connection.recv(1024):
        response = b"+PONG\r\n"
        connection.send(response)

def implement_redis_ping(server_socket):
    with socket.create_server(("localhost", 6379), reuse_port=False) as server_socket:
        while True:
            connection, _ = server_socket.accept()
            client_thread = threading.Thread(target=handle_connection, args=(connection,))
            client_thread.start()

def main():
    implement_redis_ping()



if __name__ == "__main__":
    main()
