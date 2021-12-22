import networkx as nx
import matplotlib.pyplot as plt
import warnings
from communicator import Communicator


def plot_network(peers_shard, rank):
    comm = Communicator()
    g = nx.Graph()
    plt.figure(figsize=(15, 15))
    # plt.axis('off')
    fig = plt.gcf()
    if rank == 0:
        fig.canvas.set_window_title("Processing Validators")
    elif rank == (comm.nbprocs-1):
        fig.canvas.set_window_title("Notaries")
    else:
        fig.canvas.set_window_title(f"shard {rank}")
    node_ids = list(peers_shard)
    g.add_nodes_from(node_ids)
    g.add_edges_from([[k, i] for k, v in peers_shard.items() for i in v])

    pos = nx.kamada_kawai_layout(g)
    warnings.filterwarnings("ignore")
    nx.draw(g, pos, with_labels=True, node_size=1200, node_color='y')
    warnings.resetwarnings()
    plt.savefig('./sharding/processing')

def plot_transaction_shard(time, transactions):
    fig = plt.figure()
    warnings.filterwarnings("ignore")
    fig.canvas.set_window_title("throughput")
    ax = fig.add_subplot(111)
    ax.set_ylabel('Transactions')
    ax.set_xlabel('Node Processing Tiem')
    # plt.plot(time, list(range(10000)))
    plt.plot(time, transactions)
    plt.title('throughput')
    warnings.resetwarnings()
    plt.savefig('./sharding/txsVtime')