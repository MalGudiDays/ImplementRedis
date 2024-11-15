import socket
import threading  # noqa: F401

def handle_connection(connection):
    while connection.recv(1024):
        response = b"+PONG\r\n"
        connection.send(response)

def implement_redis_ping():
    with socket.create_server(("localhost", 6379), reuse_port=False) as server_socket:
        while True:
            connection, _ = server_socket.accept()
            client_thread = threading.Thread(target=handle_connection, args=(connection,))
            client_thread.start()

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
    print(f"encoded: {encoded}")
    return (separator.join(encoded) + separator).encode(encoding=encoding)

def handle_connection(conn, addr):
    print("Connection from", addr)
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
    #implement_redis_ping()
    handle_connection()



if __name__ == "__main__":
    main()
