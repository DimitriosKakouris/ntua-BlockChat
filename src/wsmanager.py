from asyncio import Lock
import logging
import websockets
import json
import asyncio

connections = {}
connections_self_update = {}
# lock = asyncio.Lock()
# lock_update = asyncio.Lock()


locks =  {}
async def send_websocket_request(action, data, ip, port):
    # Define the WebSocket URL
    ws_url = f"ws://{ip}:{port}"

    # Get the WebSocket connection for this URL, or create a new one if it doesn't exist
    websocket = connections.get(ws_url)
    if websocket is None or websocket.closed:
        websocket = await websockets.connect(ws_url,ping_interval=None)
        connections[ws_url] = websocket


    #   # Get the lock for this WebSocket, or create a new one if it doesn't exist
    lock = locks.get(ws_url)
    if lock is None:
        lock = asyncio.Lock()
        locks[ws_url] = lock


    # Define the request
    request = {
        'action': action,
        'data': data
    }
    # print(f"Sending request to {ws_url} with {websocket}: {request}")

    # # #  # Acquire the lock
    # async with lock:
    # Send the request
    await websocket.send(json.dumps(request))

    try:
        # Wait for a response from the server with a timeout
        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
    except asyncio.TimeoutError:
        print(f"No response from {ws_url} within timeout")
        return None

# try:
    return json.loads(response)
   

locks_update = {}
async def send_websocket_request_update(action, data, ip, port):
    # Define the WebSocket URL
    ws_url = f"ws://{ip}:{port}"

    # Get the WebSocket connection for this URL, or create a new one if it doesn't exist
    websocket = connections_self_update.get(ws_url)
    if websocket is None or websocket.closed:
        websocket = await websockets.connect(ws_url,ping_interval=None)
        connections_self_update[ws_url] = websocket


      # Get the lock for this WebSocket, or create a new one if it doesn't exist
    lock = locks_update.get(ws_url)
    if lock is None:
        lock = asyncio.Lock()
        locks_update[ws_url] = lock

    # Define the request
    request = {
        'action': action,
        'data': data
     }
    # print(f"Sending request to {ws_url} with {websocket}: {request}")

    async with lock:
      try:
            # Send the request
            await websocket.send(json.dumps(request))

            # Wait for a response from the server with a timeout
            response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
      except (websockets.exceptions.ConnectionClosedError, asyncio.TimeoutError,ConnectionRefusedError):
            print(f"Connection to {ws_url} lost, retrying...")
            return json.loads('{"message": "Connection to the node lost"}')

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

