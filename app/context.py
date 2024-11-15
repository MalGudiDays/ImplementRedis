import threading
import socket


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

    def getResponse(self, data, mydict = {}):
        response = b"-1\r\n"
        if b"ECHO" in data:
            arr_size, *arr = data.split(b"\r\n")
            response = self.redis_encode([el.decode("utf-8") for el in arr[3::2]])
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
            try:
                response = self.redis_encode(mydict[key])
            except KeyError:
                response = b"$-1\r\n"
        elif b"INFO" in data:
            dt = [f"role:{self.role.decode()}", f"master_replid:{self.replid.decode()}", f"master_repl_offset:{self.repl_offset}"]
            response = self.redis_encode(dt[0]+dt[1]+dt[2])
            print(f"response: {response}")
        return response

    def handle_connection(self, connection, address):
        mydict = {}
        while True:
            data = connection.recv(1024)
            if not data:
                break
            print(data)
            response = self.getResponse(data, mydict)

            connection.send(response)

    def implement_redis_ping(self):
        with socket.create_server(("localhost", self.port), reuse_port=False) as server_socket:
            while True:
                connection, address = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_connection, args=(connection, address))
                client_thread.start()
            