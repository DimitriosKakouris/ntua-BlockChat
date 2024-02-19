import inquirer
import os
import time
import argparse
import json
import asyncio
import websockets
# from websockets_serve import new_transaction, new_message, view_last_block_transactions, get_balance

from texttable import Texttable

################## ARGUMENTS #####################
argParser = argparse.ArgumentParser()
argParser.add_argument("-p", "--port", help="Port in which node is running", default=8000, type=int)
argParser.add_argument("--ip", help="IP of the host")
args = argParser.parse_args()
# Address of node
ip_address = args.ip
port = args.port


# address = 'ws://' + str(ip_address) + ':' + str(port)
address = f'ws://{ip_address}:{port}'

async def send_websocket_request(path, data):
    async with websockets.connect(address) as websocket:
        # Convert the data to JSON and send it
        await websocket.send(json.dumps({'path': path, 'data': data}))
        # Wait for a response and return it
        response = await websocket.recv()
        return response

# Helper function to clear the console
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Command Line Interface client
async def client():
    clear_console()
    while True:
        menu = [ 
            inquirer.List('menu', 
            message= "BlockChat Client", 
            choices= ['New Transaction', 'New Message', 'View last transactions', 'Show balance', 'Help', 'Exit'], 
            ),
        ]
        choice = inquirer.prompt(menu)['menu']
        clear_console()

        if choice == 'New Transaction':
            questions = [
                inquirer.Text(name='receiver', message='What is the Receiver ID of the lucky one?'),
                inquirer.Text(name='amount', message='How many BlockChat Coins to send?'),
            ]
            answers = inquirer.prompt(questions)
            # Send transaction request
            response = await send_websocket_request('new_transaction', answers)
            print(response)

        elif choice == 'New Message':
            questions = [
                inquirer.Text(name='receiver', message='What is the Receiver ID of the lucky one?'),
                inquirer.Text(name='message', message='What is the message?'),
            ]
            answers = inquirer.prompt(questions)
            # Send message request
            response = await send_websocket_request('new_message', answers)
            print(response)
            
        elif choice == 'View last transactions':
            # Assuming you have a specific message format for this request
            response = await send_websocket_request('view_last_transactions', {})
            print(response)
            
        elif choice == 'Show balance':
            # Assuming you have a specific message format for this request
            response = await send_websocket_request('get_balance', {})
            print(response)

        elif choice == 'Help':
            # Display help text
            print('Help text goes here...')
            
        elif choice == 'Exit':
            print("Exiting...")
            break

        input("Press any key to continue...")
        clear_console()

if __name__ == "__main__":
    asyncio.run(client())
