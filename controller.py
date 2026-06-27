import socket
import threading
from pynput import mouse
from PIL import Image
import sys
from io import BytesIO
import struct

class remote_controller:
    def __init__(self):
        self.tcp_server = None
        self.udp_server = None
        self.is_online = False
        self.coordinates = None
        self.screen = None
        self.active_client_tcp = None
        self.listener = mouse.Listener(
            # on_move=self.on_move,
            # on_click=self.on_click,
            # on_scroll=self.on_scroll
            )
        self.listener.start()
        self.ports = (34467, 34468)

        try:
            self.fallback_img = Image.open("no_connection.png")
        except FileNotFoundError:
            self.fallback_img = Image.new("RGB", (1280, 720), color="gray")

    def __str__(self):
        info = {"tcp_port":self.ports[0], "udp_port":self.ports[1], "is_online": self.is_online}
        return str(info)

    def startall(self):
        self.is_online = True
        self.start_threaded_tcp_input_server()
        self.start_threaded_udp_screen_server()

    def stopall(self):
        self.is_online = False
        self.stop_udp_screen_server()
        self.stop_tcp_input_server()
        self.screen = None

    def _start_tcp_input_server(self):
        self.tcp_server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.tcp_server.bind(("0.0.0.0", self.ports[0]))
        self.tcp_server.listen(1)
        while self.is_online:
            try:
                client, addr = self.tcp_server.accept()
                self.active_client_tcp = client
                check = client.recv(4)
                if not check:
                    self.is_online = False 


            except (OSError, socket.error) as err:
                if not self.is_online:
                    break
                print(f"Socket error: {err}")

            except Exception as err:
                print(f"Unexpected error: {err}")
                client.close()
                self.active_client_tcp = None
                break
        sys.exit()

    def _recv_all(self, client, length):
        img_bytes = b''
        while len(img_bytes) < length:
            img_chunk = client.recv(length - len(img_bytes))
            img_bytes += img_chunk
        return img_bytes

    def create_tcp_packet(self, header, data=b''):
        header = int(header)
        # restart header
        if header == 0:
            payload = b''
        # mouse pos header
        elif header == 1:
            x, y = data
            payload = struct.pack('!I', x) + struct.pack('!I', y)
        #mouse clicks
        elif header == 2:
            # LEFT_CLICK = 1
            # MIDDLE_CLICK = 2
            # RIGHT_CLICK = 3
            payload = struct.pack('!I', data)
        #key pressed
        elif header == 3:
            data = str(data)
            payload = data.encode('utf-8')

        print((struct.pack('!I', header) + struct.pack('!I', len(payload))))
        return (struct.pack('!I', header) + struct.pack('!I', len(payload)) + payload)

    def restart_client(self):
        if self.active_client_tcp:
            self.active_client_tcp.sendall(self.create_tcp_packet(0))

    def send_mouse_coords(self, x, y):
        if self.active_client_tcp:
            self.active_client_tcp.sendall(self.create_tcp_packet(1, (x, y)))

    def send_mouse_clicks(self, button):
        if not self.active_client_tcp:
            return
        print(f'clicked with mode: {button.num}')
        self.active_client_tcp.sendall(self.create_tcp_packet(2, button.num))


    def start_threaded_tcp_input_server(self):
        self.tcp_socket_thread = threading.Thread(target=self._start_tcp_input_server)
        self.tcp_socket_thread.start()  

    def stop_tcp_input_server(self):
        self.is_online=False
        if self.tcp_server:
            self.tcp_server.close()
            if self.active_client_tcp:
                self.active_client_tcp.close()
                self.active_client_tcp = None
        self.tcp_server = None
        
    def _start_udp_screen_server(self):
        self.udp_server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udp_server.bind(("0.0.0.0", self.ports[1]))
        print("udp server started")
        while self.is_online:
            try:
                bytes_img, client = self.udp_server.recvfrom(65535)
                img = Image.open(BytesIO(bytes_img), 'r').convert("RGB")
                self.screen = img

            except (OSError, socket.error) as err:
                if not self.is_online:
                    break
                self.screen = None
                print(f"Socket error: {err}")

            except Exception as err:
                print(f"Unexpected error: {err}")
                client.close()
                break
        sys.exit()

    def start_threaded_udp_screen_server(self):
        self.udp_socket_thread = threading.Thread(target=self._start_udp_screen_server)
        self.udp_socket_thread.start()  

    def stop_udp_screen_server(self):
        self.is_online=False
        if self.udp_server:
            try:
                self.udp_server.close()
            except Exception:
                pass
            self.udp_server = None

    def get_screen(self):
        if not self.screen:
            return self.fallback_img
        else:
            return self.screen.copy()

    def on_move(self, x, y):
        print(f'\rPointer moved to {x, y}', end='')
        self.coordinates = (x, y)

    def on_click(x, y, button, pressed):
        print('{0} at {1}'.format(
            'Pressed' if pressed else 'Released',
            (x, y)))
        if not pressed:
            # Stop listener
            return False

    def on_scroll(x, y, dx, dy):
        print('Scrolled {0} at {1}'.format(
            'down' if dy < 0 else 'up',
            (x, y)))
        

    def get_coords(self):
        return self.coordinates
    

    def change_coords(self):
        self.active_client_tcp.send(self.coordinates)
    


if __name__ == "__main__":
    controller = remote_controller()
    controller.startall()
    print(controller)