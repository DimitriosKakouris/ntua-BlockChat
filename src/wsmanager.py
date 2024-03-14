from asyncio import Lock
import websockets
import json
import asyncio

connections = {}
connections_self_update = {}
lock = asyncio.Lock()

async def send_websocket_request(action, data, ip, port):
    # Define the WebSocket URL
    ws_url = f"ws://{ip}:{port}"

    # Get the WebSocket connection for this URL, or create a new one if it doesn't exist
    websocket = connections.get(ws_url)
    if websocket is None or websocket.closed:
        websocket = await websockets.connect(ws_url,ping_interval=None)
        connections[ws_url] = websocket

    # Define the request
    request = {
        'action': action,
        'data': data
    }
    print(f"Sending request to {ws_url} with {websocket}: {request}")

    #  # Acquire the lock
    # async with lock:
    # Send the request
    await websocket.send(json.dumps(request))

    # Wait for a response from the server
    response = await websocket.recv()
    print(f"Response from {ws_url}: {response} with request {request}")


    # try:
    return json.loads(response)
   


async def send_websocket_request_self_update(action, data, ip, port):
    # Define the WebSocket URL
    ws_url = f"ws://{ip}:{port}"

    # Get the WebSocket connection for this URL, or create a new one if it doesn't exist
    websocket = connections.get(ws_url)
    if websocket is None or websocket.closed:
        websocket = await websockets.connect(ws_url,ping_interval=None)
        connections_self_update[ws_url] = websocket

    # Define the request
    request = {
        'action': action,
        'data': data
    }
    print(f"Sending request to {ws_url} with {websocket}: {request}")

    # async with lock:
    # Send the request
    await websocket.send(json.dumps(request))

    # Wait for a response from the server
    response = await websocket.recv()
    print(f"Response from {ws_url}: {response} with request {request}")

    
    return json.loads(response)
  

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
        # print(f'##############NEW WEBSOCKET REQUEST: {websocket}#################3')

        # Send the request
        await websocket.send(json.dumps(request))

        # Wait for a response from the server
        response = await websocket.recv()

    # Return the response
    return json.loads(response)

