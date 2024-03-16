import asyncio
import os
import time
from test_websockets_serve import total_nodes
from wsmanager import send_websocket_request
from block import block_capacity

total_time = 0
num_transactions = 0
staking_amount = 10

async def execute_transactions(node_id, IP_ADDRESS, PORT):
    """This function sends the transactions of the text file"""
    print(f"Executing transactions for node {node_id} with IP {IP_ADDRESS} and port {PORT}...")
    # exit()
    
    # asyncio.sleep(0.2)
    response = await send_websocket_request('stake', {'amount': staking_amount}, IP_ADDRESS, PORT)
    print(response['message'])

    global total_time
    global num_transactions
    transaction_file = f'./input/trans{node_id}.txt'
    # blockchain_timestamps = []

    # await asyncio.sleep(1)
    
    with open(transaction_file, 'r') as f:
        for i, line in enumerate(f):
            # Get the info of the transaction.
            print(f"Sending transaction no. {i}")
            # await asyncio.sleep(0.3)
            line = line.split(' ', 1)
            receiver_id = int(line[0][2])
            message = line[1].strip()
            transaction_data = {'receiver': receiver_id, 'message': message}
            # Send the current transaction.
            try:
                start_time = time.time()
                response = await send_websocket_request('new_message', transaction_data, IP_ADDRESS, PORT)
                transaction_time = time.time() - start_time
                # block_timestamp = await send_websocket_request('get_last_block_timestamp', {}, IP_ADDRESS, PORT)
                # block_timestamp = float(block_timestamp['timestamp'])
                # if len(blockchain_timestamps) == 0 or block_timestamp != blockchain_timestamps[-1]:
                #     blockchain_timestamps.append(block_timestamp)
                total_time += transaction_time
                num_transactions += 1
                print(response['message'])
            except:
                exit("Node is not active. Try again later.\n")

    await asyncio.sleep(6)
    blockchain_timestamps = await send_websocket_request('get_block_timestamps', {}, IP_ADDRESS, PORT)
    print(f'Blockchain timestamps: {blockchain_timestamps}')
     
    block_times = [blockchain_timestamps[i+1] - blockchain_timestamps[i] for i in range(len(blockchain_timestamps) - 1)]
    throughput = num_transactions/total_time
    # block_time = sum(block_times)/len(block_times)

    print('-----------------------------------')
    print('Final results for node %d' %node_id)
    print('Throughput: %f' %throughput)
    # print('Block time: %f' %block_time)
    print('Capacity: %d' %block_capacity)
    print('-----------------------------------')

    os.makedirs('/app/results', exist_ok=True)
    with open(f'/app/{total_nodes}_clients_node_{node_id}.txt', 'a') as f:
        f.write('Final results for node %d\n' %node_id)
        f.write('Throughput: %f\n' %throughput)
        # f.write('Block time: %f\n' %block_time)
        f.write('Capacity: %d\n' %block_capacity)
        f.write('-----------------------------------')
        f.write('\n')
    