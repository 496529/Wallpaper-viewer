from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import os


class WallpaperViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Wallpaper Viewer")
        self.root.geometry("720x620")
        self.root.configure(bg="#0d0d1a")
        self.root.resizable(True, True)

        self.img_array = []
        self.img_paths = []
        self.counter = 0
        self.slideshow_active = False
        self.slideshow_id = None

        self.setup_ui()
        self.load_default_images()

    def setup_ui(self):
        # ── Title
        Label(self.root, text="🖼  Wallpaper Viewer",
              font=("Segoe UI", 18, "bold"),
              bg="#0d0d1a", fg="#c9c9ff").pack(pady=(14, 2))

        # ── Counter
        self.counter_label = Label(self.root, text="0 / 0",
                                   font=("Segoe UI", 9),
                                   bg="#0d0d1a", fg="#5555aa")
        self.counter_label.pack()

        # ── Image frame with glow border
        outer = Frame(self.root, bg="#3a3a7a", padx=2, pady=2)
        outer.pack(padx=30, pady=8)
        inner = Frame(outer, bg="#12122a")
        inner.pack()

        self.img_label = Label(inner, bg="#12122a",
                               text="No images loaded",
                               font=("Segoe UI", 13),
                               fg="#44447a", width=64, height=18)
        self.img_label.pack(padx=4, pady=4)

        # ── Filename
        self.filename_label = Label(self.root, text="",
                                    font=("Segoe UI", 8),
                                    bg="#0d0d1a", fg="#55557a")
        self.filename_label.pack(pady=(0, 6))

        # ── Navigation row
        nav = Frame(self.root, bg="#0d0d1a")
        nav.pack(pady=4)
        self._btn(nav, "◀  Prev",     self.prev_img,        "#6c63ff").pack(side=LEFT, padx=6)
        self._btn(nav, "Next  ▶",     self.next_img,        "#6c63ff").pack(side=LEFT, padx=6)

        # ── Action row
        act = Frame(self.root, bg="#0d0d1a")
        act.pack(pady=4)
        self._btn(act, "➕  Add Photo",  self.add_photo,       "#22c55e").pack(side=LEFT, padx=6)
        self.slide_btn = self._btn(act, "▶  Slideshow", self.toggle_slideshow, "#f59e0b")
        self.slide_btn.pack(side=LEFT, padx=6)
        self._btn(act, "🗑  Remove",     self.remove_img,      "#ef4444").pack(side=LEFT, padx=6)

    def _btn(self, parent, text, command, color):
        """Create a styled, animated button."""
        dark  = self._shade(color, -40)
        light = self._shade(color, +30)
        b = Button(parent, text=text, command=command,
                   bg=color, fg="white",
                   font=("Segoe UI", 10, "bold"),
                   relief="flat", bd=0, padx=16, pady=9,
                   cursor="hand2",
                   activebackground=dark, activeforeground="white")
        b.bind("<Enter>",          lambda e: b.config(bg=light))
        b.bind("<Leave>",          lambda e: b.config(bg=color))
        b.bind("<ButtonPress-1>",  lambda e: b.config(bg=dark))
        b.bind("<ButtonRelease-1>",lambda e: b.config(bg=color))
        return b

    @staticmethod
    def _shade(hex_color, delta):
        r = max(0, min(255, int(hex_color[1:3], 16) + delta))
        g = max(0, min(255, int(hex_color[3:5], 16) + delta))
        b = max(0, min(255, int(hex_color[5:7], 16) + delta))
        return f"#{r:02x}{g:02x}{b:02x}"

    def load_default_images(self):
        folder = "wallpaper_viewer_apk_images"
        if os.path.exists(folder):
            for f in sorted(os.listdir(folder)):
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                    self._add_path(os.path.join(folder, f))
        self._refresh()

    def _add_path(self, path):
        try:
            img = Image.open(path).convert("RGB")
            img.thumbnail((480, 320), Image.LANCZOS)
            # Center on a fixed canvas so all images are the same size
            canvas = Image.new("RGB", (480, 320), (18, 18, 42))
            x = (480 - img.width)  // 2
            y = (320 - img.height) // 2
            canvas.paste(img, (x, y))
            self.img_array.append(ImageTk.PhotoImage(canvas))
            self.img_paths.append(path)
        except Exception as e:
            print(f"Skipped {path}: {e}")

    def _refresh(self):
        if self.img_array:
            self.img_label.config(image=self.img_array[self.counter],
                                  text="", width=0, height=0)
            total = len(self.img_array)
            self.counter_label.config(text=f"{self.counter + 1} / {total}")
            self.filename_label.config(
                text=os.path.basename(self.img_paths[self.counter]))
        else:
            self.img_label.config(image="", text="No images loaded",
                                  width=64, height=18)
            self.counter_label.config(text="0 / 0")
            self.filename_label.config(text="")

    def next_img(self):
        if self.img_array:
            self.counter = (self.counter + 1) % len(self.img_array)
            self._refresh()

    def prev_img(self):
        if self.img_array:
            self.counter = (self.counter - 1) % len(self.img_array)
            self._refresh()

    def add_photo(self):
        types = [("Images", "*.jpg *.jpeg *.png *.bmp *.gif *.webp"), ("All", "*.*")]
        paths = filedialog.askopenfilenames(title="Select Images", filetypes=types)
        added = 0
        for p in paths:
            if p not in self.img_paths:
                self._add_path(p)
                added += 1
        if added:
            self.counter = len(self.img_array) - 1
            self._refresh()

    def remove_img(self):
        if self.img_array:
            self.img_array.pop(self.counter)
            self.img_paths.pop(self.counter)
            if self.counter >= len(self.img_array) and self.counter > 0:
                self.counter -= 1
            self._refresh()

    def toggle_slideshow(self):
        if self.slideshow_active:
            self.slideshow_active = False
            if self.slideshow_id:
                self.root.after_cancel(self.slideshow_id)
            self.slide_btn.config(text="▶  Slideshow")
        else:
            self.slideshow_active = True
            self.slide_btn.config(text="⏹  Stop")
            self._run_slideshow()

    def _run_slideshow(self):
        if self.slideshow_active and self.img_array:
            self.next_img()
            self.slideshow_id = self.root.after(2500, self._run_slideshow)


if __name__ == "__main__":
    root = Tk()
    WallpaperViewer(root)
    root.mainloop()
