import hashlib
import binascii

class Merkle(object):
    def __init__(self, hash_type="sha256"):
        hash_type = hash_type.lower()
        if hash_type in ['sha256', 'sha512', 'md5']:
            self.hash_function = getattr(hashlib, hash_type)
        else:
            raise Exception('`hash_type` {} not supported'.format(hash_type))
        
        self.reset_merkle_tree()


    # convert the value to hexadecimal form
    def _to_hexadec(self, x):
        return x.hex()
    

    # reset merkle tree
    def reset_merkle_tree(self):
        self.leaves = list()
        self.levels = None
        self.is_ready = False
    

    # add leaf to merkle tree
    def add_leaf(self, values, hashed = False):
        self.is_ready = False
        #check single leaf
        if not isinstance(values, tuple) and not isinstance(values, list):
            values = [values]
        
        for value in values:
            if hashed:
                value = value.encode('utf-8')
                value = self.hash_function(value).hexdigest()
            value = bytearray.fromhex(value)
            self.leaves.append(value)


    # get leaf from merkle tree
    def get_leaf(self, index):
        return self._to_hexadec(self.leaves[index])
    

    # get leaf count from merkle tree
    def get_leaf_count(self):
        return len(self.leaves)

    # calculate next level for leaf addition to merkle tree
    def _calculate_next_level(self):
        single_leaf = None
        N = len(self.levels[0])  # number of leaves on the level
        if N % 2 == 1:  # if odd number of leaves on the level
            single_leaf = self.levels[0][-1]
            N -= 1

        new_level = []
        for l, r in zip(self.levels[0][0:N:2], self.levels[0][1:N:2]):
            new_level.append(self.hash_function(l+r).digest())
        if single_leaf is not None:
            new_level.append(single_leaf)
        self.levels = [new_level, ] + self.levels  # prepend new level


    # construct merkle tree
    def construct_tree(self):
        self.is_ready = False
        if self.get_leaf_count() > 0:
            self.levels = [self.leaves, ]
            while len(self.levels[0]) > 1:
                self._calculate_next_level()
        self.is_ready = True


    # get merkle root
    def get_merkle_root(self):
        if self.is_ready:
            if self.levels is not None:
                return self._to_hexadec(self.levels[0][0])
            else:
                return None
        else:
            return None