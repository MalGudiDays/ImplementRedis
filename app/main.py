import argparse
import socket
import threading  # noqa: F401
import time

replicas: list[socket.socket] = []
class Context:
    def __init__(self, role=b"master", port=6379, replid=b"8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb", repl_offset=0):
        self.role = role
        self.mydict = {}
        self.port = port
        self.replid = replid
        self.repl_offset = repl_offset

    def redis_encode(self, data, encoding="utf-8"):
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

    def getResponse(self, data, connection=None):
        response = b"-1\r\n"
        if b"ECHO" in data:
            arr_size, *arr = data.split(b"\r\n")
            response = self.redis_encode([el.decode("utf-8") for el in arr[3::2]])
        elif b"PING" in data:
            response = b"+PONG\r\n"
        elif b"SET" in data:
            arr_size, *arr = data.split(b"\r\n")
            res = [el.decode("utf-8") for el in arr[3::2]]
            print(f"res: {res}")
            if len(res) > 3:
                threading.Timer(float(res[3]) / 1000.0, lambda: self.mydict.pop(res[0], None)).start()
            print(f"mydict: {self.mydict}")
            response = b"+OK\r\n"
            self.mydict[res[0]] = res[1]
            global replicas
            for r in replicas:
                r.sendall(data)  
        elif b"GET" in data:
            arr_size, *arr = data.split(b"\r\n")
            key = arr[-2].decode()
            print(f"arr: {arr}")
            print(f"key: {key}")
            print(f"mydict: {self.mydict}")
            try:
                response = self.redis_encode(self.mydict[key])
            except KeyError:
                response = b"$-1\r\n"
        elif b"INFO" in data:
            dt = [f"role:{self.role.decode()}", f"master_replid:{self.replid.decode()}", f"master_repl_offset:{self.repl_offset}"]
            response = self.redis_encode(dt[0]+dt[1]+dt[2])
            print(f"response: {response}")
        elif b"REPLCONF" in data:
            response = b"+OK\r\n"
        elif b"PSYNC" in data:
            s = f"+FULLRESYNC "
            s += f"{self.replid.decode()} {self.repl_offset}\r\n"
            response = s.encode()
            rdb_hex = "524544495330303131fa0972656469732d76657205372e322e30fa0a72656469732d62697473c040fa056374696d65c26d08bc65fa08757365642d6d656dc2b0c41000fa08616f662d62617365c000fff06e3bfec0ff5aa2"
            rdb_content = bytes.fromhex(rdb_hex)
            rdb_data = f"${len(rdb_content)}\r\n".encode()
            response += (rdb_data + rdb_content)
            replicas.append(connection)
        return response

    def handle_connection(self, connection, address):
        while True:
            data = connection.recv(1024)
            if not data:
                break
            print(data)
            response = self.getResponse(data, connection)
            if response:
                connection.send(response)

    def implement_redis_ping(self):
        with socket.create_server(("localhost", self.port), reuse_port=False) as server_socket:
            while True:
                connection, address = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_connection, args=(connection, address))
                client_thread.start()

    def perform_handshake(self, host, port):
        with socket.create_connection((host, port)) as connection:
            connection.sendall(b"*1\r\n$4\r\nPING\r\n")
            connection.recv(1024).decode()
            dt = [f"REPLCONF", f"listening-port", f"{self.port}"]
            connection.sendall(self.redis_encode(dt))
            connection.recv(1024).decode()
            dt = [f"REPLCONF", f"capa", f"psync2"]
            connection.sendall(self.redis_encode(dt))
            connection.recv(1024).decode()
            dt = [f"psync", f"?", f"-1"]
            connection.sendall(self.redis_encode(dt))
            

def main():
    parser = argparse.ArgumentParser(description="Redis-like server")
    parser.add_argument("--port", type=int, default=6379, help="Port number to listen on")
    parser.add_argument("--replicaof", type=str, help="Port number to listen on")
    args = parser.parse_args()
    print(f"args {args}")
    role = b"master"
    host = None
    port = None
    if args.replicaof:
        role = b"slave"
        host, port = args.replicaof.split()

    x = Context(role=role, port=args.port)
    if host and port:
        x.perform_handshake(host, port)
    x.implement_redis_ping() 



if __name__ == "__main__":
    main()
