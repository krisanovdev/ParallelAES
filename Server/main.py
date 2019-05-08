from Server import Server


def main():
    server = Server('Cartographic.pdf', bytes('abcdefghijklmnop', 'utf-8'))
    server.start_server()


if __name__ == '__main__':
    main()
