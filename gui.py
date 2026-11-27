import importlib.util
import os
import tkinter as tk
from tkinter import ttk

# --- Load the original scheduler file that sits next to this one -----------
# Its name has a space in it, so a normal "import" would not work.
HERE = os.path.dirname(os.path.abspath(__file__))


def load_scheduler():
    for name in ("cpu scheduler.py", "cpu_scheduler.py"):
        path = os.path.join(HERE, name)
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location("cpu_scheduler", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise SystemExit('Could not find "cpu scheduler.py" next to gui.py')


sched = load_scheduler()

COLORS = ["#8ecae6", "#ffb703", "#b7e4c7", "#f4a6c0", "#e9d985", "#a9b8f0"]
GANTT_WIDTH = 500

DARK = {
    "bg": "#101827",
    "panel": "#172234",
    "panel_alt": "#1d2a3d",
    "border": "#314158",
    "text": "#edf4ff",
    "muted": "#9fb0c5",
    "accent": "#64a8ff",
    "accent_hover": "#82bbff",
    "danger": "#ff7b7b",
    "canvas": "#111b2b",
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CPU Scheduler: FCFS vs SJF")
        self.geometry("1180x720")
        self.minsize(980, 680)
        self.procs = [(arr, burst) for _, arr, burst in sched.PROCESSES]
        self.configure(bg=DARK["bg"])
        self.setup_theme()
        self.build()
        self.refresh()

    def setup_theme(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure(".", background=DARK["bg"], foreground=DARK["text"],
                        fieldbackground=DARK["panel_alt"], bordercolor=DARK["border"],
                        lightcolor=DARK["border"], darkcolor=DARK["border"])
        style.configure("TFrame", background=DARK["bg"])
        style.configure("Card.TFrame", background=DARK["panel"])
        style.configure("TLabelframe", background=DARK["panel"], foreground=DARK["text"],
                        bordercolor=DARK["border"], borderwidth=1)
        style.configure("TLabelframe.Label", background=DARK["panel"],
                        foreground=DARK["accent"], font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", background=DARK["panel"], foreground=DARK["text"],
                        font=("Segoe UI", 10), anchor="w")
        style.configure("Muted.TLabel", background=DARK["panel"],
                        foreground=DARK["muted"], font=("Segoe UI", 9))
        style.configure("TButton", background=DARK["accent"], foreground="#08111f",
                        font=("Segoe UI", 9, "bold"), bordercolor=DARK["accent"],
                        focusthickness=2, focuscolor=DARK["accent_hover"], padding=(12, 9))
        style.map("TButton",
                  background=[("active", DARK["accent_hover"]), ("pressed", "#4b91df")],
                  foreground=[("disabled", DARK["muted"])])
        style.configure("Secondary.TButton", background=DARK["panel_alt"],
                        foreground=DARK["text"], bordercolor=DARK["border"],
                        font=("Segoe UI", 9, "bold"), padding=(12, 9))
        style.map("Secondary.TButton",
                  background=[("active", "#26364d"), ("pressed", "#344762")],
                  foreground=[("active", "#ffffff")])
        style.configure("TEntry", fieldbackground=DARK["panel_alt"],
                        foreground=DARK["text"], insertcolor=DARK["text"],
                        bordercolor=DARK["border"], padding=(8, 7))
        style.map("TEntry",
                  bordercolor=[("focus", DARK["accent"])],
                  lightcolor=[("focus", DARK["accent"])],
                  darkcolor=[("focus", DARK["accent"])])
        style.configure("Treeview", background=DARK["panel_alt"],
                        foreground=DARK["text"], fieldbackground=DARK["panel_alt"],
                        bordercolor=DARK["border"], rowheight=32,
                        font=("Segoe UI", 9))
        style.configure("Compact.Treeview", background=DARK["panel_alt"],
                        foreground=DARK["text"], fieldbackground=DARK["panel_alt"],
                        bordercolor=DARK["border"], rowheight=28,
                        font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background=DARK["border"],
                        foreground=DARK["text"], font=("Segoe UI", 9, "bold"),
                        relief="flat", padding=(6, 8))
        style.map("Treeview", background=[("selected", "#315d91")],
                  foreground=[("selected", "#ffffff")])
        style.map("Treeview.Heading",
                  background=[("active", "#3b5070")])

    # --- Layout -------------------------------------------------------------
    def build(self):
        header = tk.Frame(self, bg=DARK["bg"], height=72)
        header.pack(fill="x", padx=12, pady=(10, 4))
        tk.Label(header, text="CPU Scheduler",
                 bg=DARK["bg"], fg=DARK["text"],
                 font=("Segoe UI", 20, "bold")).pack(side="left", pady=12)
        badge = tk.Label(header, text="  FCFS  /  SJF  ",
                         bg=DARK["panel_alt"], fg=DARK["accent"],
                         font=("Segoe UI", 10, "bold"), padx=10, pady=6)
        badge.pack(side="right", pady=14)

        # Process list and add/remove controls
        top = ttk.LabelFrame(self, text="Processes", padding=10)
        top.pack(fill="x", padx=12, pady=(4, 8))

        self.table = ttk.Treeview(top, columns=("name", "arr", "burst"),
                                  show="headings", height=6)
        for col, text in (("name", "Process"), ("arr", "Arrival"), ("burst", "Burst")):
            self.table.heading(col, text=text)
            self.table.column(col, width=110, anchor="center")
        self.table.tag_configure("even", background=DARK["panel_alt"])
        self.table.tag_configure("odd", background="#202f43")
        self.table.pack(side="left", padx=(0, 8))

        form = ttk.Frame(top, padding=(12, 0), style="Card.TFrame")
        form.pack(side="left", fill="both", expand=True, anchor="n")
        self.arr_var, self.burst_var = tk.StringVar(), tk.StringVar()
        ttk.Label(form, text="Arrival").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(2, 6))
        ttk.Entry(form, textvariable=self.arr_var, width=10).grid(row=0, column=1, padx=6)
        ttk.Label(form, text="Burst").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=6)
        ttk.Entry(form, textvariable=self.burst_var, width=10).grid(row=1, column=1, padx=6)
        ttk.Button(form, text="Add process", command=self.add).grid(row=2, column=0, columnspan=2, sticky="ew")
        ttk.Button(form, text="Remove selected", command=self.remove, style="Secondary.TButton").grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Button(form, text="Reset", command=self.reset, style="Secondary.TButton").grid(row=4, column=0, columnspan=2, sticky="ew")
        self.error = tk.Label(form, bg=DARK["panel"], fg=DARK["danger"],
                              font=("Segoe UI", 9), justify="left")
        self.error.grid(row=5, column=0, columnspan=2, pady=(6, 0))

        self.arr_var.trace_add("write", lambda *_: self.error.config(text=""))
        self.burst_var.trace_add("write", lambda *_: self.error.config(text=""))
        self.bind("<Return>", lambda _event: self.add())

        # FCFS and SJF side by side
        middle = ttk.Frame(self)
        middle.pack(fill="both", expand=True, padx=12)
        middle.columnconfigure((0, 1), weight=1, uniform="a")
        self.panels = {}
        for col, title in enumerate(("FCFS", "SJF")):
            self.panels[title] = self.make_panel(middle, title, col)

        # Comparison text
        box = ttk.LabelFrame(self, text="Comparison", padding=10)
        box.pack(fill="x", padx=12, pady=(6, 12))
        self.compare_label = ttk.Label(box, justify="left",
                                       font=("Consolas", 10))
        self.compare_label.pack(anchor="w", padx=4)

    def make_panel(self, parent, title, column):
        frame = ttk.LabelFrame(parent, text=title, padding=10)
        frame.grid(row=0, column=column, sticky="nsew", padx=4)
        canvas = tk.Canvas(frame, width=GANTT_WIDTH, height=74, bg=DARK["canvas"],
                           highlightthickness=1, highlightbackground=DARK["border"])
        canvas.gantt = []
        canvas.pack(fill="x", pady=(0, 8))
        tree = ttk.Treeview(frame, columns=("p", "fin", "tat", "wait", "resp"),
                            show="headings", height=6, style="Compact.Treeview")
        for col, text in (("p", "Process"), ("fin", "Finish"), ("tat", "Turnaround"),
                          ("wait", "Waiting"), ("resp", "Response")):
            tree.heading(col, text=text)
            tree.column(col, width=80, anchor="center")
        tree.tag_configure("even", background=DARK["panel_alt"])
        tree.tag_configure("odd", background="#202f43")
        tree.pack(fill="both", expand=True, pady=(0, 8))
        avg_label = ttk.Label(frame, font=("Segoe UI", 10, "bold"),
                              foreground=DARK["accent"])
        avg_label.pack(anchor="w", pady=(2, 2))
        canvas.bind("<Configure>", lambda _event, c=canvas:
                    self.draw_gantt(c, getattr(c, "gantt", [])))
        return canvas, tree, avg_label

    # --- Buttons ------------------------------------------------------------
    def add(self):
        try:
            arr, burst = int(self.arr_var.get()), int(self.burst_var.get())
            if arr < 0 or burst < 1:
                raise ValueError
        except ValueError:
            self.error.config(text="Arrival >= 0, burst >= 1\n(whole numbers)")
            return
        self.error.config(text="")
        self.procs.append((arr, burst))
        self.arr_var.set("")
        self.burst_var.set("")
        self.refresh()

    def remove(self):
        selected = self.table.selection()
        if selected:
            del self.procs[int(selected[0])]
            self.refresh()

    def reset(self):
        self.procs = [(arr, burst) for _, arr, burst in sched.PROCESSES]
        self.refresh()

    # --- Show everything ----------------------------------------------------
    def refresh(self):
        self.table.delete(*self.table.get_children())
        for i, (arr, burst) in enumerate(self.procs):
            tag = "even" if i % 2 == 0 else "odd"
            self.table.insert("", "end", iid=str(i), values=(f"P{i + 1}", arr, burst),
                              tags=(tag,))

        named = [(f"P{i + 1}", arr, burst) for i, (arr, burst) in enumerate(self.procs)]
        averages = {}
        for title, algorithm in (("FCFS", sched.fcfs), ("SJF", sched.sjf)):
            canvas, tree, avg_label = self.panels[title]
            gantt, info = algorithm(named)
            rows, avg = sched.metrics(info) if info else ([], None)
            self.draw_gantt(canvas, gantt)
            tree.delete(*tree.get_children())
            for i, row in enumerate(rows):
                tag = "even" if i % 2 == 0 else "odd"
                tree.insert("", "end", values=row, tags=(tag,))
            averages[title] = avg
            if avg:
                avg_label.config(text=f"Average: waiting {avg[0]:.2f}   "
                                      f"turnaround {avg[1]:.2f}   response {avg[2]:.2f}")
            else:
                avg_label.config(text="")
        self.show_comparison(averages["FCFS"], averages["SJF"])

    def draw_gantt(self, canvas, gantt):
        canvas.delete("all")
        canvas.gantt = gantt
        if not gantt:
            width = max(canvas.winfo_width(), GANTT_WIDTH)
            canvas.create_text(width / 2, 37, text="No timeline",
                               fill=DARK["muted"], font=("Segoe UI", 9))
            return
        total = gantt[-1][2]
        if total <= 0:
            return
        width = max(canvas.winfo_width(), GANTT_WIDTH)
        unit = (width - 20) / total
        for name, start, end in gantt:
            x1, x2 = 10 + start * unit, 10 + end * unit
            color = "#3a4658" if name == "idle" else COLORS[(int(name[1:]) - 1) % len(COLORS)]
            canvas.create_rectangle(x1, 10, x2, 45, fill=color,
                                    outline=DARK["canvas"], width=1)
            canvas.create_text((x1 + x2) / 2, 27, text=name,
                               fill="#101827", font=("Segoe UI", 9, "bold"))
            canvas.create_text(x1, 57, text=str(start), fill=DARK["muted"],
                               font=("Consolas", 8))
        canvas.create_text(10 + total * unit, 57, text=str(total),
                           fill=DARK["muted"], font=("Consolas", 8))

    def show_comparison(self, fcfs_avg, sjf_avg):
        if not fcfs_avg or not sjf_avg:
            self.compare_label.config(text="Add a process to compare.")
            return
        lines = []
        for i, label in enumerate(("Waiting:", "Turnaround:", "Response:")):
            x, y = fcfs_avg[i], sjf_avg[i]
            if abs(x - y) < 1e-9:
                verdict = f"tie ({x:.2f} vs {y:.2f})"
            elif x < y:
                verdict = f"FCFS is better ({x:.2f} vs {y:.2f})"
            else:
                verdict = f"SJF is better ({y:.2f} vs {x:.2f})"
            lines.append(f"{label:<12}{verdict}")
        self.compare_label.config(text="\n".join(lines))


if __name__ == "__main__":
    App().mainloop()
