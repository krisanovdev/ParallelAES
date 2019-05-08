from threading import Thread
import socket
import time
import os


class Server:
    PORT = 14900
    BLOCK_SIZE = 2**10 * 2**10 * 8
    DECRYPT_FOLDER = 'Decrypted'

    def __init__(self, filename, decryption_key):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.blocks = {} # block id : raw data
        self.tasks_map = {} # socket id : block id
        self.remaining = {} # block id : remaining
        self.tasks_count = 0
        self.filename = filename
        self.decryption_key = decryption_key

        with open(filename, "rb") as file:
            data = file.read()
        data += bytes(([0] * (len(data) % 16)))
        position = 0
        block_number = 0
        data_length = len(data)
        while position != data_length:
            right_bound = position + min(data_length - position, Server.BLOCK_SIZE)
            self.blocks[block_number] = data[position:right_bound]
            self.remaining[block_number] = len(self.blocks[block_number])
            block_number += 1
            position = right_bound
        self.tasks_count = block_number
        os.makedirs(Server.DECRYPT_FOLDER, exist_ok=True)

    def start_server(self):
        self.server_socket.bind(("", Server.PORT))
        self.server_socket.listen()
        for func in [self.__wait_for_new_clients, self.__send_loop, self.__get_loop]:
            Thread(target=func).start()

    def __wait_for_new_clients(self):
        while self.remaining:
            client, addr = self.server_socket.accept()
            try:
                client.settimeout(5)
                client.send(self.decryption_key)
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
                        return
                    if not self.__client_is_busy(i):
                        self.__assign_task(i)
            except Exception as e:
                print(e)
            print('send')

    def __get_loop(self):
        while 1:
            try:
                if not self.clients:
                    time.sleep(3)
                for i in range(len(self.clients)):
                    client = self.clients[i]
                    if not self.__client_is_busy(i):
                        continue
                    data = client.recv(Server.BLOCK_SIZE)
                    self.__on_part_of_task_done(self.tasks_map[i], data)
                if not self.remaining:
                    self.__merge_chunks()
                    return
            except Exception as e:
                print(e)
            print('get')

    def __client_is_busy(self, client_index):
        return client_index in self.tasks_map and self.tasks_map[client_index] in self.remaining

    def __on_part_of_task_done(self, task_index, data):
        try:
            if not data:
                return
            chunk_path = os.path.join(Server.DECRYPT_FOLDER, 'chunk' + str(task_index))
            with open(chunk_path, 'ab+') as file:
                file.write(data)
            self.remaining[task_index] -= len(data)
            if self.remaining[task_index] == 0:
                self.remaining.pop(task_index, None)
        except Exception as e:
            print(e)

    def __assign_task(self, client_index):
        try:
            key, value = self.blocks.popitem()
            self.tasks_map[client_index] = key
            self.clients[client_index].send(value)
        except Exception as e:
            print(e)

    def __merge_chunks(self):
        result_file_path = os.path.join(Server.DECRYPT_FOLDER, self.filename)
        os.rename(os.path.join(Server.DECRYPT_FOLDER, 'chunk0'), result_file_path)
        result_file = open(result_file_path, 'ab')
        for i in range(1, self.tasks_count):
            chunk_path = os.path.join(Server.DECRYPT_FOLDER, 'chunk' + str(i))
            with open(chunk_path, 'rb') as file:
                result_file.write(file.read())
            os.remove(chunk_path)
        result_file.close()
