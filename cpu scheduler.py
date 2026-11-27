# (name, arrival, burst)
PROCESSES = [
    ("P1", 0, 9),
    ("P2", 1, 1),
    ("P3", 1, 1),
    ("P4", 4, 1),
    ("P5", 4, 8),
    ("P6", 6, 6),
]
 
def fcfs(procs):
    """First-Come First-Served: run in order of arrival"""
    order = sorted(procs, key=lambda p: p[1])  # sorted() is stable
    time, gantt, info = 0, [], {}
    for name, arr, burst in order:
        if time < arr:                      # CPU idle until the process arrives
            gantt.append(("idle", time, arr))
            time = arr
        start, end = time, time + burst
        gantt.append((name, start, end))
        info[name] = (arr, burst, start, end)
        time = end
    return gantt, info


def sjf(procs):
    """Shortest Job First (non-preemptive): among arrived processes pick the
    smallest burst; ties are broken by arrival time, then by input order."""
    remaining = list(procs)
    time, gantt, info = 0, [], {}
    while remaining:
        ready = [p for p in remaining if p[1] <= time]
        if not ready:                       # nothing has arrived: jump ahead
            nxt = min(p[1] for p in remaining)
            gantt.append(("idle", time, nxt))
            time = nxt
            continue
        p = min(ready, key=lambda x: (x[2], x[1]))  # min() keeps first on ties
        name, arr, burst = p
        start, end = time, time + burst
        gantt.append((name, start, end))
        info[name] = (arr, burst, start, end)
        time = end
        remaining.remove(p)
    return gantt, info


def metrics(info):
    rows = []
    for name, (arr, burst, start, end) in info.items():
        tat = end - arr
        rows.append((name, end, tat, tat - burst, start - arr))
    rows.sort(key=lambda r: int(r[0][1:]))
    n = len(rows)
    avg = (
        sum(r[3] for r in rows) / n,   # waiting
        sum(r[2] for r in rows) / n,   # turnaround
        sum(r[4] for r in rows) / n,   # response
    )
    return rows, avg


def report(title, gantt, info):
    rows, avg = metrics(info)
    print(f"=== {title} ===")
    print("Gantt: " + " ".join(f"| {n} {s}-{e}" for n, s, e in gantt) + " |")
    print(f"{'Proc':<6}{'Finish':<8}{'Turnaround':<12}{'Waiting':<9}{'Response'}")
    for name, fin, tat, wait, resp in rows:
        print(f"{name:<6}{fin:<8}{tat:<12}{wait:<9}{resp}")
    print(f"Average: waiting = {avg[0]:.2f}  turnaround = {avg[1]:.2f}  "
          f"response = {avg[2]:.2f}")
    print()
    return avg


def compare(a_name, a, b_name, b):
    print("=== Comparison ===")
    for i, label in enumerate(["Waiting:", "Turnaround:", "Response:"]):
        x, y = a[i], b[i]
        if abs(x - y) < 1e-9:
            verdict = f"tie ({x:.2f} vs {y:.2f})"
        elif x < y:
            verdict = f"{a_name} is better ({x:.2f} vs {y:.2f})"
        else:
            verdict = f"{b_name} is better ({y:.2f} vs {x:.2f})"
        print(f"{label:<12}{verdict}")


if __name__ == "__main__":
    g1, i1 = fcfs(PROCESSES)
    avg_fcfs = report("FCFS", g1, i1)

    g2, i2 = sjf(PROCESSES)
    avg_sjf = report("SJF", g2, i2)

    compare("FCFS", avg_fcfs, "SJF", avg_sjf)