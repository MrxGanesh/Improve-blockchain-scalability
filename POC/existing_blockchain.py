import numpy as np
import pickle
import time
import matplotlib.pyplot as plt


def InitiateChain(nShards, nUShard, initBalance):

    chain = np.zeros([2, nUShard])
    chain[1,:] = initBalance   # 0th+1st row has a gensis block
    chains = [np.copy(chain) for i in range(nShards)]
    return chains


def createBlock(nUShard, sparsity, txCap):
    
    '''
    sparsity is the fraction of transactions per block in each
    shard made by no of users. nUShard * sparsity gives no 
    of transactions per block

    Every user can send and receive money
    '''
    nTx = int(nUShard * sparsity)
    assignUsers = np.random.permutation(nUShard)
    idxSenders = assignUsers[:nTx]
    assignUsers = np.random.permutation(nUShard)
    idxReceivers = assignUsers[:nTx]
    block = np.zeros((2,nUShard))
    block[0, idxSenders] = -txCap    # value all the nUshard users will send (non positive)
    block[1, idxReceivers] = txCap   # value all the nUshard users will receiver (positive)
    return block


def blockGeneration(nShards, nUShard, sparsity, txCap):

    '''
    Generate blocks with transactions
    '''
    blocks = [createBlock(nUShard,sparsity, txCap) for n in range(nShards)]
    return blocks


def verifyTamper(opinion, n):
    '''
    decide if nodes tampers the opinion. Assume all are honest
    '''
    opinion = True
    return opinion


def verifyBlock(chain, block):
    '''
    Verify block based on the balance against its chain
    '''
    balance = np.sum(chain,axis=0)
    return (balance + block[0] >=0).all()


def verifyNode(chains, blocks, n):
    '''
    Verify all blocks at any node n based on the balance against its chain   
    '''
    nShards = len(chains)
    opinion = np.zeros(nShards)
    for k in range(nShards):
        opinion[k] = verifyBlock(chains[k], blocks[k])
    verifyTamper(opinion, n)
    return opinion


def voting(opinions):
    '''
    voting is consensus for all the nShards blocks
    '''
    nNodes, _ = opinions.shape
    votes = np.sum(opinions, axis=0)
    consensus = votes > nNodes/2        # pass the block if the vote is > 50%
    return consensus


def updateChain(chains, blocks, consensus):
    for i in range(len(chains)):
        chains[i] = np.vstack([chains[i], blocks[i] * consensus[i]])
    
    return chains 


def simulateEpoch(chains, tVerify, tUpdate, tVote, nNodes, nShards, nUShard, sparsity, idxEpoch, txCap):
    '''
    simulate and measure verification, voting(consensus) and updating of blocks in each epoch
    '''

    #generate blocks
    blocks = blockGeneration(nShards, nUShard, sparsity, txCap)

    opinions = np.zeros((nNodes, nShards))
    tVerification = []
    for n in range(nNodes):
        tStart = time.time()
        opinions[n, :] = verifyNode(chains, blocks, n)
        tPassed = time.time() - tStart
        tVerification.append(tPassed)
    
    # record the max verification time accross all nodes as epoch's verification team
    tVerify[idxEpoch] = np.max(tVerification)

    # voting consensus
    tStart = time.time()
    consensus = voting(opinions)
    tVote[idxEpoch] = time.time() - tStart

    # updating blocks
    tStart = time.time()
    updateChain(chains, blocks, consensus)
    tUpdate[idxEpoch] = time.time() - tStart

    return np.max(tVerification), np.median(tVerification), tVote[idxEpoch], \
        tUpdate[idxEpoch]


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
    plt.title('Existing Blockchain')
    plt.xlim((0, None))
    plt.ylim((0, None))
    plt.tight_layout()
    plt.show()


def existingBlockchain(nNodes, nShards, nUShard, sparsity, nEpochs, initBalance):

    #initiate blockchain system
    chains = InitiateChain(nShards, nUShard, initBalance)
    tVerify = np.zeros(nEpochs)
    tVote = np.zeros(nEpochs)
    tUpdate = np.zeros(nEpochs)

    ''' 
    the transaction value is capped with enough avalue to all users 
    to have enough value to transact in every epoch. After many 
    epochs, user balance will reduce and thus senders with 0 value to
    transact, will be rejected and chain is stuck during simulation
    '''

    txCap = initBalance/nEpochs

    #run the system
    for idxEpoch in range(nEpochs):
        print("Processing Epoch:", idxEpoch)
        simulateEpoch(chains, tVerify, tUpdate, tVote, nNodes, nShards, nUShard, sparsity, idxEpoch, txCap)

    #save results
    result = {}
    result['verfication time'] = tVerify
    result['voting time'] = tVote
    result['updating time'] = tUpdate

    file = 'existing_blockhain_N_' + str(nNodes) + '_K_' +\
            str(nShards) + '_M_' + str(nUShard) + '.pickle'
    
    with open(file, 'wb') as handle:
        pickle.dump(result, handle)
    
    return tVerify, tVote, tUpdate, file
