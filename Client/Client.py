import socket
from threading import Thread
from Crypto.Cipher import AES


class Client:
    KEY_LEN = 16
    AES_ECB_BLOCK_LEN = 16
    REQUEST_PORTION = 2**10 * 8

    def __init__(self, server_host, server_port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.unencrypted = bytearray()
        self.key = bytes()
        self.decipher = None

        self.socket.connect((server_host, server_port))

    def start_client(self):
        self.__get_key()
        self.decipher = AES.new(self.key, AES.MODE_ECB)
        Thread(target=self.__decrypt_loop).start()

    def __get_key(self):
        while len(self.key) != Client.KEY_LEN:
            data = self.socket.recv(Client.KEY_LEN)
            if len(data) > Client.KEY_LEN - len(self.key):
                self.unencrypted += data[Client.KEY_LEN - len(self.key):]
                self.key += data[:Client.KEY_LEN - len(self.key)]
            else:
                self.key += data
        print('Out')

    def __decrypt_loop(self):
        while 1:
            self.unencrypted += self.socket.recv(Client.REQUEST_PORTION)
            data_length = len(self.unencrypted)
            size_to_decrypt = data_length - data_length % Client.AES_ECB_BLOCK_LEN
            decrypted_data = self.decipher.decrypt(self.unencrypted[:size_to_decrypt])
            self.unencrypted = self.unencrypted[size_to_decrypt:]
            self.socket.send(decrypted_data)
            print('Work!')
