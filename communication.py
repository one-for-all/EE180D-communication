import asyncio
import websockets
import os

command = ''
loop = asyncio.get_event_loop()

# Set up local server for receiving inputs from other processes
HOST = ''     # Symbolic name meaning all available interfaces
PORT = 6666   # Arbitrary non-privileged port
print("Setting up local server for receiving inputs from other "
      "local processes")
async def local_socket(reader, writer):
    message = await reader.read()
    message = message.decode()
    addr = writer.get_extra_info('peername')
    print("Received {}".format(message))
    global command
    if message == 'START':
        command = 'start'
    elif message == 'PAUSE':
        command = 'pause'
    writer.close()

local_server_coroutine = asyncio.start_server(local_socket, HOST, PORT,
                                            loop=loop)
local_server = loop.run_until_complete(local_server_coroutine)
print('Serving on {}'.format(local_server.sockets[0].getsockname()))


# Set up functions for communicating with Game
print("Setting up communication with Unity game")
# A hacky way of getting wifi ip address
my_ip_address = os.popen('configure_edison --showWiFiIP').read()[:-1]
print("Communication ip address {}".format(my_ip_address))
async def send_command(websocket, path):
    global command
    async for message in websocket:
        if command != '':
            await websocket.send(command)
        command = ''

send_command_server = websockets.serve(send_command, my_ip_address, 8765)
loop.run_until_complete(send_command_server)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

local_server.close()
loop.run_until_complete(local_server.wait_closed())
loop.close()
