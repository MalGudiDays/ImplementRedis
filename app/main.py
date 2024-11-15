import argparse
import socket
import threading  # noqa: F401
import time
import context as ctx
            
def main():
    parser = argparse.ArgumentParser(description="Redis-like server")
    parser.add_argument("--port", type=int, default=6379, help="Port number to listen on")
    parser.add_argument("--replicaof", type=str, help="Port number to listen on")
    args = parser.parse_args()
    print(f"args {args}")
    role = b"master"
    if args.replicaof:
        role = b"slave"
    x = ctx.Context(role=role, port=args.port)
    x.implement_redis_ping()



if __name__ == "__main__":
    main()
