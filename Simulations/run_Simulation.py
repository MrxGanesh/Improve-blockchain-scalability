import full_Replication as fr
import simple_Sharding as ss
import time

# declare simulation parameter
nNodes = 15
nShards = 5
nUShard = 2000
sparsity = 0.2
nEpochs = 100
initBalance = 100

# Run simulation of full replication blockchain
start = time.time()
out_fr = fr.fullReplication(nNodes, nShards, nUShard, sparsity, nEpochs, initBalance)

print()
print("Full Replication:", round(time.time() - start, 5), "s")
fr.plots(out_fr[-1])


# Run simulation of full replication blockchain
start = time.time()
out_ss = ss.simpleSharding(nNodes, nShards, nUShard, sparsity, nEpochs, initBalance)

print()
print("Simple Sharding: ", round(time.time() - start, 5), "s")
ss.plots(out_ss[-1])