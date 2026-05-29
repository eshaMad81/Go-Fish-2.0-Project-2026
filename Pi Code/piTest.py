import socket

host = "0.0.0.0"
port = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen(1)

print("Waiting for connection...")

conn, addr = server.accept()

print("Connected by:", addr)

message = conn.recv(1024).decode()
print("Received:", message)

conn.send("Hello from Pi!".encode())

conn.close()
server.close()
