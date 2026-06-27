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
        self.screen_size = (1280, 720)
        self.targets_screen_res = (1280, 720)
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

        # Start/Stop button
        self.start_stop_btn_text = tk.StringVar()
        self.start_stop_btn_text.set("Stop receiving") if self.is_online else self.start_stop_btn_text.set("Start receiving")
        toggle_server_btn = tk.Button(options, command= self.toggle_server, textvariable=self.start_stop_btn_text)
        toggle_server_btn.pack(side='left')
        
        # Restart client button
        restart_client = tk.Button(options, command= self.controller.restart_client, text="Restart client")
        restart_client.pack(side='left')

        self.coordinates = tk.StringVar()
        ttk.Label(options, textvariable=self.coordinates).pack(side='left')

        ttk.Label(options, text="test").pack(side='left')

        # Screen widget
        self.canvas_width = 1280
        self.canvas_height = 720
        self.screen_canvas = tk.Canvas(main_frm, width=self.canvas_width, height=self.canvas_height)
        self.screen_canvas.pack()

        # Handle events
        self.screen_canvas.bind("<Motion>", self.convert_coords)
        self.screen_canvas.bind("<Button>", self.controller.send_mouse_clicks)

        self.update_screen()
        self.update_coordinates()
        self.root.mainloop()

    def convert_coords(self, coords):
        if not self.controller.active_client_tcp:
            return
        
        #find where the image starts
        margin_x = (self.canvas_width - self.screen_size[0])//2
        margin_y = (self.canvas_height - self.screen_size[1])//2
        
        x = coords.x - margin_x
        y = coords.y - margin_y
        if x<0 or y<0 or x>=self.screen_size[0] or y>=self.screen_size[1]:
            return
        
        print(fr"canvas coords: {coords.x}, {coords.y}")
        print(fr"img coords: {x}, {y}")
        print(f"targets_screen_res: {self.targets_screen_res}")
        print(f"screen size: {self.screen_size}")

        x =  int(x * (self.targets_screen_res[0]/self.screen_size[0]))
        y = int(y * (self.targets_screen_res[1]/self.screen_size[1]))

        print(fr"coords_after_scale: {x}, {y}")
        self.controller.send_mouse_coords(x, y)
        self.coordinates.set(f"coords: {coords.x}, {coords.y}")


    def update_coordinates(self):
            # new_coords = self.controller.get_coords()
            # self.coordinates.set(str(new_coords))
            
            self.update_coords_sceduler = self.root.after(50, self.update_coordinates)

    def update_screen(self):
        img = self.controller.get_screen()
        if img: 
            self.targets_screen_res = (img.width, img.height) # the targets screen res in order to scale it back later
            img.thumbnail((self.canvas_width, self.canvas_height))
            screen_tk_image = ImageTk.PhotoImage(image=img)
            self.screen_size = (screen_tk_image.width(), screen_tk_image.height()) # the actual size of the targets screen in the canvas

            self.screen_canvas.delete("all")
            self.screen_canvas.create_image((self.canvas_width // 2, self.canvas_height // 2), image=screen_tk_image)
            self.screen_canvas.pack()
            self.screen_canvas.image = screen_tk_image

        self.update_screen_sceduler = self.screen_canvas.after(50, self.update_screen)


main_program = main_prog()
