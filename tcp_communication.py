import asyncio
import websockets
import os

# Set up functions for communicating with Game
import socket
import sys

GAME_HOST = input("Game Host IP: ")
print("game host ip is {}".format(GAME_HOST))
GAME_PORT = 5566
game_socket = None


def establish_socket():
    global game_socket;
    for res in socket.getaddrinfo(GAME_HOST, GAME_PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            game_socket = socket.socket(af, socktype, proto)
        except OSError as msg:
            game_socket = None
            continue
        try:
            game_socket.connect(sa)
        except OSError as msg:
            game_socket.close()
            game_socket = None
            continue
        break
    if game_socket is None:
        print('could not open socket to game')
        return False
    else:
        return True


def send_to_game(command):
    global game_socket
    try:
        game_socket.sendall(command.encode())
    except (BrokenPipeError, AttributeError) as e:
        if establish_socket():
            send_command = command
            game_socket.sendall(send_command.encode())
            print("sending: " + send_command)

loop = asyncio.get_event_loop()

print("Setting up remote server for receiving message from game")
MY_REMOTE_IP = os.popen('configure_edison --showWiFiIP').read()[:-1]
MY_REMOTE_PORT = GAME_PORT+1
async def remote_socket(reader, writer):
    message = await reader.read()
    message = message.decode()
    print("message: {}".format(message))
    in_battle_header = "in battle: "
    if message.startswith(in_battle_header):
        in_battle = int(message[len(in_battle_header):])
    writer.close()

remote_server_coroutine = asyncio.start_server(remote_socket, MY_REMOTE_IP,
                                               MY_REMOTE_PORT, loop=loop)
remote_server = loop.run_until_complete(remote_server_coroutine)
print("Waiting on {}".format(remote_server.sockets[0].getsockname()))


# Set up local server for receiving inputs from other processes
HOST = '127.0.0.1'    # Symbolic name meaning all available interfaces
PORT = 6666   # Arbitrary non-privileged port
print("Setting up local server for receiving inputs from other "
      "local processes")
async def local_socket(reader, writer):
    message = await reader.read()
    message = message.decode()
    addr = writer.get_extra_info('peername')
    if message != "":
        send_to_game(message)
    writer.close()

local_server_coroutine = asyncio.start_server(local_socket, HOST, PORT,
                                            loop=loop)
local_server = loop.run_until_complete(local_server_coroutine)
print('Serving on {}'.format(local_server.sockets[0].getsockname()))



try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

local_server.close()
loop.run_until_complete(local_server.wait_closed())
loop.close()
