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


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CPU Scheduler: FCFS vs SJF")
        self.geometry("1100x640")
        self.procs = [(arr, burst) for _, arr, burst in sched.PROCESSES]
        self.build()
        self.refresh()

    # --- Layout -------------------------------------------------------------
    def build(self):
        # Process list and add/remove controls
        top = ttk.LabelFrame(self, text="Processes", padding=10)
        top.pack(fill="x", padx=12, pady=(12, 6))

        self.table = ttk.Treeview(top, columns=("name", "arr", "burst"),
                                  show="headings", height=6)
        for col, text in (("name", "Process"), ("arr", "Arrival"), ("burst", "Burst")):
            self.table.heading(col, text=text)
            self.table.column(col, width=100, anchor="center")
        self.table.pack(side="left")

        form = ttk.Frame(top, padding=(20, 0))
        form.pack(side="left", anchor="n")
        self.arr_var, self.burst_var = tk.StringVar(), tk.StringVar()
        ttk.Label(form, text="Arrival").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.arr_var, width=8).grid(row=0, column=1, padx=6)
        ttk.Label(form, text="Burst").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(form, textvariable=self.burst_var, width=8).grid(row=1, column=1, padx=6)
        ttk.Button(form, text="Add process", command=self.add).grid(row=2, column=0, columnspan=2, sticky="ew")
        ttk.Button(form, text="Remove selected", command=self.remove).grid(row=3, column=0, columnspan=2, sticky="ew", pady=4)
        ttk.Button(form, text="Reset", command=self.reset).grid(row=4, column=0, columnspan=2, sticky="ew")
        self.error = tk.Label(form, fg="red")
        self.error.grid(row=5, column=0, columnspan=2)

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
        self.compare_label = ttk.Label(box, justify="left", font=("TkFixedFont", 10))
        self.compare_label.pack(anchor="w")

    def make_panel(self, parent, title, column):
        frame = ttk.LabelFrame(parent, text=title, padding=10)
        frame.grid(row=0, column=column, sticky="nsew", padx=4)
        canvas = tk.Canvas(frame, width=GANTT_WIDTH, height=70, bg="white",
                           highlightthickness=1, highlightbackground="#cccccc")
        canvas.pack(fill="x")
        tree = ttk.Treeview(frame, columns=("p", "fin", "tat", "wait", "resp"),
                            show="headings", height=6)
        for col, text in (("p", "Process"), ("fin", "Finish"), ("tat", "Turnaround"),
                          ("wait", "Waiting"), ("resp", "Response")):
            tree.heading(col, text=text)
            tree.column(col, width=80, anchor="center")
        tree.pack(fill="x", pady=8)
        avg_label = ttk.Label(frame, font=("TkDefaultFont", 10, "bold"))
        avg_label.pack(anchor="w")
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
            self.table.insert("", "end", iid=str(i), values=(f"P{i + 1}", arr, burst))

        named = [(f"P{i + 1}", arr, burst) for i, (arr, burst) in enumerate(self.procs)]
        averages = {}
        for title, algorithm in (("FCFS", sched.fcfs), ("SJF", sched.sjf)):
            canvas, tree, avg_label = self.panels[title]
            gantt, info = algorithm(named)
            rows, avg = sched.metrics(info) if info else ([], None)
            self.draw_gantt(canvas, gantt)
            tree.delete(*tree.get_children())
            for row in rows:
                tree.insert("", "end", values=row)
            averages[title] = avg
            if avg:
                avg_label.config(text=f"Average: waiting {avg[0]:.2f}   "
                                      f"turnaround {avg[1]:.2f}   response {avg[2]:.2f}")
            else:
                avg_label.config(text="")
        self.show_comparison(averages["FCFS"], averages["SJF"])

    def draw_gantt(self, canvas, gantt):
        canvas.delete("all")
        if not gantt:
            return
        total = gantt[-1][2]
        unit = (GANTT_WIDTH - 20) / total
        for name, start, end in gantt:
            x1, x2 = 10 + start * unit, 10 + end * unit
            color = "#dddddd" if name == "idle" else COLORS[(int(name[1:]) - 1) % len(COLORS)]
            canvas.create_rectangle(x1, 10, x2, 45, fill=color, outline="black")
            canvas.create_text((x1 + x2) / 2, 27, text=name)
            canvas.create_text(x1, 57, text=str(start), font=("TkDefaultFont", 8))
        canvas.create_text(10 + total * unit, 57, text=str(total), font=("TkDefaultFont", 8))

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
