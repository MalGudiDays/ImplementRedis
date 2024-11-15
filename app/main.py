import socket
import threading  # noqa: F401
import time


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

def handle_connection(connection, address):
    mydict = {}
    while True:
        data = connection.recv(1024)
        if not data:
            break
        response = b"-1\r\n"
        print(data)
        if b"ECHO" in data:
            arr_size, *arr = data.split(b"\r\n")
            response = redis_encode([el.decode("utf-8") for el in arr[3::2]])
        elif b"PING" in data:
            response = b"+PONG\r\n"
        elif b"SET" in data:
            arr_size, *arr = data.split(b"\r\n")
            res = [el.decode("utf-8") for el in arr[3::2]]
            mydict[res[0]] = res[1]
            print(f"res: {res}")
            if len(res) > 3:
                threading.Timer(float(res[3]) / 1000.0, lambda: mydict.pop(res[0], None)).start()
            print(f"mydict: {mydict}")
            response = b"+OK\r\n"
        elif b"GET" in data:
            arr_size, *arr = data.split(b"\r\n")
            key = arr[-2].decode()
            print(f"arr: {arr}")
            print(f"key: {key}")
            print(f"mydict: {mydict}")
            if key in mydict:
                response = redis_encode(mydict[key.decode()])
        connection.send(response)

def implement_redis_ping():
    with socket.create_server(("localhost", 6379), reuse_port=False) as server_socket:
        while True:
            connection, address = server_socket.accept()
            client_thread = threading.Thread(target=handle_connection, args=(connection, address))
            client_thread.start()
            
def main():
    implement_redis_ping()



if __name__ == "__main__":
    main()
