from communicator import Communicator
from plot import plot_network
from random import choice, sample
from copy import deepcopy


class CoordChain:
    def __init__(s):
        s.communicator = Communicator()
        s.__validator_pool = 500
        s.__limit_validator_id=2000
        s.__notary_pool = 10000
        s.__limit_notary_id = 20000
        s.__nodes_per_coord = 200
        s.__validator_per_rank = 150        
        s.__notarry_per_rank = 20
        s.__coord_peers = 3
        s.__num_val_migrates = 1
        s.__num_notarry_migrates = 1
        s.__start_value = 100000
        s.__validator_acc_info = []
        s.__notary_acc_info = []
        s.__peers_in_coord = {}

    def get__peers_in_coord(s):
        return s.__peers_in_coord
    
    def get__validator_per_rank(s):
        return s.__validator_per_rank

    def boot_coord(s):
        coord_node_ids = sample(range(s.__validator_pool, 2 * s.__validator_pool), s.__nodes_per_coord)
        for node in coord_node_ids:
            s.__peers_in_coord[node] = sample((set(coord_node_ids)-{node}), s.__coord_peers)
        s.create_validator_acc_info()
        s.create_notary_acc_info()
        for rank in range(1, s.communicator.nbprocs):
            s.communicator.comm.send(s.__validator_per_rank, dest=rank, tag=111)
            s.communicator.comm.send(s.__notarry_per_rank, dest=rank, tag=222)
            s.communicator.comm.send([i["id"] for i in s.__validator_acc_info], dest=rank, tag=1)
            s.communicator.comm.send([i["id"] for i in s.__notary_acc_info], dest=rank, tag=2)

        plot_network(s.__peers_in_coord, s.communicator.rank)


    def create_validator_acc_info(s):
        for rank in range(1, s.communicator.nbprocs):
            interval = range((rank+1)*s.__validator_pool, (rank+2)*s.__validator_pool)
            for id_node in sample(interval, s.__validator_per_rank):
                account = {"id": id_node,
                           "value": s.__start_value,
                           "shard": rank}
                s.__validator_acc_info.append(account)

    def create_notary_acc_info(s):
        for rank in range(1, s.communicator.nbprocs):
            interval = range((rank+1)*s.__notary_pool, (rank+2)*s.__notary_pool)
            for id_node in sample(interval, s.__notarry_per_rank):
                account = {"id": id_node,
                           "value": s.__start_value,
                           "shard": rank}
                s.__notary_acc_info.append(account)


    def choose_rotated_notarries(s):
        old_rotated_nodes = []
        for rank in range(1, s.communicator.nbprocs):
            new_rotated_nodes = sample([(index, acc['id']) for index, acc in enumerate(s.__notary_acc_info) if acc["shard"] == rank], s.__num_notarry_migrates)
            if old_rotated_nodes:
                for node in old_rotated_nodes:
                    s.__notary_acc_info[node[0]]["shard"] += 1
            old_rotated_nodes = new_rotated_nodes
            if rank == (s.communicator.nbprocs - 1):
                for node in old_rotated_nodes:
                    s.__notary_acc_info[node[0]]["shard"] = 1
            s.communicator.comm.send([node[1] for node in new_rotated_nodes], dest=rank, tag=3)

    def choose_rotated_validators(s):
        old_rotated_nodes = []
        for rank in range(1, s.communicator.nbprocs): 
            for index, acc in enumerate(s.__validator_acc_info):
                if acc["shard"] == rank:
                    new_rotated_nodes = sample([(index, acc['id'])], s.__num_val_migrates)
            # new_rotated_nodes = sample([(index, acc['id']) for index, acc in enumerate(s.__validator_acc_info) if acc["shard"] == rank], s.__num_val_migrates)
            if old_rotated_nodes:
                for node in old_rotated_nodes:
                    s.__validator_acc_info[node[0]]["shard"] += 1
            old_rotated_nodes = new_rotated_nodes
            if rank == (s.communicator.nbprocs - 1):
                for node in old_rotated_nodes:
                    s.__validator_acc_info[node[0]]["shard"] = 1
            for node in new_rotated_nodes:
                s.communicator.comm.send([node[1]], dest=rank, tag=4)
            #s.communicator.comm.send([node[1] for node in new_rotated_nodes], dest=rank, tag=4) # wyjdzie jedna lista nodow

    def transfer_account_balance(s, transactions):
        transactions_removed = deepcopy(transactions)
        for index, shard_trans in enumerate(transactions_removed):
            indexes = []
            for ind, trans in enumerate(shard_trans):
                '''
                for ind, acc in enumerate(s.__validator_acc_info):
                    if acc['id'] == trans.sender_addr:
                        sacc = (ind,acc)
                    
                    if acc['id'] == trans.receiver_addr:
                        racc = (ind,acc)
                '''
                sacc = next((ind, acc) for ind, acc in enumerate(s.__validator_acc_info) if acc["id"] == trans.sender_addr)
                racc = next((ind, acc) for ind, acc in enumerate(s.__validator_acc_info) if acc["id"] == trans.receiver_addr)
                if trans.value <= sacc[1]["value"]:
                    s.__validator_acc_info[sacc[0]]["value"] -= trans.value
                    s.__validator_acc_info[racc[0]]["value"] += trans.value
                else:
                    indexes.append(ind)
            for i in indexes[::-1]:
                del transactions[index][i]
        return transactions

    def resend_transaction(s, transactions): 
        send_transactions = deepcopy(transactions)
        for index, shard_trans in enumerate(transactions):
            for tran in shard_trans:
                receiving_shard = next(
                    acc["shard"] for acc in s.__validator_acc_info if acc["id"] == tran.receiver_addr)
                if receiving_shard != index + 1:
                    send_transactions[receiving_shard - 1].append(tran)
        for index, shard_trans in enumerate(send_transactions):
            s.communicator.comm.send(shard_trans, dest=index + 1, tag=7)

    def burn_stake_bad_commit_availability(s, tag):
        for rank in range(1, s.communicator.nbprocs):
            acc_burned = s.communicator.comm.recv(source=rank, tag=tag)
            if acc_burned != "None":
                for index, acc in enumerate(s.__validator_acc_info):
                    if acc_burned[0] == acc['id']:
                        s.__validator_acc_info[index]['value'] -= acc_burned[1]

    def burn_stake_notarry(s):
        for rank in range(1, s.communicator.nbprocs):
            acc_burned = s.communicator.comm.recv(source=rank, tag=9)
            if acc_burned != "None":
                for index, acc in enumerate(s.__notary_acc_info):
                    if acc_burned[0] == acc['id']:
                        s.__notary_acc_info[index]['value'] -= acc_burned[1]


    # get rid of indebted validators from the shard
    def remove_indebted_validators(s):
        list_id = [acc['id'] for acc in s.__validator_acc_info]
        change_ids = []
        for index, acc in enumerate(s.__validator_acc_info):
            if acc['value'] < 0:
                interval = range(s.__limit_validator_id, ((s.communicator.nbprocs + 1) * s.__validator_pool))
                old_id = acc['id']
                new_id = choice(list(set(interval) - {acc['id']} - set(list_id)))
                s.__validator_acc_info[index]['id'] = new_id
                s.__validator_acc_info[index]['value'] = s.__start_value
                change_ids.append((old_id, new_id))
                list_id[index] = new_id
        for i in range(1, s.communicator.nbprocs):
            s.communicator.comm.send(change_ids, dest=i, tag=11)

    #get rid of indebted notarries from the shard
    def remove_indebted_notarries(s):
        list_id = [acc['id'] for acc in s.__notary_acc_info]
        change_ids = []
        for index, acc in enumerate(s.__notary_acc_info):
            if acc['value'] < 0:
                interval = range(s.__limit_notary_id, ((s.communicator.nbprocs + 1) * s.__notary_pool))
                old_id = acc['id']
                new_id = choice(list(set(interval) - {acc['id']} - set(list_id)))
                s.__notary_acc_info[index]['id'] = new_id
                s.__notary_acc_info[index]['value'] = s.__start_value
                change_ids.append((old_id, new_id))
                list_id[index] = new_id
        for i in range(1, s.communicator.nbprocs):
            s.communicator.comm.send(change_ids, dest=i, tag=12)





























        #
        #
        #
        #
        #
        #
        #
        # #Dodaje wszystkim po 20 poniewaz beda palone stawki przy tworzeniu zlych BLOKÓW i nie chce zeby ludzie sie wykosztowali
        # for account in s.val_accounts_info:
        #     account["value"] += s.config.added_paid_every_tick

