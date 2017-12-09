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
            game_socket.sendall(command.encode())

# Set up local server for receiving inputs from other processes
loop = asyncio.get_event_loop()
HOST = ''     # Symbolic name meaning all available interfaces
PORT = 6666   # Arbitrary non-privileged port
print("Setting up local server for receiving inputs from other "
      "local processes")
async def local_socket(reader, writer):
    message = await reader.read()
    message = message.decode()
    addr = writer.get_extra_info('peername')
    print("Received {}".format(message))
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
