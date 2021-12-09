from communicator import Communicator
from block import Block
from random import choice, random, sample
from copy import deepcopy
from time import time
from shard import ShardNode


class Nottaries(ShardNode):
    def __init__(s):
        s.communicator = Communicator()
        ShardNode.__init__(s, 2, s.communicator.comm.recv(source=0, tag=222))
        s.__available_stake = 400


    # check if the transaction data is available in block
    # block without transaction data deosn't need to be validated
    def check_block_data_availability(s, block_to_be_checked): # tu bedzie sprawdzana transakcja
        test_block = Block(block_to_be_checked.get__transactions(), None, time(), None, None)
        test_block.create_tree()
        test_num_leaves = test_block.get__merkletree().get_leaf_count()
        num_leaves = block_to_be_checked.get__merkletree().get_leaf_count()
        staker = choice(list(s._peers_in_shard))
        message = {'notary_staker' : staker}
        message['notary_stake'] = s.__available_stake
        hostility = random()
        if hostility < 0.34:
            if test_num_leaves != num_leaves:
                message['verdict'] = 'incomplete'
            else:
                message['verdict'] = 'complete'
        else:
            if test_num_leaves != num_leaves:
                message['verdict'] = 'complete'
            else:
                message['verdict'] = 'incomplete'
        return message


    # validate the challenge
    def validate_block_challenge(s, message, block_to_be_checked):
        fraud = 'None'
        test_block = Block(block_to_be_checked.get__transactions(), None, time(), None, None)
        test_block.create_tree()
        test_num_leaves = test_block.get__merkletree().get_leaf_count()
        num_leaves = block_to_be_checked.get__merkletree().get_leaf_count()
        if test_num_leaves != num_leaves:
            if message['verdict'] == 'incomplete':
                s.communicator.comm.send(fraud, dest=0, tag=9)
                s.communicator.comm.send([block_to_be_checked.get__staker(), block_to_be_checked.get__stake()], dest=0, tag=10)
                return True
            else:
                fraud = [message['notary_staker'], message['notary_stake']]
                s.communicator.comm.send(fraud, dest=0, tag=9)
                s.communicator.comm.send([block_to_be_checked.get__staker(), block_to_be_checked.get__stake()], dest=0, tag=10)
                return True
        else:
            if message['verdict'] == 'complete':
                s.communicator.comm.send(fraud, dest=0, tag=9)
                s.communicator.comm.send('None', dest=0, tag=10)
                return False
            else:
                fraud = [message['notary_staker'], message['notary_stake']]
                s.communicator.comm.send(fraud, dest=0, tag=9)
                s.communicator.comm.send('None', dest=0, tag=10)
                return False
    
    #Change notary ids
    def change_notarries_ids(s, change_ids):  
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

