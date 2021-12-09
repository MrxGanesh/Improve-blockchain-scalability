import numpy as np
import matplotlib.pyplot as plt
import pickle
from matplotlib import cm

'''
def plotThptvEpoch(nShards, nNodes, nEpochs, data, nType,file):
    for method in ['Max']:
        for s in nType:
            t = data[s]['tVer' + method]
            throughput = nShards[-1] / t[-1, :] / 1000  # t in secs
            plt.plot(nEpochs, throughput, label=s)
            plt.xlabel('Epoch index')
            plt.ylabel('Throughput (# blocks/ms)')
            title = 'type: ' + s 
            plt.title(title)
            plt.grid()
            plt.legend(loc='best')
        plt.savefig("thptvsepoch.png")
'''


def plotThptvNode(nShards, nNodes, nEpochs, data, nType, file):
    for method in ['Max']:
        for s in nType:
            t = data[s]['tVer' + method]
            throughput = nShards / t[:, -1] / 1000   #t in secs
            plt.plot(nNodes, throughput, label=s)
            plt.xlabel('Processing Nodes')
            plt.ylabel('Throughput (# blocks/ms)')
            title = 'type: ' + s
            plt.title(title)
            plt.grid()
            plt.legend(loc='best')
        plt.show()
        plt.savefig("thptvsNode.png")


def plots(file):
    with open(file, 'rb') as handle:
        result = pickle.load(handle)
    data = result['data']
    nShards = np.array(result['nShards'])
    nNodes = np.array(result['nNodes'])
    nEpochs = np.array(result['nEpochs'])
    nType = list(data.keys())

   
    # plot throughput v.s. epoches for the largest # of shards
    #plotThptvEpoch(nShards, nNodes, nEpochs, data, nType,file)
    # plot throughput v.s. # of nodes for the last epoch
    plotThptvNode(nShards, nNodes, nEpochs, data, nType, file)


file = 'all_results_dense_K=[5,50]_M=2000_.pickle'

plots((file))