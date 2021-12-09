import existing_blockchain as eb
import sharded_blockchain as sb
import time

# declare simulation parameter
nNodes = 15
nShards = 5
nUShard = 2000
sparsity = 0.5
nEpochs = 100
initBalance = 100

'''
# Run simulation of full replication blockchain
start = time.time()
out_eb = eb.existingBlockchain(nNodes, nShards, nUShard, sparsity, nEpochs, initBalance)

print()
print("Exisiting Blockchain:", round(time.time() - start, 5), "s")
eb.plots(out_eb[-1])
'''

# Run simulation of full replication blockchain
start = time.time()
out_sb = sb.shardedBlockchain(nNodes, nShards, nUShard, sparsity, nEpochs, initBalance)

print()
print("Sharded Blockchain: ", round(time.time() - start, 5), "s")
sb.plots(out_sb[-1])