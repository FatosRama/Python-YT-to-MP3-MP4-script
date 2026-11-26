import ctypes
import os
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from yt_dlp import YoutubeDL


# Color palette
BG = "#0B1F24"
SURFACE = "#0D2A30"
SURFACE_HOVER = "#12404A"
ACCENT = "#2EA9BF"
ACCENT_HOVER = "#3CC3DA"
TEXT = "#E6F4F7"
MUTED = "#7FA7AF"
ERROR = "#E5736B"
SUCCESS = "#5BD08A"
IG_ACCENT = "#E1306C"
IG_ACCENT_HOVER = "#F0568A"

FONT = "Segoe UI"


class HoverButton(tk.Button):
    """Flat button that changes color on hover."""

    def __init__(self, master, bg=SURFACE, hover_bg=SURFACE_HOVER, fg=ACCENT, **kwargs):
        super().__init__(master, bg=bg, fg=fg, activebackground=hover_bg, activeforeground=fg,
                         relief="flat", bd=0, cursor="hand2", **kwargs)
        self.default_bg = bg
        self.hover_bg = hover_bg
        self.bind("<Enter>", lambda e: self["state"] == "normal" and self.config(bg=self.hover_bg))
        self.bind("<Leave>", lambda e: self.config(bg=self.default_bg))

    def set_colors(self, bg, hover_bg, fg):
        self.default_bg = bg
        self.hover_bg = hover_bg
        self.config(bg=bg, fg=fg, activebackground=hover_bg, activeforeground=fg)


class ConverterTab(tk.Frame):
    """One converter page: format picker, URL, save folder, download button and progress."""

    url_label = "URL"

    def __init__(self, master, platform, accent, accent_hover, accent_fg):
        super().__init__(master, bg=BG)
        self.platform = platform
        self.accent = accent
        self.accent_hover = accent_hover
        self.accent_fg = accent_fg

        self.format = tk.StringVar(value="MP3")
        self.downloading = False
        self.last_folder = None

        self.progress_style = f"{platform}.Horizontal.TProgressbar"
        ttk.Style(self).configure(self.progress_style, troughcolor=SURFACE, background=accent,
                                  bordercolor=SURFACE, lightcolor=accent, darkcolor=accent, thickness=10)

        self.build()

    # ---------- UI construction ----------

    def build(self):
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=40, pady=(22, 24))

        tk.Label(body, text=f"{self.platform} to MP3/MP4 Converter", bg=BG, fg=self.accent,
                 font=(FONT, 20, "bold")).pack(anchor="w")
        tk.Label(body, text="Paste a link, pick a format, and hit download.", bg=BG, fg=MUTED,
                 font=(FONT, 10)).pack(anchor="w", pady=(2, 22))

        # Format toggle
        format_row = tk.Frame(body, bg=BG)
        format_row.pack(fill="x", pady=(0, 20))
        format_col = tk.Frame(format_row, bg=BG)
        format_col.pack(side="left")
        self.section_label(format_col, "FORMAT")
        toggle = tk.Frame(format_col, bg=SURFACE)
        toggle.pack(anchor="w", pady=(6, 0))
        self.mp3_button = HoverButton(toggle, text="♪  MP3  ·  Audio", font=(FONT, 11, "bold"),
                                      width=16, pady=8, command=lambda: self.select_format("MP3"))
        self.mp3_button.pack(side="left", padx=3, pady=3)
        self.mp4_button = HoverButton(toggle, text="▶  MP4  ·  Video", font=(FONT, 11, "bold"),
                                      width=16, pady=8, command=lambda: self.select_format("MP4"))
        self.mp4_button.pack(side="left", padx=(0, 3), pady=3)
        self.select_format("MP3")
        self.build_extra_options(format_row)

        # URL input
        self.section_label(body, f"{self.platform.upper()} {self.url_label}")
        url_row = tk.Frame(body, bg=BG)
        url_row.pack(fill="x", pady=(6, 20))
        self.url_entry = self.make_entry(url_row)
        HoverButton(url_row, text="Paste", font=(FONT, 10, "bold"), width=9, fg=self.accent,
                    command=self.paste_url).pack(side="left", fill="y", padx=(8, 0))

        # Folder input
        self.section_label(body, "SAVE TO")
        folder_row = tk.Frame(body, bg=BG)
        folder_row.pack(fill="x", pady=(6, 24))
        self.folder_path_entry = self.make_entry(folder_row)
        HoverButton(folder_row, text="Browse", font=(FONT, 10, "bold"), width=9, fg=self.accent,
                    command=self.browse_folder).pack(side="left", fill="y", padx=(8, 0))
        default_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.isdir(default_folder):
            self.folder_path_entry.insert(0, default_folder)

        # Download button
        self.download_button = HoverButton(body, text="Download", bg=self.accent, hover_bg=self.accent_hover,
                                           fg=self.accent_fg, font=(FONT, 13, "bold"), pady=10,
                                           command=self.download_media)
        self.download_button.pack(fill="x")

        # Progress + status
        self.progress = ttk.Progressbar(body, style=self.progress_style, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(18, 6))

        status_row = tk.Frame(body, bg=BG)
        status_row.pack(fill="x")
        self.status_label = tk.Label(status_row, text="Ready", bg=BG, fg=MUTED, font=(FONT, 10),
                                     anchor="w")
        self.status_label.pack(side="left", fill="x", expand=True)
        self.open_folder_button = HoverButton(status_row, text="Open folder", font=(FONT, 9, "bold"),
                                              fg=self.accent, padx=10, command=self.open_folder)

    def build_extra_options(self, parent):
        """Hook for platform-specific controls next to the format toggle."""

    def section_label(self, parent, text):
        tk.Label(parent, text=text, bg=BG, fg=MUTED, font=(FONT, 9, "bold")).pack(anchor="w")

    def make_entry(self, parent):
        # Wrap the entry in a frame so it gets inner padding and a focus-highlight border
        border = tk.Frame(parent, bg=SURFACE_HOVER)
        border.pack(side="left", fill="x", expand=True)
        inner = tk.Frame(border, bg=SURFACE)
        inner.pack(fill="x", padx=1, pady=1)
        entry = tk.Entry(inner, font=(FONT, 12), bg=SURFACE, fg=TEXT, insertbackground=self.accent,
                         relief="flat", bd=0)
        entry.pack(fill="x", padx=10, ipady=8)
        entry.bind("<FocusIn>", lambda e: border.config(bg=self.accent))
        entry.bind("<FocusOut>", lambda e: border.config(bg=SURFACE_HOVER))
        return entry

    # ---------- Actions ----------

    def select_format(self, fmt):
        self.format.set(fmt)
        selected, other = (self.mp3_button, self.mp4_button) if fmt == "MP3" else (self.mp4_button, self.mp3_button)
        selected.set_colors(self.accent, self.accent_hover, self.accent_fg)
        other.set_colors(SURFACE, SURFACE_HOVER, MUTED)

    def paste_url(self):
        try:
            text = self.clipboard_get().strip()
        except tk.TclError:
            return
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, text)

    def browse_folder(self):
        folder_path = filedialog.askdirectory(
            initialdir=self.folder_path_entry.get() or "/",
            title="Select a Folder"
        )
        if folder_path:
            self.folder_path_entry.delete(0, tk.END)
            self.folder_path_entry.insert(0, folder_path)

    def open_folder(self):
        if self.last_folder and os.path.isdir(self.last_folder):
            os.startfile(self.last_folder)

    def set_status(self, text, color=MUTED):
        self.status_label.config(text=text, fg=color)

    # ---------- Download ----------

    def progress_hook(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            percent = downloaded / total * 100 if total else 0
            parts = [f"Downloading… {percent:.0f}%"]
            if d.get("speed"):
                parts.append(f"{d['speed'] / 1024 / 1024:.1f} MB/s")
            if d.get("eta") is not None:
                minutes, seconds = divmod(int(d["eta"]), 60)
                parts.append(f"{minutes}:{seconds:02d} left")
            self.after(0, self.update_progress, percent, "   ·   ".join(parts))
        elif d["status"] == "finished":
            self.after(0, self.update_progress, 100, "Processing…")

    def postprocessor_hook(self, d):
        if d["status"] == "started":
            self.after(0, self.update_progress, 100, "Converting with FFmpeg…")

    def update_progress(self, percent, text):
        self.progress["value"] = percent
        self.set_status(text, self.accent)

    def download_mp3(self, url, folder_path):
        ydl_opts = {
            'ffmpeg_location': 'C:/ffmpeg/bin',
            'format': 'bestaudio/best',
            'outtmpl': f'{folder_path}/%(title)s.%(ext)s',
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        self.run_download(url, folder_path, ydl_opts)

    def download_mp4(self, url, folder_path):
        ydl_opts = {
            'ffmpeg_location': 'C:/ffmpeg/bin',
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'merge_output_format': 'mp4',
            'outtmpl': f'{folder_path}/%(title)s.%(ext)s',
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10,
            'nocheckcertificate': True
        }
        self.run_download(url, folder_path, ydl_opts)

    def run_download(self, url, folder_path, ydl_opts):
        ydl_opts.update({
            'progress_hooks': [self.progress_hook],
            'postprocessor_hooks': [self.postprocessor_hook],
            # YouTube needs a JS runtime to unlock formats; yt-dlp only enables deno by default
            'js_runtimes': {'deno': {}, 'node': {}},
            'quiet': True,
            'noprogress': True,
        })
        ydl_opts.update(self.extra_ydl_options(folder_path))
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            self.after(0, self.download_finished, False, str(e))
        else:
            self.after(0, self.download_finished, True, folder_path)

    def extra_ydl_options(self, folder_path):
        """Hook for platform-specific yt-dlp options, applied on top of the defaults."""
        return {}

    def friendly_error(self, message):
        """Hook to turn a yt-dlp error into something more helpful."""
        return message

    def download_finished(self, success, info):
        self.downloading = False
        self.download_button.config(state="normal", text="Download")
        self.download_button.set_colors(self.accent, self.accent_hover, self.accent_fg)
        if success:
            self.last_folder = info
            self.progress["value"] = 100
            self.set_status(f"✓  {self.format.get()} saved successfully", SUCCESS)
            self.open_folder_button.pack(side="right")
        else:
            self.progress["value"] = 0
            self.set_status("✕  Download failed", ERROR)
            messagebox.showerror("Error", f"An error occurred while downloading the {self.format.get()}: "
                                          f"{self.friendly_error(info)}")

    def download_media(self):
        if self.downloading:
            return
        url = self.url_entry.get().strip()
        folder_path = self.folder_path_entry.get().strip()
        if not url:
            self.set_status(f"Please enter a {self.platform} URL.", ERROR)
            self.url_entry.focus_set()
            return
        if not folder_path:
            self.set_status("Please select a folder to save the media.", ERROR)
            self.folder_path_entry.focus_set()
            return
        if not os.path.isdir(folder_path):
            self.set_status("That folder doesn't exist.", ERROR)
            self.folder_path_entry.focus_set()
            return

        self.downloading = True
        self.open_folder_button.pack_forget()
        self.progress["value"] = 0
        self.download_button.config(state="disabled", text="Downloading…")
        self.download_button.set_colors(SURFACE_HOVER, SURFACE_HOVER, MUTED)
        self.download_button.config(disabledforeground=MUTED)
        self.set_status("Starting download…", self.accent)

        target = self.download_mp3 if self.format.get() == "MP3" else self.download_mp4
        threading.Thread(target=target, args=(url, folder_path), daemon=True).start()


class InstagramTab(ConverterTab):
    """Public reels download without a login; the browser picker is for private or restricted posts."""

    url_label = "REEL URL"
    browsers = ["None", "Firefox", "Chrome", "Edge", "Brave", "Opera"]

    def build_extra_options(self, parent):
        self.browser = tk.StringVar(value="None")

        col = tk.Frame(parent, bg=BG)
        col.pack(side="right", anchor="n")
        self.section_label(col, "USE LOGIN FROM")
        picker = tk.Menubutton(col, textvariable=self.browser, bg=SURFACE, fg=TEXT,
                               activebackground=SURFACE_HOVER, activeforeground=TEXT, relief="flat",
                               bd=0, font=(FONT, 11, "bold"), width=12, pady=11, cursor="hand2",
                               indicatoron=True)
        picker.pack(anchor="w", pady=(6, 0))
        menu = tk.Menu(picker, tearoff=0, bg=SURFACE, fg=TEXT, activebackground=self.accent,
                       activeforeground=TEXT, bd=0, font=(FONT, 10))
        for name in self.browsers:
            menu.add_radiobutton(label=name, variable=self.browser, value=name)
        picker.config(menu=menu)

    def extra_ydl_options(self, folder_path):
        opts = {
            # Instagram titles are all "Video by <user>", so add the post ID to keep names unique
            'outtmpl': f'{folder_path}/%(title)s [%(id)s].%(ext)s',
            # Some reels have no sound: MP3 should fail clearly, MP4 can still save the silent video
            'format': ('bestaudio/best[acodec!=none]' if self.format.get() == "MP3"
                       else 'bestvideo*+bestaudio/best'),
        }
        if self.browser.get() != "None":
            opts['cookiesfrombrowser'] = (self.browser.get().lower(),)
        return opts

    def friendly_error(self, message):
        lowered = message.lower()
        if "requested format is not available" in lowered and self.format.get() == "MP3":
            return "This reel has no sound, so there's no audio to save as an MP3."
        if "empty media response" in lowered or "login" in lowered:
            return ("Instagram wouldn't share this post without a login (it may be private or "
                    "age-restricted).\n\nLog in to Instagram in your browser, then choose that browser "
                    "under \"Use login from\" and try again.")
        if "cookie" in lowered or "decrypt" in lowered:
            return (f"Couldn't read the login from {self.browser.get()}. Close the browser completely "
                    "and try again, or use Firefox (Chrome and Edge often lock their cookies).\n\n"
                    f"Details: {message}")
        return message


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube & Instagram Converter")
        self.resizable(False, False)
        self.overrideredirect(True)
        self.iconbitmap("./images/app_logo.ico")
        self.window_width = 720
        self.window_height = 640
        self.x = (self.winfo_screenwidth() // 2) - (self.window_width // 2)
        self.y = (self.winfo_screenheight() // 2) - (self.window_height // 2)
        self.geometry(f"{self.window_width}x{self.window_height}+{self.x}+{self.y}")
        self.configure(bg=ACCENT)  # Shows as a 1px border around the window

        ttk.Style(self).theme_use("clam")

        self.root_frame = tk.Frame(self, bg=BG)
        self.root_frame.pack(fill="both", expand=True, padx=1, pady=1)

        self.build_title_bar()
        self.build_tabs()

        self.bind("<Return>", lambda e: self.current_tab.download_media())
        self.bind("<Map>", self.on_restore)
        self.after(10, self.show_in_taskbar)

    # ---------- UI construction ----------

    def build_title_bar(self):
        bar = tk.Frame(self.root_frame, bg=SURFACE, height=40)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        try:
            logo = tk.PhotoImage(file="./images/app_logo.png")
            self.logo_image = logo.subsample(max(1, logo.width() // 28))
            tk.Label(bar, image=self.logo_image, bg=SURFACE).pack(side="left", padx=(12, 6))
        except tk.TclError:
            pass

        title = tk.Label(bar, text="Media Converter", bg=SURFACE, fg=TEXT, font=(FONT, 10, "bold"))
        title.pack(side="left")

        close_btn = HoverButton(bar, text="✕", bg=SURFACE, hover_bg="#C0392B", fg=TEXT,
                                font=(FONT, 11), width=4, command=self.destroy)
        close_btn.pack(side="right", fill="y")
        min_btn = HoverButton(bar, text="—", bg=SURFACE, hover_bg=SURFACE_HOVER, fg=TEXT,
                              font=(FONT, 10), width=4, command=self.minimize)
        min_btn.pack(side="right", fill="y")

        # Let the user drag the borderless window around by its title bar
        for widget in (bar, title):
            widget.bind("<ButtonPress-1>", self.start_move)
            widget.bind("<B1-Motion>", self.do_move)

    def build_tabs(self):
        tab_bar = tk.Frame(self.root_frame, bg=BG)
        tab_bar.pack(fill="x", padx=40, pady=(14, 0))
        tk.Frame(self.root_frame, bg=SURFACE_HOVER, height=1).pack(fill="x", padx=40)

        content = tk.Frame(self.root_frame, bg=BG)
        content.pack(fill="both", expand=True)

        self.tabs = {
            "YouTube": ConverterTab(content, "YouTube", ACCENT, ACCENT_HOVER, BG),
            "Instagram": InstagramTab(content, "Instagram", IG_ACCENT, IG_ACCENT_HOVER, TEXT),
        }
        icons = {"YouTube": "▶", "Instagram": "◎"}

        self.tab_buttons = {}
        for name in self.tabs:
            holder = tk.Frame(tab_bar, bg=BG)
            holder.pack(side="left", padx=(0, 6))
            button = HoverButton(holder, text=f"{icons[name]}  {name}", bg=BG, hover_bg=SURFACE,
                                 fg=MUTED, font=(FONT, 11, "bold"), padx=16, pady=6,
                                 command=lambda n=name: self.show_tab(n))
            button.pack()
            underline = tk.Frame(holder, bg=BG, height=3)
            underline.pack(fill="x")
            self.tab_buttons[name] = (button, underline)

        self.show_tab("YouTube")

    def show_tab(self, name):
        for tab_name, (button, underline) in self.tab_buttons.items():
            tab = self.tabs[tab_name]
            if tab_name == name:
                button.set_colors(BG, SURFACE, tab.accent)
                underline.config(bg=tab.accent)
                tab.pack(fill="both", expand=True)
            else:
                button.set_colors(BG, SURFACE, MUTED)
                underline.config(bg=BG)
                tab.pack_forget()
        self.current_tab = self.tabs[name]
        self.configure(bg=self.current_tab.accent)  # Window border follows the active tab's color

    # ---------- Window behaviour ----------

    def start_move(self, event):
        self.drag_x = event.x_root - self.winfo_x()
        self.drag_y = event.y_root - self.winfo_y()

    def do_move(self, event):
        self.geometry(f"+{event.x_root - self.drag_x}+{event.y_root - self.drag_y}")

    def minimize(self):
        # Borderless windows can't be iconified, so temporarily restore the frame
        self.overrideredirect(False)
        self.iconify()

    def on_restore(self, event):
        if self.state() == "normal" and not self.overrideredirect():
            self.overrideredirect(True)
            self.show_in_taskbar()

    def show_in_taskbar(self):
        # Borderless windows are hidden from the taskbar by default, so flag it as an app window
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = (style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        # The window has to be re-shown for the style change to take effect
        self.withdraw()
        self.after(10, self.deiconify)


if __name__ == "__main__":
    # Give the app its own taskbar identity so it shows its icon instead of Python's
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("YTtoMP3.Converter")
    app = App()
    app.mainloop()
