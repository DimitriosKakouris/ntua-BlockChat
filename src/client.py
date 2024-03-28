import inquirer
import os
import asyncio
from wsmanager import send_websocket_request
import json
import subprocess

from dotenv import load_dotenv
load_dotenv()

result = subprocess.run(["hostname", "-I"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
ips = result.stdout.strip().split()
matched_ip = [i for i in ips if "10.110.0" in i]
ip_address = matched_ip[0]
port = 80

address = f'ws://{ip_address}:{port}'


# Helper function to clear the console
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')



def prompt_with_interrupt(questions):
    try:
        return inquirer.prompt(questions)
    except KeyboardInterrupt:
        return None  # Indicate that an interrupt occurred




# Command Line Interface client
async def client():
    clear_console()
    running = True
    while running:
      
        menu = [ 
            inquirer.List('menu', 
            message= "BlockChat Client", 
            choices= ['New Transaction', 'New Message','Add Stake', 'View last block','View Last Messages', 'Show balance', 'Help', 'Exit'], 
            ),
        ]
        choice = prompt_with_interrupt(menu)
        if choice is None:
            print("\nReturning to main menu...")
            continue
        choice = choice['menu']
        clear_console()

        data = await send_websocket_request('get_ring_length', {}, ip_address, port)
        if data['ring_len'] < int(os.getenv('TOTAL_NODES')) and choice != 'Exit':
            print("\nPlease wait for all nodes to join the network before choosing an action.")
            continue
        elif choice == 'New Transaction':
            questions = [
                inquirer.Text(name='receiver', message='What is the Receiver ID?'),
                inquirer.Text(name='amount', message='How many BlockChat Coins to send?'),
            ]
            answers = prompt_with_interrupt(questions)
            if answers is None:
                print("\nReturning to main menu...")
                continue
      
            receiver = answers['receiver']
            # Send transaction request
            transaction_data = {'receiver': receiver, 'amount': answers['amount']}
            response = await send_websocket_request('new_transaction', transaction_data, ip_address, port)
            # print(response)





        elif choice == 'New Message':
            questions = [
                inquirer.Text(name='receiver', message='What is the Receiver ID?'),
                inquirer.Text(name='message', message='What is the message?'),
            ]
            answers = prompt_with_interrupt(questions)
            if answers is None:
                print("\nReturning to main menu...")
                continue
         


            receiver = answers['receiver']
            # Send transaction request
            transaction_data = {'receiver': receiver, 'message': answers['message']}
            response = await send_websocket_request('new_message', transaction_data, ip_address, port)
            # print(response)
            # response = await send_websocket_request('new_message', answers, ip_address, port)
        



        elif choice == 'Add Stake':
            questions = [
                inquirer.Text(name='amount', message='How many BlockChat Coins to stake?'),
            ]
            answers = prompt_with_interrupt(questions)
            if answers is None:
                print("\nReturning to main menu...")
                continue
            # Send stake request
            response = await send_websocket_request('stake', {'amount': answers['amount']}, ip_address, port)
            # print(response)
            



        elif choice == 'View last block':
            # Assuming you have a specific message format for this request
            response = await send_websocket_request('view_last_transactions', {}, ip_address, port)
            print(json.dumps(response, indent=4))




        elif choice == 'View Last Messages':
            response = await send_websocket_request('view_last_messages', {}, ip_address, port)
            print(json.dumps(response, indent=4))
            



        elif choice == 'Show balance':
            # Assuming you have a specific message format for this request
            print(ip_address, port)
            response = await send_websocket_request('get_balance', {}, ip_address, port)
            print("Balance:", response['balance'])
            print("Amount reserved for staking:", response['stake'])
            print("Confirmed balance:", response['confirmed_balance'])
            print("Confirmed amount reserved for staking:", response['confirmed_stake'])



        elif choice == 'Help':
            # Display help text
            print('Choose among the following actions:')
            print('\t\u2022New Transaction: Send BlockChat Coins to another user.')
            print('\t\u2022New Message: Send a message to another user.')
            print('\t\u2022Add Stake: Stake some of your BlockChat Coins.')
            print('\t\u2022View last block: View the transactions of the last validated block of the blockchain.')
            print('\t\u2022View Last Messages: View all the messages you have received by other users.')
            print('\t\u2022Show balance: Display your current soft and hard state of balance and staking amount.')
            print('\t\u2022Help: Display this help text.')
            print('\t\u2022Exit: Close the client.')
            print('You can return to the main menu at any time by pressing Ctrl+C.')

        elif choice == 'Exit':
            print("Exiting...")
            running = False
            break

        if choice != 'Exit':
            input("Press enter to continue...")
            clear_console()
        # else:
        #     running = False
        #     break



if __name__ == "__main__":
    asyncio.run(client())