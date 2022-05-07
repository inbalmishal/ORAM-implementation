import socket
import select
import json
from constants import SERVER_IP, SERVER_PORT, MESSAGE_SIZE



def class_to_str(object):
    json_string = json.dumps(object)
    return json_string


def str_to_class(json_string):
    object = json.loads(json_string)
    return object

class Server:
    def __init__(self):
        self.all_data = {}

    def print_data(self):
        print("----------------------------------------")
        for (i, client_data) in enumerate(self.all_data):
            print(f"{i}: {client_data}\n")
        print("----------------------------------------")

    def print_client_sockets(self, client_sockets):
        for c in client_sockets:
            print("\t", c.getpeername())

    def start_serv(self):
        def initial_upload():
            self.all_data[current_socket.getpeername()].append(content)
            messages_to_send.append((current_socket, f"Action succeeded - "
                                                     f"{len(self.all_data[current_socket.getpeername()])}"))

        def get_path():
            leaf_idx = int(content)
            leaf_path = []
            i = leaf_idx

            while i >= 0:
                leaf_path.append(self.all_data[current_socket.getpeername()][i])
                i = (i - 1) // 2

            # send the leaf path
            messages_to_send.append((current_socket, class_to_str(leaf_path)))

        def upload_file():
            leaf_str, new_path_str = content.split(" ", 1)
            new_path = str_to_class(new_path_str)

            # get the wanted leaf
            leaf_idx = int(leaf_str)
            i = leaf_idx

            for j in range(len(new_path)):
                self.all_data[current_socket.getpeername()][i] = new_path[j]
                i = (i - 1) // 2
                j += 1

            # send success message
            messages_to_send.append((current_socket, "Action succeeded"))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serv:
            print("Setting up server...")
            serv.bind((SERVER_IP, SERVER_PORT))
            serv.listen(5)

            print("Listening for clients...")
            client_sockets = []
            messages_to_send = []

            while True:
                rlist, wlist, xlist = select.select([serv] + client_sockets, client_sockets, [])

                for current_socket in rlist:
                    if current_socket is serv:  # new client
                        connection, client_address = current_socket.accept()
                        print("New client joined!", client_address)

                        # add the client to "all_data" dict
                        self.all_data[connection.getpeername()] = []
                        client_sockets.append(connection)
                        self.print_client_sockets(client_sockets)

                    else:  # old client
                        try:
                            data = current_socket.recv(MESSAGE_SIZE).decode()
                        except Exception as e:
                            messages_to_send.append((current_socket, f"Action Failed1 + {e}"))

                        if data == "":  # close connection
                            print("Connection closed", )
                            client_sockets.remove(current_socket)
                            current_socket.close()
                            self.print_client_sockets(client_sockets)

                            # download the current data
                            # with open('all_data.json', 'w') as f:
                            #     json.dump(self.all_data, f)

                        else:  # data
                            action, content = data.split(" ", 1)

                            try:
                                if action == "initial_upload":
                                    messages_to_send.append((current_socket, "Action Excepted\n"))
                                    initial_upload()

                                elif action == "get_path":
                                    get_path()

                                elif action == "upload_file":
                                    upload_file()


                            except Exception as e:
                                messages_to_send.append((current_socket, f"Action Failed + {e}"))

                for message in messages_to_send:
                    current_socket, data = message
                    if current_socket in wlist:
                        current_socket.send(data.encode())
                    messages_to_send.remove(message)


if __name__ == '__main__':
    server = Server()
    server.start_serv()
