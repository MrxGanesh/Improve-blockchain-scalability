import numpy as np
import time


def createBlock(nUShard, sparsity, txCap):

    nTxs = int(nUShard * sparsity)
    assignUsers = np.random.permutation(nUShard)
    idxSenders = assignUsers[:nTxs]
    assignUsers = np.random.permutation(nUShard)
    idxRecivers = assignUsers[:nTxs]
    block = np.zeros((2, nUShard))
    block[0, idxSenders] = -txCap
    block[1, idxRecivers] = txCap
    return block


def verifyBlock(chain, block):
   
    start = time.time()
    bal = np.sum(chain, axis=0)
    newBal = bal + block
    ignore = (newBal > 0).all()
    t = time.time() - start
    return t


def existingBlockchainEpoch (nShards, nNodes, nUShard, sparsity, chainLength, initBalance):
    initChain = np.vstack([np.zeros((1,nUShard)), \
                            initBalance *np.ones((1,nUShard))])
    
    block = createBlock(nUShard, sparsity, initBalance/ chainLength/2)
    chain = np.vstack([initChain, np.repeat(block, chainLength, axis=0)])
    tVerify = np.zeros(nNodes)

    for n in range(nNodes):
        #measure verfication time of each nodes
        for k in range(nShards):
            tVerify[n] += verifyBlock(chain, block[0, :])
    
    return np.max(tVerify), np.median(tVerify), np.mean(tVerify)


def shardedBlockchainEpoch (nShards, nNodes, nUShard, sparsity, chainLength, initBalance):
    tVerifyMax = []
    tVerifyMedian = []
    tVerifyMean = []
    nRep = int(nNodes/nShards)

    for k in range(nShards):
        tMax, tMedian, tMean = \
            existingBlockchainEpoch(1, nRep, nUShard, sparsity,
                                chainLength, initBalance)
        
        tVerifyMax.append(tMax)
        tVerifyMedian.append(tMedian)
        tVerifyMean.append(tMean)

    return np.max(tVerifyMax), np.median(tVerifyMedian), np.mean(tVerifyMean)
