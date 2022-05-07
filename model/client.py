import socket

from model.bucket import Bucket
from model.clientfile import ClientFile
from model.serverfile import ServerFile
from cryptography.fernet import Fernet
import model
import os
import json
import string
import random
import math
from model.constants import *

class Client:
    def __init__(self, n):
        def write_key():
            key = Fernet.generate_key()
            with open("key.key", "wb") as key_file:
                key_file.write(key)

        if not os.path.exists("key.key"):
            print("create new key")
            write_key()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((SERVER_IP, SERVER_PORT))
        self.files_num = n  # => 2*n - 1 nodes in the tree, n leaves
        self.stash = {}
        self.all_files = {}
        self.generate_tree()

    def close_connection(self):
        self.client_socket.close()

    def get_path(self, leaf_idx):
        action = 'get_path '
        message = action.encode() + str(leaf_idx).encode()

        self.client_socket.send(message)
        leaf_path_encoded = self.client_socket.recv(MESSAGE_SIZE)
        leaf_path = decode_class(leaf_path_encoded)
        return leaf_path

    def try_upload_stash(self):
        if self.stash:
            for filename in self.stash.keys():
                leaf = self.get_random_leaf()
                client_file = self.all_files[filename]
                client_file.leaf = leaf

                leaf_path = self.get_path(leaf)

                buckets = []
                # decrypt the leaf path
                for encrypted_bucket in leaf_path:
                    # decrypt each bucket
                    bucket_str = self.decrypt_class(encode_class(encrypted_bucket))
                    bucket = str_to_class(bucket_str)
                    buckets.append(bucket)

                # enter the current file into the path instead of a dummy file

                # choose random bucket
                bucket_idx = random.randint(0, len(leaf_path) - 1)

                # check if the bucket is full
                if buckets[bucket_idx].num_real_files == NUM_OF_LOGS_IN_BUCKET * int(math.log(self.files_num, 2)):
                    print(f"{filename} stays in the stash")
                else:
                    idx = buckets[bucket_idx].num_real_files
                    buckets[bucket_idx].files[idx] = self.stash[filename]
                    buckets[bucket_idx].num_real_files += 1
                    # remove the item from the stash
                    del self.stash[filename]

                    # encrypt the whole path again
                    encrypted_buckets = []
                    for bucket in buckets:
                        encrypted_bucket = self.encrypt_class(bucket)
                        encrypted_buckets.append(decode_class(encrypted_bucket))

                    action = 'upload_file '
                    message = action.encode() + (str(leaf) + " ").encode() + encode_class(encrypted_buckets)

                    self.client_socket.send(message)
                    res = self.client_socket.recv(MESSAGE_SIZE).decode()
                    print(f"res: {res}, upload {filename} from the stash")

                    self.all_files[filename].leaf = leaf

    def upload_file(self, filepath, filename):
        leaf = self.get_random_leaf()

        client_file = ClientFile(filename, filepath, leaf)
        server_file = ServerFile(client_file.pad_filename(filename), client_file.pad_data().decode())

        if filename in self.all_files.keys():
            raise Exception("This file already exists")
        else:
            leaf_path = self.get_path(leaf)

            buckets = []
            # decrypt the leaf path
            for encrypted_bucket in leaf_path:
                # decrypt each bucket
                bucket_str = self.decrypt_class(encode_class(encrypted_bucket))
                bucket = str_to_class(bucket_str)
                buckets.append(bucket)

            # enter the current file into the path instead of a dummy file

            # choose random bucket
            bucket_idx = random.randint(0, len(leaf_path) - 1)

            # check if the bucket is full
            if buckets[bucket_idx].num_real_files == NUM_OF_LOGS_IN_BUCKET * int(math.log(self.files_num, 2)):
                if len(self.stash) == self.files_num:
                    raise Exception("too many files in the stash")
                else:
                    print(f"add {filename} to the stash")
                    client_file.leaf = -1
                    self.all_files[filename] = client_file
                    self.stash[filename] = server_file
            else:
                idx = buckets[bucket_idx].num_real_files
                buckets[bucket_idx].files[idx] = server_file
                buckets[bucket_idx].num_real_files += 1

                # encrypt the whole path again
                encrypted_buckets = []
                for bucket in buckets:
                    encrypted_bucket = self.encrypt_class(bucket)
                    encrypted_buckets.append(decode_class(encrypted_bucket))

                action = 'upload_file '
                message = action.encode() + (str(leaf) + " ").encode() + encode_class(encrypted_buckets)

                self.client_socket.send(message)
                res = self.client_socket.recv(MESSAGE_SIZE).decode()
                print(f"res: {res}, filename: {filename}")
                self.all_files[filename] = client_file

    def get_file(self, filename):
        if filename not in self.all_files.keys():
            return None, 0

        client_file = self.all_files[filename]
        leaf = client_file.leaf

        if leaf == -1:  # the file is in the stash
            file = self.stash[filename]
            return file, client_file.real_size

        action = "get_path "
        message = action.encode() + str(leaf).encode()

        self.client_socket.send(message)
        path_str = self.client_socket.recv(MESSAGE_SIZE).decode()
        path = str_to_class(path_str)

        new_path = []
        final_res = -1

        # decrypt the path and return the file
        for encrypted_bucket in path:
            # decrypt each bucket
            bucket_str = self.decrypt_class(encode_class(encrypted_bucket))
            bucket = str_to_class(bucket_str)

            new_encrypted_bucket = self.encrypt_class(bucket)
            new_path.append(new_encrypted_bucket.decode())

            for file_str in bucket.files:
                file = str_to_class(file_str)
                if type(file) is ServerFile:
                    if file.filename == client_file.padded_name:
                        final_res = file

        action = 'upload_file '
        message = action.encode() + (str(leaf) + " ").encode() + encode_class(new_path)

        self.client_socket.send(message)
        res = self.client_socket.recv(MESSAGE_SIZE).decode()
        print(f"res: {res}, filename: {filename}")

        if final_res == -1:
            return None
        elif self.check_file(filename, final_res.data):
            final_res.filename = filename
            return final_res, client_file.real_size
        else:
            raise Exception("Someone changed your file")

    def check_file(self, filename, new_file):
        file = self.all_files[filename]
        original_hash = file.hashed_file
        new_hash = model.clientfile.hash_file(new_file.encode())
        if original_hash == new_hash:
            return True
        return False

    def delete_file(self, filename):
        if filename not in self.all_files.keys():
            raise Exception("Not found!")
        f = self.all_files[filename]
        leaf = f.leaf

        # if the file in the stash
        if leaf == -1:  # the file is in the stash
            del self.stash[filename]
            del self.all_files[filename]
        else:
            action = "get_path "
            message = action.encode() + str(leaf).encode()

            self.client_socket.send(message)
            path_str = self.client_socket.recv(MESSAGE_SIZE).decode()
            path = str_to_class(path_str)

            new_buckets = []
            # decrypt the path
            for encrypted_bucket in path:
                # decrypt each bucket
                bucket_str = self.decrypt_class(encode_class(encrypted_bucket))
                bucket = str_to_class(bucket_str)

                for (i, file_str) in enumerate(bucket.files):
                    file = str_to_class(file_str)
                    if type(file) is ServerFile:
                        if file.filename == f.padded_name:
                            bucket.files[i] = generate_dummy()
                            bucket.num_real_files -= 1

                # encrypt the buckets again
                encrypted_new_bucket = self.encrypt_class(bucket)
                new_buckets.append(decode_class(encrypted_new_bucket))

            # upload the path
            action = 'upload_file '
            message = action.encode() + (str(leaf) + " ").encode() + encode_class(new_buckets)

            self.client_socket.send(message)
            res = self.client_socket.recv(MESSAGE_SIZE).decode()
            print(f"res: {res}, filename: {filename}")
            del self.all_files[filename]

    def get_random_leaf(self):
        def Diff(li1, li2):
            return list(set(li1) - set(li2))

        leaves = [file.leaf for file in self.all_files.values()]
        opt = list(range(self.files_num - 1, 2 * self.files_num - 1))
        final_opt = Diff(opt, leaves)

        if len(final_opt) == 0:
            raise Exception("too many files!")

        ran = random.choice(final_opt)
        return ran

    def generate_tree(self):
        """upload n dummy files"""

        def upload_dummy_bucket(dummy_bucket):
            action = "initial_upload "
            message = action.encode() + dummy_bucket

            self.client_socket.send(message)
            data = self.client_socket.recv(MESSAGE_SIZE).decode()
            print(data)

        def generate_bucket():
            bucket_files = []
            for i in range(NUM_OF_LOGS_IN_BUCKET * int(math.log(self.files_num, 2))):
                dummy_data = generate_dummy()
                bucket_files.append(dummy_data)

            bucket = Bucket(bucket_files, 0)
            bucket_encrypted = self.encrypt_class(bucket)
            return bucket_encrypted

        for i in range(int(2 * self.files_num - 1)):
            dummy_bucket = generate_bucket()
            upload_dummy_bucket(dummy_bucket)

    @staticmethod
    def encrypt_class(file):
        key = open("key.key", "rb").read()
        f = Fernet(key)

        encrypted_data = f.encrypt(encode_class(file))
        return encrypted_data

    @staticmethod
    def decrypt_class(encrypted_file):
        key = open("key.key", "rb").read()
        f = Fernet(key)

        # decrypt data
        decrypted_data = f.decrypt(encrypted_file)

        return decrypted_data.decode()

def generate_dummy():
    ran = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=DUMMY_SIZE))
    return ran

def encode_class(object):
    if type(object) is ServerFile:
        return str(object).encode()

    if type(object) is Bucket:
        return str(object).encode()

    json_string = json.dumps(object)
    return json_string.encode()


def decode_class(json_string):
    ob_str = json_string.decode()

    # Check if it is ServerFile object
    idx1 = ob_str.find('{filename}')
    idx2 = ob_str.find('{data}')

    if idx1 == 0 and idx2 != -1:
        filename = ob_str[10:idx2]
        data = ob_str[idx2 + 6:]
        return ServerFile(filename, data)

    # Check if it is Bucket object
    idx1 = ob_str.find('{real_files}{')

    if idx1 == 0:
        temp = ob_str[13:]
        i = temp.find('}')

        real_files_num = int(temp[:i])
        files = json.loads(temp[i + 1:])
        return Bucket(files, real_files_num)

    try:
        object = json.loads(ob_str)
    except:
        object = ob_str

    return object


def class_to_str(object):
    if type(object) is ServerFile or type(object) is Bucket:
        return str(object)

    json_string = json.dumps(object)
    return json_string


def str_to_class(json_string):
    ob_str = json_string

    idx1 = ob_str.find('{filename}')
    idx2 = ob_str.find('{data}')

    if idx1 == 0 and idx2 != -1:
        filename = ob_str[10:idx2]
        data = ob_str[idx2 + 6:]
        return ServerFile(filename, data)

    # Check if it is Bucket object
    idx1 = ob_str.find('{real_files}{')

    if idx1 == 0:
        temp = ob_str[13:]
        i = temp.find('}')

        real_files_num = int(temp[:i])
        files = json.loads(temp[i + 1:])
        return Bucket(files, real_files_num)

    try:
        object = json.loads(ob_str)
    except:
        object = ob_str

    return object
