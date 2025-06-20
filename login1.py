import tkinter as tk
from tkinter import messagebox
import sqlite3
import subprocess

DB_FILE = "users.db"

# Create users table if it doesn't exist
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")
conn.commit()
conn.close()

# --- Colors ---
BG_COLOR = '#1c1b2f'
BOX_COLOR = '#6a1b9a'
BTN_COLOR = '#f1e4ff'
BTN_TEXT_COLOR = '#3e0b5e'
ACCENT_COLOR = '#d500f9'
TEXT_COLOR = '#ffffff'
BORDER_COLOR = '#f500f5'

def login_page():
    def login():
        username = username_entry.get()
        password = password_entry.get()

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            messagebox.showinfo("Login Success", f"Welcome {username}!")
            root.destroy()
            subprocess.Popen(["python", "employee.py"])
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    def open_register():
        root.destroy()
        register_page()

    root = tk.Tk()
    root.title("StaffSphere - Login")
    root.geometry("900x700")
    root.configure(bg=BG_COLOR)

    tk.Label(root, text="Welcome to Staffsphere!", bg=BG_COLOR, fg=ACCENT_COLOR, font=("Segoe UI", 26, "bold")).pack(pady=(30,10))
    tk.Label(root, text="Login to continue", bg=BG_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 14)).pack(pady=(0,30))

    box_frame = tk.Frame(root, bg=BOX_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=3, width=450, height=400)
    box_frame.pack(padx=30, pady=10)
    box_frame.pack_propagate(False)

    tk.Label(box_frame, text="Username", bg=BOX_COLOR, fg=BTN_COLOR, font=("Segoe UI", 12, "bold")).pack(pady=(20,5))
    username_entry = tk.Entry(box_frame, width=28, font=("Segoe UI", 12))
    username_entry.pack(pady=5, ipady=4)

    tk.Label(box_frame, text="Password", bg=BOX_COLOR, fg=BTN_COLOR, font=("Segoe UI", 12, "bold")).pack(pady=(15,5))
    password_entry = tk.Entry(box_frame, width=28, show="*", font=("Segoe UI", 12))
    password_entry.pack(pady=5, ipady=4)

    tk.Button(box_frame, text="Login", width=22, bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Segoe UI", 12, "bold"), command=login).pack(pady=(20,8))
    tk.Button(box_frame, text="Register", width=22, bg=ACCENT_COLOR, fg='white', font=("Segoe UI", 12, "bold"), command=open_register).pack(pady=(0,20))

    root.mainloop()

def register_page():
    def register():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields!")
            return

        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Registration successful! Go to Login.")
            root.destroy()
            login_page()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")

    root = tk.Tk()
    root.title("Register - StaffSphere")
    root.geometry("400x500")
    root.configure(bg=BG_COLOR)

    tk.Label(root, text="Register", fg=ACCENT_COLOR, bg=BG_COLOR, font=("Segoe UI", 24, "bold")).pack(pady=(40, 10))
    tk.Label(root, text="Create your account", fg=TEXT_COLOR, bg=BG_COLOR, font=("Segoe UI", 12)).pack(pady=(0, 20))

    form = tk.Frame(root, bg=BOX_COLOR, padx=20, pady=20, bd=2, relief="ridge")
    form.pack()

    tk.Label(form, text="Username", fg=TEXT_COLOR, bg=BOX_COLOR, font=("Segoe UI", 11, "bold")).pack(pady=(5, 0))
    username_entry = tk.Entry(form, font=("Segoe UI", 11), width=25)
    username_entry.pack(pady=(0, 10))

    tk.Label(form, text="Password", fg=TEXT_COLOR, bg=BOX_COLOR, font=("Segoe UI", 11, "bold")).pack(pady=(5, 0))
    password_entry = tk.Entry(form, font=("Segoe UI", 11), show="*", width=25)
    password_entry.pack(pady=(0, 15))

    tk.Button(form, text="Register", bg=ACCENT_COLOR, fg="white", font=("Segoe UI", 12, "bold"), width=20, command=register).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    login_page()
