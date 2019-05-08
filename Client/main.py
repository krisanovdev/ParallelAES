from Client import Client


def main():
    '''key = 'abcdefghijklmnop'
    cipher = AES.new(bytes(key, 'utf-8'), AES.MODE_ECB)
    msg = cipher.encrypt(bytes('TechTutorialsX!!TechTutorialsX!!', 'utf-8'))
    print(len(msg))
    print(type(msg))
    print(msg)

    with open("filename", "wb") as newFile:
        newFile.write(msg)

    with open("filename", "rb") as newFile:
        data = newFile.read()
    decipher = AES.new(bytes(key, 'utf-8'), AES.MODE_ECB)
    print(decipher.decrypt(data).decode('utf-8'))'''

    client = Client('127.0.0.1', 14900)
    client.start_client()


if __name__ == '__main__':
    main()
