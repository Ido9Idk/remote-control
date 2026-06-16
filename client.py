import socket
from PIL import ImageGrab, ImageDraw, Image
import threading
from time import sleep
from pynput import mouse
from pynput.mouse import Button, Controller
# from screeninfo import get_monitors
from io import BytesIO
from os import execv
from sys import argv, executable
import struct
from pathlib import Path

class client():
    def __init__(self):
        self.client_udp_screen = None
        self.mouse_coordinates = None
        self.mouse = Controller()
        self.screen_res = (1280, 720)
        self.host_adress = "127.0.0.1"
        self.tcp_port = 34467
        self.udp_port = 34468
        listener = mouse.Listener(
        on_move=self.on_move,)
        listener.start()

    def restart(self):
        print("restart function")
        print("argv: " + str(argv))
        print("executable: "+ str(executable))
        quoted_script_path = f'"{argv[0]}"'
        execv(executable, [executable] + [quoted_script_path])  #fix here

    def _connect_to_controller_tcp(self):
        while True:
            try:
                self.client_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_tcp.connect(('127.0.0.1', self.tcp_port))
                while True:
                    header, data = self._recv_all(self.client_tcp)
                    if header == 0:
                        print("recieved restart packet")
                        self.restart()
                    elif header == 1:
                        x, y = struct.unpack('!2I', data)
                        print(x, y)
                        self.mouse.position = (x, y)

            except Exception as err:
                print(err)
                self.client_tcp = None
            sleep(0.1)

            print(self.client_tcp)

    def connect_to_controller_tcp_threaded(self):
        self.tcp_socket_thread = threading.Thread(target=self._connect_to_controller_tcp)
        self.tcp_socket_thread.start()


    def _recv_all(self, client):
        print("received")
        data = b''
        header = struct.unpack('!I', client.recv(4))[0] #unpack returns a tuple
        length = struct.unpack('!I', client.recv(4))[0]
        while len(data) < length:
            chunk = client.recv(length - len(data))
            data += chunk
        print("header: "+ str(header))
        print("data: "+ str(data))
        return header, data

    def _parse_tcp_packet(self):
        if not self.client_tcp:
            return
        struct.unpack()

    def connect_to_controller_udp(self):
        try:
            self.client_udp_screen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.client_udp_screen.connect(('127.0.0.1', self.udp_port))

        except Exception as err:
            print(err)


    def send_screen(self):
        MAX_UDP_SIZE = 60000
        while True:
            if not self.client_tcp:
                continue

            im = ImageGrab.grab()

            if(self.mouse_coordinates):
                cursor = ImageDraw.Draw(im)
                cursor.circle(self.mouse_coordinates, 5, fill='#089bbf', outline='#076b85', width=1)

            im.thumbnail(self.screen_res)


            virtual_file = BytesIO()
            im.save(virtual_file, format='JPEG', quality=30, optimize=True)
            
            file_bytes = virtual_file.getvalue()
            # print(fr'{len(file_bytes)}')

            if len(file_bytes) > MAX_UDP_SIZE:
                continue

            self.client_udp_screen.sendto(file_bytes, ("127.0.0.1", self.udp_port))

            sleep(0.01)


    def on_move(self, x, y):
        self.mouse_coordinates = (x, y)


my_client = client()
my_client.connect_to_controller_tcp_threaded()
my_client.connect_to_controller_udp()
my_client.send_screen()