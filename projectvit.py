import tkinter as tk
from tkinter import messagebox
import random
import time
import json
import os

ss = os.path.dirname(os.path.abspath(__file__))
Memoryfile = os.path.join(ss, "memory_game_best.json")


def load_best_memory():
    if os.path.exists(Memoryfile):
        try:
            with open(Memoryfile, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_best_memory(data):
    try:
        with open(Memoryfile, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

root = tk.Tk()
root.title("Memory Match — Focus Break")
root.geometry("520x560")
root.config(bg="#fff9e6")

tk.Label(root,
         text="🧠 Memory Match",
         font=("Segoe UI", 18, "bold"),
         bg="#fff5db").pack(pady=10)

EMOJIS = ["🍎", "🍌", "🍇", "🍓", "🍒", "🥝", "🍍", "🍑"]  # 8 pairs -> 16 cards
cards = EMOJIS * 2
random.shuffle(cards)

moves_var = tk.IntVar(value=0)
time_var = tk.IntVar(value=0)
pairs_var = tk.IntVar(value=0)

info_frame = tk.Frame(root, bg="#fff9e6")
info_frame.pack(pady=4)
tk.Label(info_frame, text="Moves:", bg="#fff9e6").grid(row=0, column=0, padx=6)
tk.Label(info_frame, textvariable=moves_var, bg="#fff9e6").grid(row=0, column=1, padx=6)
tk.Label(info_frame, text="Time(s):", bg="#fff9e6").grid(row=0, column=2, padx=6)
tk.Label(info_frame, textvariable=time_var, bg="#fff9e6").grid(row=0, column=3, padx=6)
tk.Label(info_frame, text="Pairs:", bg="#fff9e6").grid(row=0, column=4, padx=6)
tk.Label(info_frame, textvariable=pairs_var, bg="#fff9e6").grid(row=0, column=5, padx=6)

best = load_best_memory()
if "moves" in best:
    best_label = tk.Label(root,
                          text=f"Best: {best['moves']} moves, {best['time']}s",
                          bg="#fff9e6")
else:
    best_label = tk.Label(root, text="Best: —", bg="#fff9e6")
best_label.pack(pady=6)

grid = tk.Frame(root, bg="#fff9e6")
grid.pack(pady=8)

buttons = []
revealed = [False] * 16
matched = [False] * 16
first_pick = None
lock_flag = False
start_time = None


def update_timer():
    """Update shown time every 500 ms while game running."""
    if start_time is not None and pairs_var.get() < len(EMOJIS):
        time_var.set(int(time.time() - start_time))
        root.after(500, update_timer)


def check_match(a, b):
    global first_pick, lock_flag, start_time

    if cards[a] == cards[b]:
        matched[a] = matched[b] = True
        pairs_var.set(pairs_var.get() + 1)
        buttons[a].config(bg="#d4ffd9")
        buttons[b].config(bg="#d4ffd9")
    else:
        revealed[a] = revealed[b] = False
        buttons[a].config(text="", state="normal")
        buttons[b].config(text="", state="normal")

    first_pick = None
    lock_flag = False

    if pairs_var.get() == len(EMOJIS):
        total_time = int(time.time() - start_time) if start_time else 0
        moves = moves_var.get()

        prev = load_best_memory()
        better = False
        if "moves" not in prev:
            better = True
        elif moves < prev["moves"]:
            better = True
        elif moves == prev["moves"] and total_time < prev.get("time", 10**9):
            better = True

        if better:
            save_best_memory({"moves": moves, "time": total_time})
            best_label.config(text=f"Best: {moves} moves, {total_time}s")

        messagebox.showinfo("🎉 Well done!",
                            f"You finished in {moves} moves and {total_time} seconds.")


def reveal(i):
    global first_pick, lock_flag, start_time

    if lock_flag or revealed[i] or matched[i]:
        return

    if start_time is None:
        start_time = time.time()
        update_timer()

    buttons[i].config(text=cards[i], state="disabled")
    revealed[i] = True

    if first_pick is None:
        first_pick = i
    else:
        lock_flag = True
        moves_var.set(moves_var.get() + 1)
        root.after(600, lambda: check_match(first_pick, i))


def reset_board():
    global cards, revealed, matched, first_pick, lock_flag, start_time
    random.shuffle(cards)
    for i, b in enumerate(buttons):
        b.config(text="", state="normal", bg="SystemButtonFace")
        revealed[i] = False
        matched[i] = False
    moves_var.set(0)
    time_var.set(0)
    pairs_var.set(0)
    first_pick = None
    lock_flag = False
    start_time = None

for idx in range(16):
    btn = tk.Button(
        grid,
        text="",
        width=6,
        height=3,
        font=("Segoe UI", 20),
        command=lambda x=idx: reveal(x)
    )
    btn.grid(row=idx // 4, column=idx % 4, padx=6, pady=6)
    buttons.append(btn)

ctrl = tk.Frame(root, bg="#fff9e6")
ctrl.pack(pady=10)
tk.Button(ctrl, text="Reset / Shuffle",
          command=reset_board,
          bg="#6aa84f", fg="white").pack(side="left", padx=8)
tk.Button(ctrl, text="Close",
          command=root.destroy,
          bg="#a64d79", fg="white").pack(side="left", padx=8)

root.mainloop()
