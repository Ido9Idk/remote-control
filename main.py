from tkinter import ttk
import tkinter as tk
from controller import remote_controller
import sys
from PIL import ImageTk

class main_prog():
    def __init__(self):
        self.controller = remote_controller()
        self.coordinates = None
        self.root = None
        self.is_online = False
        self.create_gui()

    def toggle_server(self):
        # stop
        if self.is_online:
            self.controller.stopall()
            self.is_online = False
            self.start_stop_btn_text.set("Start receiving")
        # start
        else:
            self.controller.startall()
            self.is_online = True
            self.start_stop_btn_text.set("Stop receiving")


    def close_all(self):
        self.controller.stopall()
        self.root.after_cancel(self.update_coords_sceduler)
        self.root.destroy()
        sys.exit()

    def create_gui(self):
        self.root = tk.Tk()
        self.root.title("Remote control app (O_O)")
        self.root.resizable(0, 0)
        self.root.geometry('1280x740')
        self.root.protocol("WM_DELETE_WINDOW", self.close_all)

        main_frm = ttk.Frame(self.root, padding=0)
        main_frm.pack()

        options = ttk.Frame(main_frm, padding=0)
        options.pack(expand=True, fill='x')

        self.start_stop_btn_text = tk.StringVar()
        self.start_stop_btn_text.set("Stop receiving") if self.is_online else self.start_stop_btn_text.set("Start receiving")
        toggle_server_btn = tk.Button(options, command= self.toggle_server, textvariable=self.start_stop_btn_text)
        toggle_server_btn.pack(side='left')
        
        restart_client = tk.Button(options, command= self.controller.restart_client, text="Restart client")
        restart_client.pack(side='left')

        self.coordinates = tk.StringVar()
        ttk.Label(options, textvariable=self.coordinates).pack(side='left')

        ttk.Label(options, text="test").pack(side='left')

        self.screen_label = tk.Label(main_frm)
        self.screen_label.pack()
        self.screen_label.bind("<Motion>", self.ctrl_clients_coords)

        self.update_screen()
        self.update_coordinates()
        self.root.mainloop()

    def ctrl_clients_coords(self, coords):
        x = coords.x * 1920//1280
        y = coords.y * 1080//720
        print(fr"coords: {coords.x}, {coords.y}")
        self.controller.send_mouse_coords(x, y)
        new_coords = (coords.x, coords.y)
        self.coordinates.set(str(new_coords))


    def update_coordinates(self):
            new_coords = self.controller.get_coords()
            self.coordinates.set(str(new_coords))
            
            self.update_coords_sceduler = self.root.after(50, self.update_coordinates)

    def update_screen(self):
        img = self.controller.get_screen()
        screen = ImageTk.PhotoImage(image=img)
        self.screen_label.configure(image=screen)
        self.screen_label.pack()
        self.screen_label.image = screen

        self.update_screen_sceduler = self.screen_label.after(50, self.update_screen)


main_program = main_prog()
