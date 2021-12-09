from coord import CoordChain
from validators import Validator
from notarries import Nottaries
from communicator import Communicator
from plot import plot_network
from plot import plot_transaction_shard
from time import time
import csv


class Main:
    def __init__(s):
        s.__sim_ep = 25

    def get__sim_ep(s):
        return s.__sim_ep


if __name__ == "__main__":
    main = Main()
    communicator = Communicator()


    if communicator.comm.rank == 0:
        coord = CoordChain()
        coord.boot_coord()
    #communicator.comm.barrier()
    if communicator.comm.rank != 0:
        validators = Validator()
        notarries = Nottaries()
    if communicator.rank == 1:
        time_list = [0]
        num_transactions = [0]
        gg = True
    for tick in range(main.get__sim_ep()):
        if communicator.rank == 0:
            if tick % 2 == 0:
               coord.choose_rotated_notarries()
               #print("choose notarries")
            if tick % 5 == 0:
                coord.choose_rotated_validators()
                #print("choose validators")

        # communicator.comm.barrier()

        if communicator.rank != 0:
            if tick % 2  == 0:
                notarries.shuffle_shard_nodes(communicator.comm.recv(source=0, tag=3))
                #print("shuffle notaries")
            if tick % 5 == 0:
                validators.shuffle_shard_nodes(communicator.comm.recv(source=0, tag=4))
                #print("shuffle validators")
            validators.send_transactions_to_coord(list(validators.get__validator_peers_in_shard()), validators.get__all_val_ids())
        # communicator.comm.barrier()

        if communicator.rank == 0:
            transaction_received = []
            for rank in range(1, communicator.nbprocs):
                transaction_received.append(communicator.comm.recv(source=rank, tag=6))
            transaction_after_del = coord.transfer_account_balance(transaction_received)
            coord.resend_transaction(transaction_after_del)
        # communicator.comm.barrier()

        if communicator.rank != 0:
            subchain = validators.create_subchain(validators.get__all_val_ids(), validators.shard_chain)
            valid_block = validators.check_block_time(subchain)
            validators.approve_block(valid_block, validators.get__all_val_ids())
            validators.validate_chain(valid_block)
            validators.remove_transactions()
            message = notarries.check_block_data_availability(validators.shard_chain[-1])
            verdict = notarries.validate_block_challenge(message, validators.shard_chain[-1])
            if verdict:
                validators.recognized_remove(valid_block)
        # communicator.comm.barrier()

        if communicator.rank == 0:
            coord.burn_stake_bad_commit_availability(8)
            coord.burn_stake_notarry()
            coord.burn_stake_bad_commit_availability(10)
            coord.remove_indebted_validators()
            coord.remove_indebted_notarries()
        # communicator.comm.barrier()

        if communicator.rank != 0:
            validators.change_validators_ids(communicator.comm.recv(source=0, tag=11))
            notarries.change_notarries_ids(communicator.comm.recv(source=0, tag=12))
            if communicator.rank == 1:
                if gg == True:
                    start_time = time()
                    gg = False
                time_list.append(time()-start_time)
                num_transactions.append(tick*validators.get__transaction_per_block()*communicator.nbprocs)
        # communicator.comm.barrier()

    if communicator.rank == 0:
        pass
        # plot_network(coord.get__peers_in_coord(), communicator.rank)
    else:
        plot_network(validators.get__validator_peers_in_shard(), communicator.rank)
        if communicator.rank == 1:
            with open('./sharding/tps.csv', 'a') as fd:
                writer = csv.writer(fd)
                for i in range(len(time_list)):
                    writer.writerow([time_list[i], num_transactions[i]])
            print('--------------------------------------------------')
            print()
            print("No of Shards: "+ str(communicator.nbprocs))
            print("No of transactions: " + str(num_transactions[-1]))
            print("Node Processing time: " + str(round(time_list[-1],2)) + " secs")
            print() 
            print("throughput:" + str(num_transactions[-1]//time_list[-1]) + " tps")
            print('--------------------------------------------------')
            plot_transaction_shard(time_list,num_transactions)
            #print(validators.shard_chain)

            '''    
            for i in range (len(validators.shard_chain)):
                blockd = []
                blockd.append(validators.shard_chain[i].get__block_id())
            print(blockd)
            '''