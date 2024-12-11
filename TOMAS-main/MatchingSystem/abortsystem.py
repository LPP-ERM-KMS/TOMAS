from tkinter import *

running = True  # Global flag
idx = 0  # loop index

def start():
    """Enable scanning by setting the global flag to True."""
    global running
    running = True

def stop():
    """Stop scanning by setting the global flag to False."""
    global running
    running = False

root = Tk()
root.title("Title")
root.geometry("500x500")

app = Frame(root)
app.grid()

start = Button(app, text="Start Scan", command=start)
stop = Button(app, text="Stop", command=stop)

start.grid()
stop.grid()

while True:
    if idx % 500 == 0:
        root.update()
        idx = 0

    if running:
        print("hello")
        idx += 1
