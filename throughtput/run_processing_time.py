import numpy as np
import pickle
import time


def runProcessing(density='dense', nShards=list(range(5, 51, 5)),
            nEpochs=list(range(100, 1001, 100)),
            redundancy=3, nUShard=2000, sparsity=0.5,
            initBal=1000, nRuns=500):
    if density == 'dense':
        import processing_time as pt
    
    nNodesRange = [k * redundancy for k in nShards]

    nType = ['full_replication', 'simple_sharding']
    metrices = ['tVerMax', 'tVerMedian', 'tVerMean']
    data = {}
    for s in nType:
        data[s] = {}
        for m in metrices:
            data[s][m] = np.zeros((len(nShards), len(nEpochs)))

    for i in range(len(nShards)):
        numShards = nShards[i]
        numNodes = nNodesRange[i]
        for j in range(len(nEpochs)):
            numEpochs = nEpochs[j]
            print('Now running K=' + str(numShards) + ' Epoch=' +
                  str(numEpochs))
            for n in range(nRuns):
                print('**--FR--**')
                tVerMax, tVerMedian, tVerMean = \
                    pt.fullReplicationEpoch(numShards, numNodes, nUShard, sparsity,
                               numEpochs, initBal)
                data['full_replication']['tVerMax'][i, j] += tVerMax / nRuns
                data['full_replication']['tVerMedian'][i, j] += \
                    tVerMedian / nRuns
                data['full_replication']['tVerMean'][i, j] += \
                    tVerMean / nRuns

                print('**--SS--**')
                tVerMax, tVerMedian, tVerMean =\
                    pt.simpleShardingEpoch(numShards, numNodes, nUShard, sparsity,
                               numEpochs, initBal)
                data['simple_sharding']['tVerMax'][i, j] += tVerMax / nRuns
                data['simple_sharding']['tVerMedian'][i, j] += \
                    tVerMedian / nRuns
                data['simple_sharding']['tVerMean'][i, j] += \
                    tVerMean / nRuns


        result = {}
        result['nShards'] = nShards
        result['nNodes'] = nNodesRange
        result['nEpochs'] = nEpochs
        result['data'] = data
        file = 'all_nType_' + density + '_' + \
                   'K=' + str(numShards) + '_' \
                   'M=' + str(nUShard) + '_' + \
                   'r=' + str(redundancy) + '_' + \
                   'epoch=' + str(nEpochs[0]) + ',' + \
                   str(nEpochs[-1]) + ']_' + \
                   's=' + str(sparsity) + '_' + \
                   str(int(time.time() / 1000)) + '.pickle'
        with open(file, 'wb') as handle:
            pickle.dump(result, handle)
    result = {}
    result['nShards'] = nShards
    result['nNodes'] = nNodesRange
    result['nEpochs'] = nEpochs
    result['data'] = data
    file = 'all_nType_' + density + '_' + \
               'K=[' + str(nShards[0]) + ',' + \
               str(nShards[-1]) + ']_' + \
               'M=' + str(nUShard) + '_' + \
               'r=' + str(redundancy) + '_' + \
               'epoch=' + str(nEpochs[0]) + ',' + \
               str(nEpochs[-1]) + ']_' + \
               's=' + str(sparsity) + '_' + \
               str(int(time.time() / 1000)) + '.pickle'
    with open(file, 'wb') as handle:
        pickle.dump(result, handle)
    print('Completed. Data saved at: ', file)
    return file


density = 'dense'
sparsity = 0.5
# nShards = list(range(5, 51, 5))
nShards = [5, 50]
nEpochs = list(range(100, 1001, 100))
# nEpochs = [1000]
nUShard = 2000
nRuns = 5
redundancy = 3
file = runProcessing(density=density, nShards=nShards,
                   nEpochs=nEpochs, nUShard=nUShard,
                   redundancy=redundancy,
                   sparsity=sparsity, nRuns=nRuns)
