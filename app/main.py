import socket
import threading  # noqa: F401

def handle_connection(connection):
    while True:
        with connection.recv(4096) as data:
            if not data:
                break
            print(data)
            response = redis_encode([el.decode("utf-8") for el in data[3::2]])
            connection.send(response)

def implement_redis_ping():
    with socket.create_server(("localhost", 6379), reuse_port=False) as server_socket:
        while True:
            connection, _ = server_socket.accept()
            #client_thread = threading.Thread(target=handle_connection, args=(connection,))
            #client_thread.start()
            handle_connection(connection)

def redis_encode(data, encoding="utf-8"):
    if not isinstance(data, list):
        data = [data]
    separator = "\r\n"
    size = len(data)
    encoded = []
    for datum in data:
        encoded.append(f"${len(datum)}")
        encoded.append(datum)
    if size > 1:
        encoded.insert(0, f"*{size}")
    return (separator.join(encoded) + separator).encode(encoding=encoding)

def main():
    implement_redis_ping()



if __name__ == "__main__":
    main()
