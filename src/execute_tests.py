import asyncio
import os
import sys
import time
import pytz
from wserve import total_nodes, compute_justice
from wsmanager import send_websocket_request
from block import block_capacity
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

total_time = 0
num_transactions = 0
staking_amount = 10
if compute_justice:
    higher_stake = 100
    chosen_ip = os.getenv('BOOTSTRAP_IP', '10.110.0.2')
    chosen_port = os.getenv('BOOTSTRAP_PORT', '80')

async def execute_transactions(node_id, IP_ADDRESS, PORT):
    """This function sends the transactions of the text file"""
    print(f"Executing transactions for node {node_id} with IP {IP_ADDRESS} and port {PORT}...")

    if compute_justice:
        if IP_ADDRESS == chosen_ip and PORT == chosen_port:
            print(f"Node {node_id} is the chosen one. Staking {higher_stake} coins...")
            response = await send_websocket_request('stake', {'amount': higher_stake}, IP_ADDRESS, PORT)
        else:
            print(f"Staking {staking_amount} coins...")
            response = await send_websocket_request('stake', {'amount': staking_amount}, IP_ADDRESS, PORT)
    else:
        print(f"Staking {staking_amount} coins...")
        response = await send_websocket_request('stake', {'amount': staking_amount}, IP_ADDRESS, PORT)

    global total_time
    global num_transactions
    transaction_file = f'./testing/{total_nodes}nodes/trans{node_id}.txt'
    
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
                total_time += transaction_time
                num_transactions += 1
            except:
                exit("Node is not active. Try again later.\n")

        await asyncio.sleep(10)
        timestamps_validators= await send_websocket_request('get_block_timestamps', {}, IP_ADDRESS, PORT)
        blockchain_timestamps = timestamps_validators['blocks']
        blockchain_validators = timestamps_validators['validators']
        tuple_list = list(zip(blockchain_timestamps, blockchain_validators))
        print(f'Blockchain timestamps and validators: {tuple_list}')
        
        block_times = [float(blockchain_timestamps[i+1]) - float(blockchain_timestamps[i]) for i in range(len(blockchain_timestamps) - 1)]
        throughput = num_transactions/total_time
        block_time = sum(block_times)/len(block_times)

        print('-----------------------------------')
        print('Final results for node %d' %node_id)
        print('Throughput: %f' %throughput)
        print('Block time: %f' %block_time)
        print('Capacity: %d' %block_capacity)
        print('-----------------------------------')
        timezone = pytz.timezone('Europe/Athens')
        date = datetime.now(timezone).strftime('%Y-%m-%d %H:%M')
        os.makedirs('./testing/results', exist_ok=True)
        with open(f'./testing/results/{total_nodes}_clients_node_{node_id}.txt', 'a') as f:
            f.write(date)
            f.write('\nFinal results for node %d\n' %node_id)
            f.write(f'Blockchain timestamps and validators: {tuple_list}\n')
            f.write('Throughput: %f\n' %throughput)
            f.write('Block time: %f\n' %block_time)
            f.write('Capacity: %d\n' %block_capacity)
            f.write('-----------------------------------')
            f.write('\n')
        
        