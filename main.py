import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import threading
from yt_dlp import YoutubeDL


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Youtube to MP3/MP4 Converter")
        self.resizable(False, False)
        self.iconbitmap("./images/app_logo.ico")
        self.configure(bg="#2EA9BF")
        self.window_width = 400
        self.window_height=550
        self.x = (self.winfo_screenwidth() // 2) - (self.window_width //2)
        self.y = (self.winfo_screenheight() //2) - (self.window_height // 2)
        self.geometry(f"{self.window_width}x{self.window_height}+{self.x}+{self.y}")
        self.main_title = tk.Label(self, text="Youtube to MP3/MP4 Converter", bg="#2EA9BF", font=("Inter", 16, "bold"))
        self.main_title.pack(pady=35)
        self.format_selection_label = tk.Label(self, text="Select your desired format:", bg="#2EA9BF", font=("Inter", 12))
        self.format_selection_label.place(x=40, y=100)
        self.mp3_button = tk.Button(self, text="MP3",bg="#0D2A30", fg="#2EA9BF", font=("Inter", 12), border=0, width=10, height=2, command=self.select_mp3)
        self.mp3_button.place(x=45, y=140)
        self.mp4_button = tk.Button(self, text="MP4",bg="#0D2A30", fg="#2EA9BF", font=("Inter", 12), border=0, width=10, height=2, command=self.select_mp4)
        self.mp4_button.place(x=250, y=140)
        self.url_label = tk.Label(self, text="Enter your Youtube URL here:", bg="#2EA9BF", font=("Inter", 12))
        self.url_label.place(x=40, y=220)
        self.url_entry = tk.Entry(self, width=35, font=("Inter", 12), border=0)
        self.url_entry.place(x=40, y=270)
        self.folder_path_label = tk.Label(self, text="Select or type the folder path to save the media:", bg="#2EA9BF", font=("Inter", 12))
        self.folder_path_label.place(x=40, y=310)
        self.folder_path_entry = tk.Entry(self, width=35, font=("Inter", 12), border=0)
        self.folder_path_entry.place(x=40, y=360)
        self.browse_button = tk.Button(self, text="Browse", bg="#0D2A30", fg="#2EA9BF", font=("Inter", 12), border=0, width=6, height=1, command=self.browse_folder)
        self.browse_button.place(x=40, y=390)
        self.download_button = tk.Button(self, text="Download", bg="#0D2A30", fg="#2EA9BF", font=("Inter", 12), border=0, width=20, height=2, command=self.download_media)
        self.download_button.place(x=100, y=450)
    def select_mp3(self):
        self.mp3_button.config(state="disabled")
        self.mp4_button.config(state="normal")

    def select_mp4(self):
        self.mp4_button.config(state="disabled")
        self.mp3_button.config(state="normal")

    def browse_folder(self):
        folder_path = filedialog.askdirectory(
            initialdir="/",
            title="Select a Folder"
        )
        if folder_path:
            self.folder_path_entry.delete(0, tk.END)
            self.folder_path_entry.insert(0, folder_path)

    def download_mp3(self, url, folder_path):
        ydl_opts = {
            'ffmpeg_location': 'C:/ffmpeg/bin',
            'format': 'bestaudio/best',
            'outtmpl': f'{folder_path}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred while downloading the MP3: {str(e)}")

    def download_mp4(self, url, folder_path):
        ydl_opts = {
            'ffmpeg_location': 'C:/ffmpeg/bin',
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'merge_output_format': 'mp4',
            'outtmpl': f'{folder_path}/%(title)s.%(ext)s'
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred while downloading the MP4: {str(e)}")

    def download_media(self):
        url = self.url_entry.get()
        folder_path = self.folder_path_entry.get()
        if not url:
            tk.messagebox.showerror("Error", "Please enter a Youtube URL.")
            return
        if not folder_path:
            tk.messagebox.showerror("Error", "Please select a folder to save the media.")
            return
        if self.mp3_button['state'] == 'normal' and self.mp4_button['state'] == 'normal':
            tk.messagebox.showerror("Error", "Please select a format (MP3 or MP4).")
            return
        if self.mp3_button['state'] == 'disabled':
            format = "MP3"
            download_thread = threading.Thread(target=self.download_mp3, args=(url, folder_path))
        else:
            format = "MP4"
            download_thread = threading.Thread(target=self.download_mp4, args=(url, folder_path))
        download_thread.start()
        tk.messagebox.showinfo("Download", f"Downloading {format} from {url} to {folder_path}...")

    
if __name__ == "__main__":    
    app = App()
    app.mainloop()