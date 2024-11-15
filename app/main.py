import socket
import threading  # noqa: F401

def handle_connection(connection, address):
    while True:
        data = connection.recv(1024).decode("utf-8")
        if not data:
            break
        response = b"+PONG\r\n"
        if "echo" in data:
            response = data.split("\r\n")[-2]
            ln = len(response)
            response = f"${ln}\r\n{response}\r\n"
        connection.send(response.encode("utf-8"))

def implement_redis_ping(server_socket):
    with socket.create_server(("localhost", 6379), reuse_port=False) as server_socket:
        while True:
            connection, address = server_socket.accept()
            client_thread = threading.Thread(target=handle_connection, args=(connection, address))
            client_thread.start()

def main():
    implement_redis_ping()



if __name__ == "__main__":
    main()
