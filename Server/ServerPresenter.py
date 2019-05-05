from threading import Thread
import socket
import time


class ServerPresenter:
    PORT = 14900
    BLOCK_SIZE = 2**10 # 1 kb

    def __init__(self, filename):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.blocks = {} # block id : raw data
        self.tasks_map = {} # socket id : block id
        self.remaining = {} # block id : remaining

        with open(filename, "rb") as file:
            data = file.read()
            data += bytes(([0] * (len(self.blocks) % 16)))
            position = 0
            block_number = 0
            while position != len(data):
                right_bound = position + min(len(data) - position, ServerPresenter.BLOCK_SIZE)
                self.blocks[block_number] = data[position:right_bound]
                self.remaining[block_number] = len(self.blocks[block_number])
                block_number += 1
                position = right_bound

        print(len(self.blocks))

    def start_server(self):
        self.server_socket.bind(("", ServerPresenter.PORT))
        self.server_socket.listen()
        for func in [self.__wait_for_new_clients, self.__send_loop, self.__get_loop]:
            t = Thread(target=func)
            t.start()

    def __wait_for_new_clients(self):
        while 1:
            client, addr = self.server_socket.accept()
            try:
                self.clients.append(client)
            except Exception as e:
                print(e)

    def __send_loop(self):
        while 1:
            try:
                if not self.clients:
                    time.sleep(3)
                for i in range(len(self.clients)):
                    if not self.blocks:
                        time.sleep(5)
                        continue
                    if not self.__client_is_busy(i):
                        self.__assign_task(i)
            except Exception as e:
                print(e)

    def __get_loop(self):
        while 1:
            try:
                if not self.clients:
                    time.sleep(3)
                for i in range(len(self.clients)):
                    client = self.clients[i]
                    data = client.recv(ServerPresenter.BLOCK_SIZE)
                    self.__on_part_of_task_done(self.tasks_map[i], data)
            except Exception as e:
                print(e)

    def __client_is_busy(self, client_index):
        return client_index in self.tasks_map and self.remaining[self.tasks_map[client_index]] != 0

    def __on_part_of_task_done(self, task_index, data):
        with open('file' + str(task_index), 'ab+') as file:
            file.write(data)
        self.remaining[task_index] -= len(data)

    def __assign_task(self, client_index):
        key, value = self.blocks.popitem()
        self.tasks_map[client_index] = key
        self.clients[client_index].send(value)
