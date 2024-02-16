import inquirer
import os
import time
import argparse
import requests
from requests.exceptions import RequestException
import json
import asyncio
from websockets import *

from texttable import Texttable

################## ARGUMENTS #####################
argParser = argparse.ArgumentParser()
argParser.add_argument("-n", "--num_nodes", help="Nuber of Nodes", default=5, type=int)
#argParser.add_argument("-p", "--port", help="Port in which node is running", default=8000, type=int)
#argParser.add_argument("--ip", help="IP of the host")
args = argParser.parse_args()
# Address of node
# ip_address = args.ip
# port = args.port
num_nodes = args.num_nodes
ip_address = "192.168.1.10"
port = "6789"
address= 'http://' + str(ip_address) + ':' + str(port) 

# Helper function to clear the console
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Command Line Interface client
# Main CLI client rewritten for async/await pattern
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

        if choice == 'New transaction':
            questions = [
                inquirer.Text(name='receiver', message ='What is the Receiver ID of the lucky one?'),
                inquirer.Text(name='amount', message = 'How many BlockChat Coins to send?'),
            ]
            answers = inquirer.prompt(questions)
            response = await new_transaction(answers['receiver'], answers['amount'])
            print(response)

        elif choice == 'New Message':
            questions = [
                inquirer.Text(name='receiver', message ='What is the Receiver ID of the lucky one?'),
                inquirer.Text(name='message', message = 'What is the message?'),
            ]
            answers = inquirer.prompt(questions)
            response = await new_message(answers['receiver'], answers['message'])
            print(response)
            
        elif choice == 'View last transactions':
            response = await view_last_block_transactions()
            # Assuming response processing and printing logic here
            
        elif choice == 'Show balance':
            response = await get_balance()
            print(response)
            
        elif choice == 'Help':
            print('New transaction:')
            print('Send transaction to a node. Select node id and amount.\n\n')
            print('View last transactions')
            print('View the transactions of the last validated block.\n\n')
            print('Show balance')
            print('View the balance of the client from the client wallet.\n\n')
            
        elif choice == 'Exit':
            print("We will miss you")
            break

        input("Press any key to go back...")
        clear_console()

# Running the client in an event loop
if __name__ == "__main__":
    asyncio.run(client())