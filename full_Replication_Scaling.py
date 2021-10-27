import numpy as np
import pickle
import time
import matplotlib.pyplot as plt
import full_Replication as fr


def chainInitiation(nShards, nUShard, sparsity, chainLength, initBalance):
    
    # initiate chain
    chains = fr.InitiateChain(nShards, nUShard, initBalance)
    txCap = initBalance/ chainLength/2
    for k in range(nShards):
        for e in range(chainLength):
            chains[k] = np.vstack([chains[k], fr.createBlock(nUShard, sparsity, txCap)])
    
    return chains


def fullReplicationScaling (nNodes, nShards, nUShard, sparsity, nEpochs, initBalance):

    '''
    Verify process of a full replication blockchain in a single epoch,
    with nEpochs blocks verified in each chain
    '''

    # initialize system afer n epoches (n=nEpochs)
    chainLength = nEpochs - 1
    chains = chainInitiation(nShards, nUShard, sparsity, chainLength, initBalance)
    tVerify = np.zeros(nEpochs)
    tVote = np.zeros(nEpochs)
    tUpdate = np.zeros(nEpochs)

    tVerifyMax, tVerifyMedian, tVote, tUpdate = \
         fr.simulateEpoch(chains, tVerify, tUpdate, tVote, nNodes, nShards, nUShard, 
                            sparsity, nEpochs-1, initBalance/nEpochs)
    
    return tVerifyMax, tVote, tUpdate


def scaleFullReplication(nShards, redundancy, nUShard, sparsity, nEpochs, initBalance):
    nNodes = nShards * redundancy
    scale = nShards.size

    tVerify = np.zeros(scale)
    tUpdate = np.zeros(scale)
    tVote = np.zeros(scale)
    throughput = np.zeros(scale)

    for i in range(scale):
        tVerify[i], tVote[i], tUpdate[i] = \
            fullReplicationScaling(nNodes[i], nShards[i], nUShard, sparsity, nEpochs, initBalance)

        throughput[i] = nShards[i]/ (tVerify[i] + tVote[i])
    
    result = {}
    result['verification time'] = tVerify
    result['voting time'] = tVote
    result['updating time'] = tUpdate
    result['throughput'] = throughput
    file = 'full_replication_redundancy_' + str(redundancy) +\
               '_M_' + str(nUShard) + '_s_' +\
               str(sparsity) + '_numEpochs_' + str(nEpochs) + '_' +\
               str(int(time.time())) + '.pickle'
    with open(file, 'wb') as handle:
        pickle.dump(result, handle)

    return tVerify, tVote, tUpdate, throughput, file

def plots(file, nNodes):
    print(file)
    with open(file, 'rb') as handle:
        result = pickle.load(handle)
    for key in result.keys():
        if key == 'throughput':
            plt.plot(nNodes, result[key], label=key)
    plt.xlabel('Number of nodes')
    plt.ylabel('Throughput (# of blocks per sec)')
    plt.grid()
    plt.legend(loc='best')
    plt.title('Data source:\n' + file)
    plt.xlim((0, None))
    plt.ylim((0, None))
    plt.tight_layout()
    plt.show()