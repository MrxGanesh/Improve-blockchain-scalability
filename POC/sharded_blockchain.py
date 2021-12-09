import numpy as np
import pickle
import time
import matplotlib.pyplot as plt

from existing_blockchain import existingBlockchain

def shardedBlockchain(nNodes, nShards, nUShard, sparsity, nEpochs, initBalance):
    
    # nNodes must be a multiple of nShards
    assert nNodes % nShards == 0

    # no of nodes that repeats a shard
    nRep = int(nNodes / nShards)
    tVerify = []
    tVote = []
    tUpdate = []
    for k in range(1,nShards+1):
        print()
        print("Processing Shard:", str(k))
        print()
        tvr, tvo, tup, _ = existingBlockchain(nNodes=nRep, nShards=1, nUShard=nUShard,sparsity=sparsity,  
                                           nEpochs=nEpochs, initBalance=initBalance)
        
        tVerify.append(tvr)
        tVote.append(tvo)
        tUpdate.append(tup)

    '''
    the maximum verification voting and updating time should be considered across all shards
    '''

    tVerify = np.max(tVerify, axis=0)   # max of each column
    tVote = np.max(tVote, axis=0)   
    tUpdate = np.max(tUpdate, axis=0)

    result = {}
    result['verification time'] = tVerify
    result['voting time'] = tVote
    result['updating time'] = tUpdate
    file = 'sharded_blockchain_N_' + str(nNodes) + '_K_' +\
               str(nShards) + '_M_' + str(nUShard) + '.pickle'
    with open(file, 'wb') as handle:
        pickle.dump(result, handle)

    return tVerify, tVote, tUpdate, file

def plots(file):
    print(file)
    with open(file, 'rb') as handle:
        result = pickle.load(handle)
    for key in result.keys():
        if not key == 'updating time':
            plt.plot(range(len(result[key])), result[key] * 1000, label=key)
    plt.xlabel('Epoch')
    plt.ylabel('Time (ms)')
    plt.grid()
    plt.legend(loc='best')
    plt.title('Sharded Blockchain')
    plt.xlim((0, None))
    plt.ylim((0, None))
    plt.tight_layout()
    plt.savefig('shardedblockchain.png')

# unitTests()