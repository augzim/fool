import os
import socket


class Server:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def __enter__(self):
        # open a port on linux os
        os.system(f'ufw enable && ufw allow {self.port}')
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        # close a port after a server was shut down
        os.system(f'echo "$PASSWORD" | sudo -S ufw delete allow {self.port} && ufw disable')
