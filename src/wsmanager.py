from asyncio import Lock
import websockets
import json

connections = {}
# async def send_websocket_request(action, data, ip, port):
#      # Define the WebSocket URL
#     ws_url = f"ws://{ip}:{port}"

#     # Define the request
#     request = {
#         'action': action,
#         'data': data
#     }

#     # print(f"Sending request to {ws_url}: {request}")
#     # Connect to the WebSocket server and send the request
#     async with websockets.connect(ws_url) as websocket:
#         await websocket.send(json.dumps(request))

#         # Wait for a response from the server
#         response = await websocket.recv()

#     # Return the response
#     return json.loads(response)



async def send_websocket_request(action, data, ip, port):
    # Define the WebSocket URL
    ws_url = f"ws://{ip}:{port}"

    # Get the WebSocket connection for this URL, or create a new one if it doesn't exist
    websocket = connections.get(ws_url)
    if websocket is None or websocket.closed:
        websocket = await websockets.connect(ws_url)
        connections[ws_url] = websocket

    # Define the request
    request = {
        'action': action,
        'data': data
    }
    print(f"Sending request to {ws_url} with {websocket}: {request}")

    # Send the request
    await websocket.send(json.dumps(request))

    # Wait for a response from the server
    response = await websocket.recv()
    print(f"Response from {ws_url}: {response} with request {request}")

    # try:
    return json.loads(response)
    # except json.JSONDecodeError:
    #     return None

async def send_websocket_request_unique(action, data, ip, port):
    # Define the WebSocket URL
    ws_url = f"ws://{ip}:{port}"

    # Connect to the WebSocket server and send the request
    async with websockets.connect(ws_url) as websocket:
        # Define the request
        request = {
            'action': action,
            'data': data
        }

        # Send the request
        await websocket.send(json.dumps(request))

        # Wait for a response from the server
        response = await websocket.recv()

    # Return the response
    return json.loads(response)

async def broadcast_websocket_request(action, data):
    request={
        'action': action,
        'data': data
    }
    websocket.broadcast(connections.values(), json.dumps(request))

# async def broadcast_websocket_request(action, data):
#     # Create a list of tasks, one for each connection
#     tasks = [send_websocket_request(action, data, ip, port) for (ip, port) in connections]

#     # Wait for all tasks to complete
#     responses = await asyncio.gather(*tasks)

#     # Return the responses
#     return responses
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