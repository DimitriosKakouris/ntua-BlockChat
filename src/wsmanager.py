from asyncio import Lock
import websockets
import json

async def send_websocket_request(action, data, ip, port):
     # Define the WebSocket URL
    ws_url = f"ws://{ip}:{port}"

    # Define the request
    request = {
        'action': action,
        'data': data
    }

    # print(f"Sending request to {ws_url}: {request}")
    # Connect to the WebSocket server and send the request
    async with websockets.connect(ws_url) as websocket:
        await websocket.send(json.dumps(request))

        # Wait for a response from the server
        response = await websocket.recv()

    # Return the response
    return json.loads(response)

# connections = {}
# locks = {}

# async def send_websocket_request(action, data, sender_ip, sender_port, receiver_ip, receiver_port):
#     # Define the WebSocket URL
#     ws_url = f"ws://{receiver_ip}:{receiver_port}"

#     # Define the request
#     request = {
#         'action': action,
#         'data': data
#     }

#     # Define the connection pair
#     pair = (f"{sender_ip}:{sender_port}", f"{receiver_ip}:{receiver_port}")

#     # Check if a connection to this node already exists
#     if pair not in connections:
#         # Connect to the WebSocket server and store the connection
#         websocket = await websockets.connect(ws_url)
#         connections[pair] = websocket
#         locks[pair] = Lock()  # Create a new lock for this connection

#     # Use the lock to ensure that only one coroutine uses the connection at a time
#     async with locks[pair]:
#         # Send the request
#         await connections[pair].send(json.dumps(request))

#         # Wait for a response from the server
#         response = await connections[pair].recv()

#     # Return the response
#     return json.loads(response)