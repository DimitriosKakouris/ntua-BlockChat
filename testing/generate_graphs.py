import matplotlib.pyplot as plt
import numpy as np

import re

def to_snake_case(text):
    text_no_parentheses = re.sub(r'\(.*\)', '', text).strip()
    snake_case_text = re.sub(r'\s+', '_', text_no_parentheses).lower()
    return snake_case_text

def draw_plots(v1, v1b, v2, v2b, v3, v3b, xlabel, title):
    nodes = np.array([5, 10])
    configurations = ['CAPACITY=5', 'CAPACITY=10', 'CAPACITY=20']
    
    
    data = {}
    data[configurations[0]] = np.array([v1, v1b])
    data[configurations[1]] = np.array([v2, v2b])
    data[configurations[2]] = np.array([v3, v3b])


    fig, ax = plt.subplots()

    colors = ['blue', 'green', 'purple']
    markers = ['o', 's', '*']

    for i, config in enumerate(configurations):
        ax.plot(nodes, data[config], label=f'{config}', color=colors[i], marker=markers[i])

    ax.set_xlabel(xlabel)

    ax.set_title(title)

    ax.set_xticks([5, 10])

    ax.legend()

    plt.grid(True)

    plt.savefig(f'./graphs/{to_snake_case(title)}.png')


throughput_pattern = re.compile(r'Throughput: (\d+\.\d+)')
def access_throughput_values(num_clients, node):
    throughput_values = []
    with open(f'./results/{num_clients}_clients_node_{node}.txt', 'r') as f:
        for line in f:
            match = throughput_pattern.search(line)
            if match:
                throughput_value = float(match.group(1))
                throughput_values.append(throughput_value)
    return throughput_values[:3]

v1_lst = []
v2_lst = []
v3_lst = []
for i in range(5):
    results = access_throughput_values(5, i)
    v1_lst.append(results[0])
    v2_lst.append(results[1])
    v3_lst.append(results[2])
    
v1b_lst = []
v2b_lst = []
v3b_lst = []
for i in range(10):
    results = access_throughput_values(10, i)
    v1b_lst.append(results[0])
    v2b_lst.append(results[1])
    v3b_lst.append(results[2])


# Plot for throughput
v1 = np.mean(v1_lst)
v2 = np.mean(v2_lst)
v3 = np.mean(v3_lst)

v1b = np.mean(v1b_lst)
v2b = np.mean(v2b_lst)
v3b = np.mean(v3b_lst)

draw_plots(v1, v1b, v2, v2b, v3, v3b, 'Number of Nodes', 'Throughput (transactions per second)')


blocktime_pattern = re.compile(r'Block time: (\d+\.\d+)')
def access_blocktime_values(num_clients, node):
    blocktime_values = []
    with open(f'./results/{num_clients}_clients_node_{node}.txt', 'r') as f:
        for line in f:
            match = blocktime_pattern.search(line)
            if match:
                blocktime_value = float(match.group(1))
                blocktime_values.append(blocktime_value)
    return blocktime_values[:3]

# Plot for block time
results = access_blocktime_values(5, 0)
v1 = results[0]
v2 = results[1]
v3 = results[2]

results = access_blocktime_values(10, 0)
v1b = results[0]
v2b = results[1]
v3b = results[2]


draw_plots(v1, v1b, v2, v2b, v3, v3b, 'Number of Nodes', 'Block Time (seconds)')
