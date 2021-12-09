from communicator import Communicator
from shard import ShardNode
from transaction import Transaction
from block import Block
from plot import plot_network
from random import random, choice, sample
from copy import deepcopy
from time import time, sleep
import csv


class Validator(ShardNode):
    def __init__(s):
        s.communicator = Communicator()
        ShardNode.__init__(s, 1, s.communicator.comm.recv(source=0, tag=111))
        s.__transaction_per_block = 500               
        s.__transaction_max_value = 100
        s.__max_stake = 400000
        s.__shard_chain = [Block(None, None, time(), None, None)]   
        #plot_network(s._peers_in_shard, s.communicator.rank)          
    
    # get functions
    def get__validator_peers_in_shard(s):
        return s._peers_in_shard

    def get__all_val_ids(s):
        return s._all_ids

    def get__transaction_per_block(s):
        return s.__transaction_per_block

    @property
    def shard_chain(s):
        return s.__shard_chain


    ''' Each different shards (being the data layer) have validators, who validate transactions, proposes blocks
    and send it to the coord chain. This coord chain is the coordination layer that coordinates with n
    number of shards, collect the validated block and merges on main chain.
    
    Validator peers validates the transactions and the validators are generally individual or pooled together
    based on the value they stake on the coord chain'''

    def send_transactions_to_coord(s, nodes_in_shard, node_ids):
        shard_transactions = []
        for i in range(s.__transaction_per_block):
            sender_addr = choice(nodes_in_shard)
            receiver_addr = choice(list((set(node_ids) - {sender_addr})))
            value = choice(range(1, s.__transaction_max_value))
            # append transactions to be sent to a list
            shard_transactions.append(Transaction(sender_addr, receiver_addr, value))

        #send transactions to coord
        s.communicator.comm.send(shard_transactions, dest=0, tag=6)


    #create a subchain of valid transactions
    def create_subchain(s, nodes_in_shard, chain):
        subchain = []
        valid_transactionss = s.communicator.comm.recv(source=0, tag=7)  
        # print(len(valid_transactionss))
        value_in_block = 0
        for tx in valid_transactionss:
            value_in_block += tx.value
        while True:
            staker = choice(nodes_in_shard)
            stake = choice(list(range(value_in_block, s.__max_stake + 1)))
            block = Block(valid_transactionss, chain[-1].get__block_id(), time(), staker, stake)
            block.create_tree()
            subchain.append(block)
            if random() < 0.4:  
                break
        return subchain


    # check block processing time
    def check_block_time(s, subchain):
        early = min([block.get__time() for block in subchain])
        return next(block for block in subchain if block.get__time() == early)

    #approve blocks with valid transactions
    def approve_block(s, valid_block, nodes_in_shard):
        sleep(1)         
        hostility = random()
        if hostility < 0.34:
            s.__shard_chain.append(valid_block)
        else:
            value_in_block = 0
            for tran in valid_block.get__transactions():
                value_in_block += tran.value
            staker = choice(nodes_in_shard)
            stake = choice(list(range(value_in_block, s.__max_stake + 1)))
            block = Block(valid_block.get__transactions(), hash(s.__shard_chain[-1].get__block_id()), time(), staker, stake)
            block.create_tree()
            s.__shard_chain.append(block)
        #adiition of valid blocks to chain
        #print(s.__shard_chain)


    #the last one is checked as in every turn it chain changes
    def validate_chain(s, valid_block): 
        fraud = "None"
        
        #if the parent hash of the block is not same as previous block id, the validation is fradulant
        if s.__shard_chain[-1].get__parent() is not None: 
            if s.__shard_chain[-1].get__parent() != s.__shard_chain[-2].get__block_id():
                fraud = [s.__shard_chain[-1].get__staker(), s.__shard_chain[-1].get__stake()]
                del s.__shard_chain[-1]
                s.__shard_chain.append(valid_block) 
            
         # staker and staking of fraudulent validation is sent to coord for penalising
        s.communicator.comm.send(fraud, dest=0, tag=8) 


    # this deletes transactions from blocks (incase if needed to be when it is found fradulant)
    # k=1 -> one del at a time
    def remove_transactions(s):
        [index] = sample(range(len(s.__shard_chain[-1].get__transactions())), k=1)
        del s.__shard_chain[-1].get__transactions()[index]


    def recognized_remove(s, valid_block):
        del s.__shard_chain[-1]
        s.__shard_chain.append(valid_block)


    #change validator ids
    def change_validators_ids(s, change_ids):  
        new_val_peers_in_shard = deepcopy(s._peers_in_shard)
        for key, val in new_val_peers_in_shard.items():
            for change in change_ids:
                for index, vali in enumerate(val):
                    if vali == change[0]:
                        s._peers_in_shard[key][index] = change[1]

        for key in new_val_peers_in_shard:
            for change in change_ids:
                if key == change[0]:
                    s._peers_in_shard[change[1]] = s._peers_in_shard[change[0]]

        for change in change_ids:
            if change[0] in s._peers_in_shard.keys():
                s._peers_in_shard.pop(change[0])

        for change in change_ids:
            for index, node in enumerate(s._all_ids):
                if node == change[0]:
                    s._all_ids[index] = change[1]
