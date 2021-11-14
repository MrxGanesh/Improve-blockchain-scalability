import numpy as np
import pickle
import time
import matplotlib.pyplot as plt
import full_Replication_Scaling as frs


def simpleShardingScaling (nNodes, nShards, nUShard, sparsity, nEpochs, initBalance):

    assert nNodes % nShards == 0

    #no of nodes that repeats a shard
    nRep = int(nNodes / nShards)
    tVerifyMax = []
    tVerifyMedian = []
    tVote = []
    tUpdate = []
    for k in range(nShards):
        t1, t2, t3 = \
            frs.fullReplicationScaling(nNodes=nRep, nShards=1,  
                                       nUShard=nUShard, sparsity=sparsity, 
                                       nEpochs=nEpochs, initBalance=initBalance)
        tVerifyMax.append(t1)
        tVote.append(t2)
        tUpdate.append(t3)
    
    return tVerifyMax, tVote, tUpdate


def scaleSimpleSharding(nShards, redundancy, nUShard, sparsity, nEpochs, initBalance):
    nNodes = nShards * redundancy
    scale = nShards.size

    tVerify = np.zeros(scale)
    tUpdate = np.zeros(scale)
    tVote = np.zeros(scale)
    throughput = np.zeros(scale)

    for i in range(scale):
        tVerify[i], tVote[i], tUpdate[i] = \
            simpleShardingScaling(nNodes[i], nShards[i], nUShard, sparsity, nEpochs, initBalance)
        throughput[i] = nShards[i] / (tVerify[i] + tVote[i])

    # save the results
    result = {}
    result['verification time'] = tVerify
    result['voting time'] = tVote
    result['updating time'] = tUpdate
    result['throughput'] = throughput
    file = 'simple_sharding_redundancy_' + str(redundancy) +\
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