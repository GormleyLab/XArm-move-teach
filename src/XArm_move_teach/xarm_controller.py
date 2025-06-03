import sys
import time
import pandas as pd
import threading
import pygame
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from xarm.wrapper import XArmAPI


class XArmController:
    def __init__(self, ip, home_position=None):
        self.ip = ip
        self.home_position = home_position or [-159.3, -193.5, 329.4, 180, 0, -90]
        self.arm = None
        self.joystick = None
        
    def initialize_xarm(self):
        self.arm = XArmAPI(self.ip)
        self.arm.motion_enable(True)
        self.arm.set_mode(0)
        self.arm.set_state(0)
        self.arm.set_gripper_mode(0)
        self.arm.set_gripper_enable(True)
        self.arm.set_gripper_speed(1000)
        self.arm.set_gripper_position(850, wait=True)
        self.arm.set_position(*self.home_position[:6], speed=400, wait=True)
        print(f"Connected to xArm at {self.ip}")
        return self.arm

    def go_to_home(self):
        self.arm.set_mode(0)
        self.arm.set_state(0)
        self.arm.set_position(*self.home_position[:6], speed=400, wait=True)
        print("Moved to home position.")

    def initialize_controller(self):
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            print("No Xbox controller detected. Please connect one and try again.")
            sys.exit()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        print("Initialized controller:", self.joystick.get_name())
        return self.joystick

    def step_move(self, axis_x, axis_y, axis_z, axis_r, pos_increment):
        self.arm.set_mode(0)
        self.arm.set_state(0)
        
        pos_x, pos_y, pos_z, pos_r = (
            self.arm.position[0],
            self.arm.position[1],
            self.arm.position[2],
            self.arm.position[5],
        )
        pos_r += int(pos_increment * axis_r)
        pos_x += int(pos_increment * axis_x)
        pos_y -= int(pos_increment * axis_y)
        pos_z -= int(pos_increment * axis_z)
        new_pos = [pos_x, pos_y, pos_z, 180, 0, pos_r]
        self.arm.set_position(*new_pos[:6], speed=400, wait=True)
        print(f"Step move: X={pos_x}, Y={pos_y}, Z={pos_z}, R={pos_r}")

    def velocity_move(self, axis_x, axis_y, axis_z, axis_r, speed):
        self.arm.set_mode(5)
        self.arm.set_state(0)
        vel_x = int(speed * axis_x)
        vel_y = int(speed * axis_y * -1)
        vel_z = int(speed * axis_z * -1)
        vel_r = int(speed * axis_r * 0.5)
        self.arm.vc_set_cartesian_velocity([vel_x, vel_y, vel_z, 0, 0, vel_r])
        print(f"Velocity move: X={vel_x}, Y={vel_y}, Z={vel_z}, R={vel_r}")

    def controller_loop(self, control_mode, pos_increment, velocity):
        AXIS_X = 0
        AXIS_Y = 1
        AXIS_Z = 3
        AXIS_R = 2
        GRIPPER_CLOSED_BUTTON = 0
        GRIPPER_OPEN_BUTTON = 1
        EXIT_BUTTON = 6
        deadzone = 0.2

        print("Controller loop started in", control_mode, "mode.")
        running = True
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                axis_x = self.joystick.get_axis(AXIS_X)
                axis_y = self.joystick.get_axis(AXIS_Y)
                axis_z = self.joystick.get_axis(AXIS_Z)
                axis_r = self.joystick.get_axis(AXIS_R)
                
                if abs(axis_x) < deadzone:
                    axis_x = 0.0
                if abs(axis_y) < deadzone:
                    axis_y = 0.0
                if abs(axis_z) < deadzone:
                    axis_z = 0.0
                if abs(axis_r) < deadzone:
                    axis_r = 0.0

                if control_mode == "step":
                    self.step_move(axis_x, axis_y, axis_z, axis_r, pos_increment)
                else:
                    self.velocity_move(axis_x, axis_y, axis_z, axis_r, velocity)
                
                if self.joystick.get_button(GRIPPER_OPEN_BUTTON):
                    self.arm.set_gripper_position(850, wait=True)
                    print("Gripper opened")
                    
                if self.joystick.get_button(GRIPPER_CLOSED_BUTTON):
                    self.arm.set_gripper_position(270, wait=True)
                    print("Gripper closed")

                if self.joystick.get_button(EXIT_BUTTON):
                    print("Stop button pressed. Stopping controller movement.")
                    running = False

                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Interrupted by user. Exiting controller loop...")
        finally:
            sys.exit()

    def move_mode(self):
        def start_control():
            control_mode = mode_var.get()
            try:
                pos_increment_val = float(increment_entry.get())
            except ValueError:
                pos_increment_val = 5
            try:
                velocity_val = float(velocity_entry.get())
            except ValueError:
                velocity_val = 100

            start_button.config(state=tk.DISABLED)
            status_label.grid()

            control_thread = threading.Thread(
                target=self.controller_loop,
                args=(control_mode, pos_increment_val, velocity_val),
                daemon=True,
            )
            control_thread.start()

            def check_thread():
                if control_thread.is_alive():
                    root.after(100, check_thread)
                else:
                    start_button.config(state=tk.NORMAL)
                    status_label.grid_remove()

            root.after(100, check_thread)

        root = tk.Tk()
        root.title("xArm Control via Xbox Controller")

        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        mode_var = tk.StringVar(value="velocity")
        ttk.Label(main_frame, text="Control Mode:").grid(column=0, row=0, sticky=tk.W)
        step_radio = ttk.Radiobutton(main_frame, text="Step", variable=mode_var, value="step")
        vel_radio = ttk.Radiobutton(
            main_frame, text="Velocity", variable=mode_var, value="velocity"
        )
        step_radio.grid(column=1, row=0, sticky=tk.W)
        vel_radio.grid(column=2, row=0, sticky=tk.W)

        ttk.Label(main_frame, text="Step Increment (mm):").grid(column=0, row=1, sticky=tk.W)
        increment_entry = ttk.Entry(main_frame, width=10)
        increment_entry.insert(0, "5")
        increment_entry.grid(column=1, row=1, sticky=(tk.W, tk.E))

        ttk.Label(main_frame, text="Velocity (mm/s):").grid(column=0, row=2, sticky=tk.W)
        velocity_entry = ttk.Entry(main_frame, width=10)
        velocity_entry.insert(0, "100")
        velocity_entry.grid(column=1, row=2, sticky=(tk.W, tk.E))

        start_button = ttk.Button(main_frame, text="Start Control", command=start_control)
        start_button.grid(column=0, row=3, pady=10)

        def quit_app():
            root.destroy()

        quit_button = ttk.Button(main_frame, text="Done", command=quit_app)
        quit_button.grid(column=1, row=3, pady=10)
            
        home_button = ttk.Button(main_frame, text="Go Home", command=self.go_to_home)
        home_button.grid(column=2, row=3, pady=10)

        status_label = ttk.Label(main_frame, text="Press Stop Button on Controller When Done")
        status_label.grid(column=0, row=5, columnspan=2, pady=10)
        status_label.grid_remove()

        try:
            xbox_image = Image.open("xbox_controller.png")
            xbox_image = xbox_image.resize((400, 300))
            xbox_photo = ImageTk.PhotoImage(xbox_image)
            img_label = ttk.Label(main_frame, image=xbox_photo)
            img_label.grid(column=0, row=4, columnspan=3, pady=10)
        except FileNotFoundError:
            print("Xbox controller image not found, continuing without image")

        root.mainloop()

    def enter_position_name(self):
        def submit_position_name():
            response.set(entry.get())
            if response.get():
                print(f"Position name entered: {response.get()}")
                win.destroy()
            else:
                print("Please enter a valid position name.")

        win = tk.Tk()
        win.title("Enter Position Name")
        win.geometry("300x200")
        response = tk.StringVar()
        ttk.Label(win, text="Enter Position Name:").pack(pady=10)
        entry = ttk.Entry(win)
        entry.pack(pady=5)
        submit_button = ttk.Button(win, text="Submit", command=submit_position_name)
        submit_button.pack(pady=10)
        win.mainloop()
        return response.get()

    def add_position(self):
        def add_position():
            response.set("add")
            win.destroy()
        
        def done():
            response.set("done")
            win.destroy()
        
        win = tk.Tk()
        win.title("Teach Mode")
        win.geometry("300x200")
        response = tk.StringVar()
        manual_move_button = ttk.Button(win, text="Add New Position", command=add_position)
        manual_move_button.grid(column=0, row=0, pady=10)
        teach_mode_button = ttk.Button(win, text="Done", command=done)
        teach_mode_button.grid(column=1, row=0, pady=10)
        win.mainloop()
        return response.get()

    def goto_position(self):
        df = pd.read_excel('xArm positions.xlsx')
        df = df.fillna('')
        
        pos_dict = {}
        pos_list = []
        
        for column_name in df.columns:
            for pos in df[column_name]:
                if pos != '':
                    pos_list.append(eval(pos))
            pos_dict[column_name] = pos_list
            pos_dict['reverse_'+column_name] = list(reversed(pos_list))
            pos_list = []
        
        win = tk.Tk()
        win.title("GOTO Mode")
        win.geometry("400x150")
        
        ttk.Label(win, text="Select Position:").pack(pady=10)
        
        combo = ttk.Combobox(win, values=list(df.columns))
        combo.pack(pady=5)
        combo.current(0)
        
        def pickup():
            location = combo.get()
            reverse_location = 'reverse_' + location
            print("Picking up from position:", location)
            
            self.arm.move_arc_lines(pos_dict[location], speed=300, wait=True)
            self.arm.set_gripper_position(800, wait=True)
            self.arm.move_arc_lines(pos_dict[reverse_location], speed=300, wait=True)
        
        def dropoff():
            location = combo.get()
            reverse_location = 'reverse_' + location
            print("Dropping off to position:", location)
            
            self.arm.move_arc_lines(pos_dict[location], speed=300, wait=True)
            self.arm.set_gripper_position(850, wait=True)
            self.arm.move_arc_lines(pos_dict[reverse_location], speed=300, wait=True)
        
        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=10)
        
        pickup_button = ttk.Button(btn_frame, text="Pickup", command=pickup)
        pickup_button.pack(side=tk.LEFT, padx=10)
        
        dropoff_button = ttk.Button(btn_frame, text="Dropoff", command=dropoff)
        dropoff_button.pack(side=tk.LEFT, padx=10)
        
        home_button = ttk.Button(btn_frame, text="Go Home", command=self.go_to_home)
        home_button.pack(side=tk.LEFT, padx=10)
        
        def quit_app():
            win.destroy()

        quit_button = ttk.Button(btn_frame, text="Done", command=quit_app)
        quit_button.pack(side=tk.LEFT, padx=10)
        
        win.mainloop()

    def choose_mode(self):
        def move_mode():
            response.set("move")
            win.destroy()
        
        def teach_mode():
            response.set("teach")
            win.destroy()
            
        def goto_mode():
            response.set("GOTO")
            win.destroy()
        
        win = tk.Tk()
        win.title("Select Control Mode")
        win.geometry("350x100")
        response = tk.StringVar()
        manual_move_button = ttk.Button(win, text="Manual Move", command=move_mode)
        manual_move_button.grid(column=0, row=0, pady=10)
        teach_mode_button = ttk.Button(win, text="Teach Mode", command=teach_mode)
        teach_mode_button.grid(column=1, row=0, pady=10)
        goto_mode_button = ttk.Button(win, text="GOTO Mode", command=goto_mode)
        goto_mode_button.grid(column=2, row=0, pady=10)
        
        def quit_app():
            response.set("quit")
            win.destroy()

        quit_button = ttk.Button(win, text="Quit", command=quit_app)
        quit_button.grid(column=3, row=0, pady=10)
        win.mainloop()
        return response.get()

    def run(self):
        self.initialize_xarm()
        self.initialize_controller()
        
        mode = self.choose_mode()
        while mode != 'quit':
            if mode == "move":
                self.move_mode()
            elif mode == "teach":
                print("Teaching mode selected. Going to home position")
                self.go_to_home()
                df = pd.read_excel('../../xArm positions.xlsx')
                position_list = []
                position_list.append(self.arm.position)
                name = self.enter_position_name()
                add_or_done = self.add_position()
                while add_or_done == 'add':
                    self.move_mode()
                    position_list.append(self.arm.position)
                    print(position_list)
                    add_or_done = self.add_position()
                new_df = pd.DataFrame({name: pd.Series(position_list)})
                df = pd.concat([df, new_df], axis=1)
                df = df.fillna('')
                df.to_excel('xArm positions.xlsx', index=False)
            elif mode == "GOTO":
                self.goto_position()
                
            mode = self.choose_mode()

        self.go_to_home()
        print("Exiting...")
        pygame.quit()
        self.arm.disconnect()