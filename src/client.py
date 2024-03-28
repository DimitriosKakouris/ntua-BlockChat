import inquirer
import os
import asyncio
from wsmanager import send_websocket_request, send_websocket_request_unique
import json

from dotenv import load_dotenv
load_dotenv()
ip_address = os.getenv('IP')
port = os.getenv('PORT')
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

        #res = await send_websocket_request_unique('check_allow_transactions', {}, ip_address, port)
        #if not res['variable']:
        if os.getenv('ALLOW_TRANSACTIONS') == 'False':
            print("\nTransactions can be executed when all nodes are connected.")
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
            print('Help text goes here...')
            


        elif choice == 'Exit':
            print("Exiting...")
            break


    if choice != 'Exit':
        input("Press enter to continue...")
        clear_console()
    else:
       
        running = False



if __name__ == "__main__":
    asyncio.run(client())