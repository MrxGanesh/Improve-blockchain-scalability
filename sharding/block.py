from merkle import Merkle

class Block:
    def __init__(self, transactions, parent, time, staker, stake):
        self.__transactions = transactions
        self.__time = time
        self.__parent = parent
        self.__staker = staker
        self.__stake = stake
        self.__blockchain = []
        self.__merkletree = Merkle(hash_type="md5")
        self.__block_id = 0

    ''' Get functions '''
    def get__parent(self):
        return self.__parent

    def get__block_id(self):
        return self.__block_id

    def get__staker(self):
        return self.__staker

    def get__stake(self):
        return self.__stake

    def get__transactions(self):
        return self.__transactions

    def get__time(self):
        return self.__time

    def get__merkletree(self):
        return self.__merkletree

    def create_tree(self):
        if self.__transactions is not None:
            for transaction in self.__transactions:
                tx = f"{transaction.transaction_id} {transaction.sender_addr} {transaction.receiver_addr} {transaction.value}"
                self.__merkletree.add_leaf(tx, True)

        self.__merkletree.construct_tree()
        self.__block_id = hash((self.__merkletree.get_merkle_root(), self.__time, self.__parent))
        
