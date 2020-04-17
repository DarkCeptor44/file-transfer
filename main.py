import socket
import pathlib
from tqdm import tqdm
from tkinter import Tk, filedialog
from argparse import ArgumentParser
from colorama import init, Fore

SEPARATOR = '<SEPARATOR>'
BUFFER_SIZE = 4096
DEFAULT_PORT = 3001


def ask_for_file():
    root = Tk()
    root.withdraw()
    filename = filedialog.askopenfilename()
    return filename


def ask_where_to_save():
    """

    :rtype: pathlib.WindowsPath
    """
    root = Tk()
    root.withdraw()
    path = filedialog.asksaveasfilename()
    return pathlib.Path(path).absolute()


def get_progress_bar(desc: str, size: int):
    return tqdm(range(size), desc, unit='B', unit_scale=True, unit_divisor=1024)


def check_file(filename: str):
    """

    :rtype: pathlib.WindowsPath
    """
    try:
        file = pathlib.Path(filename).absolute()
        if file.exists() and file.is_file():
            return file
        elif file.exists() and (not file.is_file() or file.is_dir()):
            raise IOError(f'\'{file}\' is a directory')
        else:
            raise IOError(f'File \'{file}\' does not exist')
    except IOError:
        pass


class Client:
    def __init__(self, ip: str, port: int = DEFAULT_PORT):
        if ip is None or ip == '':
            raise ValueError("Invalid IP")

        if port is None or port == 0:
            raise ValueError('Invalid Port')

        self.host = ip
        self.port = port

    def send(self, filename: str):
        file_to_send = check_file(filename)
        if file_to_send is None:
            raise ValueError("File to send is null")

        # size = os.path.getsize(file_to_send)
        size = file_to_send.stat().st_size
        s = socket.socket()
        # s.settimeout(1)
        print(f'{Fore.YELLOW}[*] Connecting to {self.host}:{self.port}{Fore.RESET}')
        s.connect((self.host, self.port))
        print(f'{Fore.GREEN}[+] Connected.{Fore.RESET}')

        s.send(f'{filename}{SEPARATOR}{size}'.encode())
        Client.actually_send(s, file_to_send)

    @staticmethod
    def actually_send(s: socket.socket, file: pathlib.WindowsPath):
        size = file.stat().st_size
        progress = get_progress_bar(f'{Fore.GREEN}Sending {file.name}{Fore.RESET}', size)
        with open(str(file.absolute()), 'rb') as f:
            for _ in progress:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break

                s.sendall(bytes_read)
                progress.update(len(bytes_read))
        s.close()


class Server:
    def __init__(self, port: int = DEFAULT_PORT):
        if port is None or port == 0:
            raise ValueError('Invalid Port')

        self.host = '0.0.0.0'
        self.port = port

    def receive(self):
        s = socket.socket()
        s.bind((self.host, self.port))
        s.listen(5)
        print(f'{Fore.GREEN}[*] Listening as {self.host}:{self.port}{Fore.RESET}')

        client_socket, address = s.accept()
        print(f'{Fore.BLUE}[+] {address} is connected.{Fore.RESET}')

        received = client_socket.recv(BUFFER_SIZE).decode()
        filepath, filesize = received.split(SEPARATOR)
        file = pathlib.Path(filepath)
        Server.actually_receive(s, client_socket, file, int(filesize))

    @staticmethod
    def actually_receive(s: socket.socket, cs: socket.socket, file: pathlib.WindowsPath, size: int):
        progress = get_progress_bar(f'{Fore.GREEN}Receiving {file.name}{Fore.RESET}', size)
        with open(str(ask_where_to_save().absolute()), 'wb') as f:
            for _ in progress:
                bytes_read = cs.recv(BUFFER_SIZE)
                if not bytes_read:
                    break

                f.write(bytes_read)
                progress.update(len(bytes_read))

        cs.close()
        s.close()


if __name__ == '__main__':
    parser = ArgumentParser(description='File Transfer Utility')
    parser.add_argument('operation', help='Client or Server', nargs='?')
    parser.add_argument('--host', help='IP Address of the host', type=str)
    args = parser.parse_args()

    try:
        if str(args.operation).lower() == 'client':
            if args.host is not None and args.host != '':
                print('Starting client...')

                client = Client(args.host)
                client.send(ask_for_file())
            else:
                print(f'{Fore.RED}Invalid Host{Fore.RESET}')
                parser.print_usage()
        elif str(args.operation).lower() == 'server':
            print('Starting server...')

            server = Server()
            server.receive()
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print('Exitting now...')
    except Exception as e:
        print(f'{Fore.RED}Error: {str(e)}{Fore.RESET}')
