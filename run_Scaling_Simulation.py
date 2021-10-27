import time
import numpy as np
import full_Replication_Scaling as frs
import simple_Sharding_Scaling as sss

nShards = np.arange(10, 105, 10)
redundancy = 3
nUShard = 50
sparsity = 0.2
nEpochs = 100
initBalance = 100

# Run full replication
start = time.time()
out_frs = frs.scaleFullReplication(nShards, redundancy, nUShard, sparsity, nEpochs, initBalance)
print("Full Replication: ", round(time.time() - start,5), 's')
frs.plots(out_frs[-1],nShards * redundancy)


# Run simple sharding
start = time.time()
out_sss =sss.scaleSimpleSharding(nShards, redundancy, nUShard, sparsity, nEpochs, initBalance)
print("Simple Sharding: ", round(time.time() - start,5), 's')
sss.plots(out_sss[-1],nShards * redundancy)