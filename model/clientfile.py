import hashlib
import numpy.random
import string
from model.constants import *


class ClientFile:
    def __init__(self, filename, filepath, leaf):
        self.filepath = filepath
        self.leaf = leaf
        self.real_size = len(self.read_file())
        self.hashed_file = hash_file(self.pad_data())
        self.padded_name = self.pad_filename(filename)


    def read_file(self):
        with open(self.filepath, 'rb') as file:
            file_data = file.read()
        return file_data

    def pad_filename(self, filename):
        if len(filename) > FILE_NAME_SIZE:
            raise Exception("file name is too big (bigger than 10 bytes)")
        elif len(filename) < FILE_NAME_SIZE:
            diff = FILE_NAME_SIZE - len(filename)
            numpy.random.seed(diff)
            pad = ''.join(numpy.random.choice(list(string.ascii_letters + string.digits + string.punctuation), size=diff))
            new_name = filename + pad
            return new_name
        else:
            return filename

    def pad_data(self):
        data = self.read_file()
        if self.real_size < FILE_SIZE:
            diff = FILE_SIZE - self.real_size
            numpy.random.seed(diff)
            pad = ''.join(numpy.random.choice(list(string.ascii_letters + string.digits + string.punctuation), size=diff))
            new_data = data + pad.encode()
            return new_data
        elif self.real_size > FILE_SIZE:
            raise Exception("file is too big (bigger than 64 bytes)")
        else:
            return data

def hash_file(file_data):
    sha1Hash = hashlib.sha1(file_data)
    sha1Hashed = sha1Hash.hexdigest()
    return sha1Hashed
