import tkinter as tk
from tkinter import filedialog

def select_folder_path():
    # Hide the main window if you don't need it
    # root.withdraw() 
    
    folder_path = filedialog.askdirectory(
        initialdir="/", # Start directory for the dialog
        title="Select a Folder"
    )

    if folder_path:
        print("Selected folder path:", folder_path)
        # You can also display the path in a Tkinter Entry widget
        # entry_widget.delete(0, tk.END)
        # entry_widget.insert(0, folder_path)

# Example usage in a Tkinter GUI:
root = tk.Tk()
root.title("Folder Path Selector")
root.geometry("300x150")

# Button to open the folder dialog
select_button = tk.Button(root, text="Select Folder", command=select_folder_path)
select_button.pack(pady=20)

root.mainloop()
