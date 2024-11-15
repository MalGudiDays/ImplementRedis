import socket
import threading  # noqa: F401


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

def handle_connection(conn, addr):
    while True:
        data = conn.recv(32)
        if not data:
            break
        arr_size, *arr = data.split(b"\r\n")
        if arr[1] == b"ping":
            resp = redis_encode("PONG")
            conn.sendall(resp)
        elif arr[1] == b"echo":
            resp = redis_encode([el.decode("utf-8") for el in arr[3::2]])
            conn.sendall(resp)
        else:
            break
    conn.close()

def main():
    with socket.create_server(("localhost", 6379), reuse_port=False) as server_socket:
        while True:
            connection, address = server_socket.accept()
            handle_connection(connection, address)



if __name__ == "__main__":
    main()
