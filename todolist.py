import tkinter as tk
from tkinter import messagebox, Scrollbar, Toplevel
from tkcalendar import Calendar
import sqlite3
from datetime import datetime

# ----------------- DATABASE SETUP -----------------
conn = sqlite3.connect('todo.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    task TEXT NOT NULL,
    status TEXT NOT NULL,
    due_date TEXT
)''')
conn.commit()

# ----------------- FUNCTIONS -----------------
def add_task():
    task = task_entry.get()
    due_date = due_entry.get()

    if task:
        try:
            if due_date:
                datetime.strptime(due_date, "%Y-%m-%d")  # Validate format
            c.execute("INSERT INTO tasks (task, status, due_date) VALUES (?, ?, ?)",
                      (task, "Pending", due_date))
            conn.commit()
            task_entry.delete(0, tk.END)
            due_entry.delete(0, tk.END)
            load_tasks()
        except ValueError:
            messagebox.showwarning("Date Error", "Due date must be in YYYY-MM-DD format.")
    else:
        messagebox.showwarning("Input Error", "Task cannot be empty!")

def delete_task():
    try:
        selected = task_listbox.curselection()[0]
        task_id = task_ids[selected]
        c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        load_tasks()
    except IndexError:
        messagebox.showwarning("Selection Error", "Select a task to delete.")

def mark_done():
    try:
        selected = task_listbox.curselection()[0]
        task_id = task_ids[selected]
        c.execute("UPDATE tasks SET status=? WHERE id=?", ("Done", task_id))
        conn.commit()
        load_tasks()
    except IndexError:
        messagebox.showwarning("Selection Error", "Select a task to mark as done.")

def load_tasks():
    task_listbox.delete(0, tk.END)
    global task_ids
    task_ids = []
    today = datetime.now().date()

    for row in c.execute("SELECT id, task, status, due_date FROM tasks"):
        task_id, task, status, due_date = row
        icon = "✅" if status == "Done" else "🕒"
        display = f"{icon} {task}"

        if due_date:
            try:
                due = datetime.strptime(due_date, "%Y-%m-%d").date()
                if due < today and status != "Done":
                    display += f" [🔴 OVERDUE: {due_date}]"
                else:
                    display += f" [📅 {due_date}]"
            except:
                display += f" [📅 {due_date}]"

        task_listbox.insert(tk.END, display)
        task_ids.append(task_id)

def open_calendar():
    top = Toplevel(root)
    top.title("Pick a Date")
    top.configure(bg="#2d2d44")

    cal = Calendar(top, selectmode='day', year=2025, month=5, day=29,
                   background="#00cec9", foreground="black", headersbackground="#00cec9")
    cal.pack(pady=20)

    def pick_date():
        due_entry.delete(0, tk.END)
        due_entry.insert(0, cal.get_date())
        top.destroy()

    tk.Button(top, text="Select Date", command=pick_date,
              font=("Arial", 12), bg="#00b894", fg="white").pack(pady=10)

# ----------------- GUI SETUP -----------------
root = tk.Tk()
root.title("📝 RC Spot - Pro To-Do App")
root.geometry("550x600")
root.configure(bg="#1f1f2e")

title = tk.Label(root, text="Your To-Do List", font=("Arial", 20, "bold"),
                 bg="#1f1f2e", fg="#00ffd5")
title.pack(pady=10)

frame = tk.Frame(root, bg="#1f1f2e")
frame.pack(pady=5)

task_entry = tk.Entry(frame, width=32, font=("Arial", 14))
task_entry.grid(row=0, column=0, padx=5, pady=5, columnspan=2)

due_entry = tk.Entry(frame, width=20, font=("Arial", 12))
due_entry.grid(row=1, column=0, pady=5, sticky="w")

due_label = tk.Label(frame, text="Due Date (YYYY-MM-DD)", font=("Arial", 10),
                     bg="#1f1f2e", fg="#ffffff")
due_label.grid(row=1, column=1, sticky="w")

cal_button = tk.Button(frame, text="📅 Calendar", command=open_calendar,
                       font=("Arial", 10), bg="#6c5ce7", fg="white", width=12)
cal_button.grid(row=1, column=2, padx=5)

add_button = tk.Button(frame, text="➕ Add Task", width=40, bg="#00b894", fg="white",
                       font=("Arial", 12), command=add_task)
add_button.grid(row=2, column=0, columnspan=3, pady=10)

btn_frame = tk.Frame(root, bg="#1f1f2e")
btn_frame.pack(pady=5)

done_button = tk.Button(btn_frame, text="✅ Mark Done", width=15,
                        bg="#0984e3", fg="white", font=("Arial", 11), command=mark_done)
done_button.grid(row=0, column=0, padx=10)

del_button = tk.Button(btn_frame, text="🗑️ Delete", width=15,
                       bg="#d63031", fg="white", font=("Arial", 11), command=delete_task)
del_button.grid(row=0, column=1)

# Listbox with scrollbar
list_frame = tk.Frame(root, bg="#1f1f2e")
list_frame.pack(pady=10)

scrollbar = Scrollbar(list_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

task_listbox = tk.Listbox(list_frame, width=60, height=15, font=("Arial", 12),
                          bg="#2d2d44", fg="white", bd=0, selectbackground="#00cec9",
                          yscrollcommand=scrollbar.set)
task_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

scrollbar.config(command=task_listbox.yview)

load_tasks()

root.mainloop()
