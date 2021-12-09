from random import randrange


class Transaction:
    def __init__(self, sender_addr, receiver_addr, value):  #to id_bedzie problem
        self.transaction_id = randrange(10**30, 10**31)
        self.sender_addr = sender_addr
        self.receiver_addr = receiver_addr
        self.value = value
