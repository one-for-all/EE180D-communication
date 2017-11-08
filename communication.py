import asyncio
import websockets
import socket

command = ''

print("Setting up local server")
# Set up local server for receiving inputs from parts
HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 6666              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

# Set up functions for communicating with Game
my_ip_address = '131.179.26.104'
async def send_command(websocket, path):
    global command
    async for message in websocket:
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                data = data.decode("utf-8")
                print('Received {}'.format(data))
                if data == 'START':
                    command = 'start'
                elif data == 'PAUSE':
                    command = 'pause'
        print("Received {}".format(message))
        await websocket.send(command)
        command = ''

send_command_server = websockets.serve(send_command, my_ip_address, 8765)

asyncio.get_event_loop().run_until_complete(send_command_server)
asyncio.get_event_loop().run_forever()


# while True:
#     conn, addr = s.accept()
#     with conn:
#         print('Connected by', addr)
#         while True:
#             data = conn.recv(1024)
#             if not data:
#                 break
#             data = data.decode("utf-8")
#             print('Received {}'.format(data))
#             if data == 'START':
#                 command = 'start'
#             elif data == 'PAUSE':
#                 command = 'pause'



# async def hello(websocket, path):
#     name = await websocket.recv()
#     print("< {}".format(name))
#
#     greeting = "Hello {}!".format(name)
#     await websocket.send(greeting)
#     print("> {}".format(greeting))

# start_server = websockets.serve(hello, ip_address, 8765)
#
# async def consumer_handler(websocket, path):
#     async for message in websocket:
#         print(message)
#         reply = input()
#         await websocket.send(reply)
#        await consumer(message)
#
#async def consumer(message):
#    print(message)

# consumer_server = websockets.serve(consumer_handler, ip_address, 8765)

# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_until_complete(consumer_server)
# asyncio.get_event_loop().run_forever()
