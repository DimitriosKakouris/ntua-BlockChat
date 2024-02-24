import inquirer
import os
import time
import argparse
import json
import asyncio
import websockets
from websockets_serve import send_websocket_request
from texttable import Texttable


ip_address = os.getenv('IP')
port = os.getenv('PORT')

# address = 'ws://' + str(ip_address) + ':' + str(port)
address = f'ws://{ip_address}:{port}'


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
            choices= ['New Transaction', 'New Message','Add Stake', 'View last transactions', 'Show balance', 'Help', 'Exit'], 
            ),
        ]
        choice = inquirer.prompt(menu)['menu']
        clear_console()

        if choice == 'New Transaction':
            questions = [
                inquirer.Text(name='receiver', message='What is the Receiver wallet address?'),
                inquirer.Text(name='amount', message='How many BlockChat Coins to send?'),
            ]
            answers = inquirer.prompt(questions)
             # Read the receiver ID from the text file
            # with open(answers['receiver'], 'r') as file:
            #     receiver = file.read().strip()
            #     receiver = receiver.replace('\\n', '\n')

            receiver = answers['receiver']
             # Send transaction request
            transaction_data = {'receiver': receiver, 'amount': answers['amount']}
            response = await send_websocket_request('new_transaction', transaction_data, ip_address, port)
            print(response)

        elif choice == 'New Message':
            questions = [
                inquirer.Text(name='receiver', message='What is the Receiver ID of the lucky one?'),
                inquirer.Text(name='message', message='What is the message?'),
            ]
            answers = inquirer.prompt(questions)
            # Send message request
            # with open(answers['receiver'], 'r') as file:
            #     receiver = file.read().strip()
            #     receiver = receiver.replace('\\n', '\n'

            receiver = answers['receiver']
             # Send transaction request
            transaction_data = {'receiver': receiver, 'message': answers['message']}
            response = await send_websocket_request('new_message', transaction_data, ip_address, port)
            print(response)
            # response = await send_websocket_request('new_message', answers, ip_address, port)
          
        elif choice == 'Add Stake':
            questions = [
                inquirer.Text(name='amount', message='How many BlockChat Coins to stake?'),
            ]
            answers = inquirer.prompt(questions)
            # Send stake request
            response = await send_websocket_request('stake', {'amount': answers['amount']}, ip_address, port)
            print(response)
            
        elif choice == 'View last transactions':
            # Assuming you have a specific message format for this request
            response = await send_websocket_request('view_last_transactions', {},ip_address, port)
            print(response)
            
        elif choice == 'Show balance':
            # Assuming you have a specific message format for this request
            print(ip_address, port)
            response = await send_websocket_request('get_balance', {}, ip_address, port)
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
