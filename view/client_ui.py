from tkinter import messagebox
from tkinter import *
import tkinter as tk
import sys

# from  import Client
from model.client import Client


def on_closing(root, client):
    if client is None:
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()

    elif messagebox.askokcancel("Quit", "Do you want to quit?"):
        client.close_connection()
        root.destroy()
    sys.exit()


def zero_page():
    def getInput(files_num_text):
        try:
            window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window, None))
            n = files_num_text.get("1.0", "end-1c")
            if int(n) <= 0:
                raise Exception("The number needs to be positive")
            client = Client(int(n))
            first_page(client, window)
        except Exception as e:
            messagebox.showinfo('Error: ', e)

    window = Tk()
    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window, None))
    window.title('Client')
    window.geometry('360x400')
    window.configure(bg='#4a7abc')

    L1 = Label(window, bg='white', text="Enter number of files to store: (power of 2)").pack(pady=10)
    files_num_text = tk.Text(window, height=4, width=40)
    files_num_text.pack()

    btn1 = Button(window, bg='white', text="Send",
                  command=lambda: getInput(files_num_text)).pack()  # first_page(client, window))

    window.mainloop()


def first_page(client, old_page=None):
    old_page.destroy()

    main_window = Tk()
    main_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(main_window, client))
    main_window.title('Client')
    main_window.geometry('360x400')
    main_window.configure(bg='#4a7abc')

    L1 = Label(main_window, bg='white', text="Actions:").pack(pady=10)

    btn1 = Button(main_window, bg='white', text="Upload a file",
                  command=lambda: upload_file_page(main_window, client)).pack(pady=10)

    btn2 = Button(main_window, bg='white', text="Get a file",
                  command=lambda: get_file_page(main_window, client)).pack(pady=10)

    btn3 = Button(main_window, bg='white', text="Delete a file",
                  command=lambda: delete_file_page(main_window, client)).pack(pady=10)

    main_window.mainloop()


def getTextInput_upload(filepath_txt, filename_txt, client, upload_window):
    try:
        upload_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(upload_window, client))
        client.try_upload_stash()
        filepath = filepath_txt.get("1.0", "end-1c")
        filename = filename_txt.get("1.0", "end-1c")
        client.upload_file(filepath, filename)
        messagebox.showinfo('Upload File', 'Done!')
        first_page(client, upload_window)
    except Exception as e:
        messagebox.showinfo('Error: ', e)


def upload_file_page(old_page, client):
    old_page.destroy()

    upload_window = tk.Tk()
    upload_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(upload_window, client))
    upload_window.title('Upload File')
    upload_window.geometry('360x400')
    upload_window.configure(bg='#4a7abc')

    L1 = Label(upload_window, bg='white', text="Enter the file path:").pack(pady=10)
    filepath_text = tk.Text(upload_window, height=4, width=40)
    filepath_text.pack()

    L2 = Label(upload_window, bg='white', text="Enter the file name:").pack(pady=10)
    filename_text = tk.Text(upload_window, height=4, width=40)
    filename_text.pack()

    btnRead = tk.Button(upload_window, height=1, width=10, text="Upload",
                        command=lambda: getTextInput_upload(filepath_text, filename_text, client, upload_window))
    btnRead.pack()

    rtnButton = tk.Button(upload_window, height=1, width=10, text="Back",
                          command=lambda: first_page(client, upload_window))
    rtnButton.pack()

    upload_window.mainloop()


def getTextInput_get(filename_txt, client, get_window):
    try:
        get_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(get_window, client))
        client.try_upload_stash()
        filename = filename_txt.get("1.0", "end-1c")
        file, real_size = client.get_file(filename)
        if file is None:
            messagebox.showinfo('Error', 'Not Found!')
            first_page(client, get_window)
        messagebox.showinfo('Get File', 'Done!')
        present_file_page(get_window, client, file, real_size)
    except Exception as e:
        messagebox.showinfo('Error: ', e)


def get_file_page(old_page, client):
    old_page.destroy()

    get_window = tk.Tk()
    get_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(get_window, client))
    get_window.title('Get File')
    get_window.geometry('360x400')
    get_window.configure(bg='#4a7abc')

    L2 = Label(get_window, bg='white', text="Enter the file name:").pack(pady=10)
    filename_text = tk.Text(get_window, height=4, width=40)
    filename_text.pack()

    btnRead = tk.Button(get_window, height=1, width=20, text="Get the file",
                        command=lambda: getTextInput_get(filename_text, client, get_window))
    btnRead.pack()

    rtnButton = tk.Button(get_window, height=1, width=20, text="Back",
                          command=lambda: first_page(client, get_window))
    rtnButton.pack()

    get_window.mainloop()


def present_file_page(old_page, client, file, real_size):
    old_page.destroy()

    present_file = tk.Tk()
    present_file.protocol("WM_DELETE_WINDOW", lambda: on_closing(present_file, client))
    present_file.title('File')
    present_file.geometry('360x400')
    present_file.configure(bg='#4a7abc')

    L2 = Label(present_file, bg='white', text=f"The wanted file: {file.filename}").pack(pady=10)
    data_text = Label(present_file, bg='white', text=file.data[:real_size]).pack()

    rtnButton = tk.Button(present_file, height=1, width=20, text="Back",
                          command=lambda: first_page(client, present_file))
    rtnButton.pack()

    present_file.mainloop()


def getTextInput_delete(filename_txt, client, delete_window):
    try:
        delete_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(delete_window, client))
        client.try_upload_stash()
        filename = filename_txt.get("1.0", "end-1c")
        client.delete_file(filename)
        messagebox.showinfo('Delete File', 'Done!')
        first_page(client, delete_window)
    except Exception as e:
        messagebox.showinfo('Error: ', e)


def delete_file_page(old_page, client):
    old_page.destroy()

    delete_window = tk.Tk()
    delete_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(delete_window, client))
    delete_window.title('Delete File')
    delete_window.geometry('360x400')
    delete_window.configure(bg='#4a7abc')

    L2 = Label(delete_window, bg='white', text="Enter the file name:").pack(pady=10)
    filename_text = tk.Text(delete_window, height=4, width=40)
    filename_text.pack()

    btnRead = tk.Button(delete_window, height=1, width=10, text="Delete",
                        command=lambda: getTextInput_delete(filename_text, client, delete_window))
    btnRead.pack()

    rtnButton = tk.Button(delete_window, height=1, width=10, text="Back",
                          command=lambda: first_page(client, delete_window))
    rtnButton.pack()

    delete_window.mainloop()


if __name__ == '__main__':
    zero_page()