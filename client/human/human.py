from Tkinter import *
import thread

# On Linux, you may need to install python-tk package...


########################################################################
class HumanClient(object):
    ####################################################################
    def __init__(self):
        self.root = Tk()
        self.root.title("Battleship")
        self.grid_image = PhotoImage(file="grid.gif")
        Label(self.root, image=self.grid_image).pack(side=TOP, expand=True, fill=BOTH)

        top_frame = Frame(self.root)
        top_frame.pack(side=TOP, expand=True, fill=BOTH)

        self.scrollbar = Scrollbar(top_frame)
        self.list_box = Listbox(top_frame, height=10, width=80)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.list_box.pack(side=LEFT, expand=True, fill=BOTH)
        self.scrollbar.config(command=self.list_box.yview)
        self.list_box.config(yscrollcommand=self.scrollbar.set)

        bottom_frame = Frame(self.root)
        bottom_frame.pack(side=BOTTOM, fill=X)
        Label(bottom_frame, text="User Input").pack(side=LEFT)
        self.text_entry = Entry(bottom_frame)
        self.text_entry.insert(END, "")
        self.text_entry.pack(side=RIGHT, expand=True, fill=X)
        self.text_entry.bind("<Return>", lambda event: self.send_response())
        self.text_entry.bind("<KP_Enter>", lambda event: self.send_response())

    ####################################################################
    def send_response(self):
        text = self.text_entry.get()
        print text.strip()  # send it to standard out, followed by a newline
        self.text_entry.delete(0, END)

    ####################################################################
    def add_line(self, line):
        self.list_box.insert(END, line)
        self.list_box.select_clear(self.list_box.size() - 2)  # Clear the current selected item
        self.list_box.select_set(END)                         # Select the new item
        self.list_box.yview(END)                              # Set the scrollbar to the end of the list_box


########################################################################
def run_listener(client):
    while True:
        line = raw_input()
        client.add_line(line)
        if line == "|INFO|end game|END|":
            return


########################################################################
if __name__ == "__main__":
    client = HumanClient()
    thread.start_new_thread(run_listener, (client,))
    mainloop()
