import asyncio
import time
from websockets_serve import node, IP_ADDRESS, PORT, total_nodes
from wsmanager import send_websocket_request

total_time = 0
num_transactions = 0
total_mining_time = 0



async def execute_transactions():
    """This function sends the transactions of the text file"""

    global total_time
    global num_transactions
    global total_mining_time
    #address = 'http://' + IPAddr + ':' + str(port) + '/api/create_transaction'
    node_id = int(PORT) - 8000
    transaction_file = f'./input/trans{node_id}.txt'
    # id_to_pk = [None] * total_nodes
    # for dic in node.ring:
    #     id = int(dic['id'])
    #     id_to_pk[id] = dic['public_key']

    with open(transaction_file, 'r') as f:
        for i, line in enumerate(f):
            # Get the info of the transaction.
            print(f"Sending transaction no. {i}")
            line = line.split(' ', 1)
            receiver_id = int(line[0][2])
            message = line[1].strip()
            transaction_data = {'receiver': receiver_id, 'message': message}
                
            #transaction = {'receiver': receiver_id, 'amount': amount}

            #print(f'Transaction {id} -> {receiver_id} : {amount} nbc')

            # Send the current transaction.
            try:
                start_time = time.time()
                response = await send_websocket_request('new_message', transaction_data, IP_ADDRESS, PORT)
                total_time = time.time() - start_time
                #message = response.json()["message"]
                minting_time = response.json()["mining_time"]
                if response.status_code == 200:
                    total_time += total_time
                    num_transactions += 1
                    total_mining_time += minting_time
                print(message + "\n")
            except:
                exit("Node is not active. Try again later.\n")

    print(f"\nTransactions for node {id} are done and the results are available on the results file")

    try:
        address = 'http://' + IPAddr + ':' + str(port) + '/api/get_metrics'
        response = requests.get(address).json()
        num_blocks = response['num_blocks'] - 1
        capacity = response['capacity']
        difficulty = response['difficulty']
        node_id = int(id)
        throughput = num_transactions/total_time
        block_time = total_mining_time/num_blocks

        # with open('./results/5node' + str(node_id) + '.txt', 'a') as f:
        with open('./results/10node' + str(node_id) + '.txt', 'a') as f:
            f.write('------------------------\n')
            f.write('Final results for node %d\n' %node_id)
            f.write('------------------------\n')
            f.write('Throughput: %f\n' %throughput)
            f.write('Block time: %f\n' %block_time)
            f.write('Capacity: %d\n' %capacity)
            f.write('Difficulty: %d\n' %difficulty)
            f.write('\n')
    except:
        exit("\nSomething went wrong while receiving the total blocks.\n")

def get_id():
    address = 'http://' + IPAddr + ':' + str(port) + '/api/get_id'
    response = requests.get(address).json()
    message = response['message']
    return message


# Run the server
if __name__ == "__main__":
    asyncio.run(execute_transactions())

# if __name__ == "__main__":
#     # Define the argument parser.
#     parser = ArgumentParser(description='Sends transactions in the noobcash blockchain given from a text file.')

#     required = parser.add_argument_group('required arguments')
#     required.add_argument('-d', help='path to the directory of the transactions', required=True)
#     required.add_argument('-p', type=int, help='port that the api is listening on', required=True)

#     # Parse the given arguments.
#     args = parser.parse_args()
#     input_dir = args.d
#     port = args.p

#     input("\nPress Enter to start the transactions\n")

#     # Find the corresponding transaction file.
#     id = get_id()
#     input_file = os.path.join(input_dir, 'transactions' + str(id) + '.txt')

#     start_transactions()