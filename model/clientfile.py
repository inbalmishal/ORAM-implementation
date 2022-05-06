import hashlib
import numpy.random
import string
FILE_SIZE = 512

class ClientFile:
    def __init__(self, filepath, leaf, stash_idx=-1):
        self.filepath = filepath
        self.leaf = leaf
        self.real_size = len(self.read_file())
        self.hashed_file = hash_file(self.padding())
        self.stash_idx = stash_idx


    def read_file(self):
        with open(self.filepath, 'rb') as file:
            file_data = file.read()
        return file_data

    def padding(self):
        data = self.read_file()
        if self.real_size < FILE_SIZE:
            diff = FILE_SIZE - self.real_size
            numpy.random.seed(diff)
            pad = ''.join(numpy.random.choice(list(string.ascii_letters + string.digits + string.punctuation), size=diff))
            new_data = data + pad.encode()
            return new_data
        elif self.real_size > FILE_SIZE:
            raise Exception("file is too big (bigger than 1024 bytes)")
        else:
            return data

def hash_file(file_data):
    sha1Hash = hashlib.sha1(file_data)
    sha1Hashed = sha1Hash.hexdigest()
    return sha1Hashed
