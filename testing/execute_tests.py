import asyncio
import time
from websockets_serve import node, IP_ADDRESS, PORT, total_nodes
from wsmanager import send_websocket_request
from block import block_capacity

total_time = 0
num_transactions = 0


async def execute_transactions():
    """This function sends the transactions of the text file"""

    global total_time
    global num_transactions
    node_id = node.id
    transaction_file = f'./input/trans{node_id}.txt'
    
    with open(transaction_file, 'r') as f:
        for i, line in enumerate(f):
            # Get the info of the transaction.
            print(f"Sending transaction no. {i}")
            line = line.split(' ', 1)
            receiver_id = int(line[0][2])
            message = line[1].strip()
            transaction_data = {'receiver': receiver_id, 'message': message}
            blockchain_timestamps = []
            # Send the current transaction.
            try:
                start_time = time.time()
                response = await send_websocket_request('new_message', transaction_data, IP_ADDRESS, PORT)
                transaction_time = time.time() - start_time
                block_timestamp = await send_websocket_request('get_last_block_timestamp', {}, IP_ADDRESS, PORT)
                block_timestamp = block_timestamp['timestamp']
                if len(blockchain_timestamps) == 0 or block_timestamp != blockchain_timestamps[-1]:
                    blockchain_timestamps.append(block_timestamp)
                total_time += transaction_time
                num_transactions += 1
                print(response['message'])
            except:
                exit("Node is not active. Try again later.\n")

    
    block_times = [blockchain_timestamps[i+1] - blockchain_timestamps[i] for i in range(len(blockchain_timestamps) - 1)]
    throughput = num_transactions/total_time
    block_time = sum(block_times)/len(block_times)

    with open(f'./results/{total_nodes}_clients_node_{node_id}.txt', 'a') as f:
        f.write('Final results for node %d\n' %node_id)
        f.write('Throughput: %f\n' %throughput)
        f.write('Block time: %f\n' %block_time)
        f.write('Capacity: %d\n' %block_capacity)
        f.write('-----------------------------------')
        f.write('\n')
    

# Run the server
if __name__ == "__main__":
    asyncio.run(execute_transactions())