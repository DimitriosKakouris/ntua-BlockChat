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
    print("Welcome to the BlockChat Client!")
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

        if choice != 'Exit':
            data = await send_websocket_request('get_ring_length', {}, ip_address, port)
            if data['ring_len'] < int(os.getenv('TOTAL_NODES')):
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
                ring_len = await send_websocket_request('get_ring_length', {}, ip_address, port)
                if int(receiver) >= ring_len['ring_len']:
                    print("\nReceiver ID is out of range. Please enter a valid ID.")
                    continue
                # Send transaction request
                transaction_data = {'receiver': receiver, 'amount': answers['amount']}
                response = await send_websocket_request('new_transaction', transaction_data, ip_address, port)




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
                ring_len = await send_websocket_request('get_ring_length', {}, ip_address, port)
                if int(receiver) >= ring_len['ring_len']:
                    print("\nReceiver ID is out of range. Please enter a valid ID.")
                    continue
                # Send transaction request
                transaction_data = {'receiver': receiver, 'message': answers['message']}
                response = await send_websocket_request('new_message', transaction_data, ip_address, port)
            



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
                



            elif choice == 'View last block':
                response = await send_websocket_request('view_last_transactions', {}, ip_address, port)
                print(json.dumps(response, indent=4))




            elif choice == 'View Last Messages':
                response = await send_websocket_request('view_last_messages', {}, ip_address, port)
                print(json.dumps(response, indent=4))
                



            elif choice == 'Show balance':
                print(ip_address, port)
                response = await send_websocket_request('get_balance', {}, ip_address, port)
                print("Balance:", response['balance'])
                print("Amount reserved for staking:", response['stake'])
                print("Confirmed balance:", response['confirmed_balance'])
                print("Confirmed amount reserved for staking:", response['confirmed_stake'])



            elif choice == 'Help':
                # Display help text
                print('Choose among the following actions:')
                print('  \u2022 New Transaction: Send BlockChat Coins to another user.')
                print('  \u2022 New Message: Send a message to another user.')
                print('  \u2022 Add Stake: Stake some of your BlockChat Coins.')
                print('  \u2022 View last block: View the transactions of the last validated block of the blockchain.')
                print('  \u2022 View Last Messages: View all the messages you have received by other users.')
                print('  \u2022 Show balance: Display your current soft and hard state of balance and staking amount.')
                print('  \u2022 Help: Display this help text.')
                print('  \u2022 Exit: Close the client.')
                print('You can return to the main menu at any time by pressing Ctrl+C.')
            
            input("Press enter to continue...")
            clear_console()

        else:
            print("Exiting...")
            running = False
            break




if __name__ == "__main__":
    asyncio.run(client())