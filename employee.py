import sqlite3
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import font
import csv
from tkinter import filedialog ,messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter.ttk import Combobox

conn = sqlite3.connect("employee_management.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE employees ADD COLUMN performance_date TEXT")
    cursor.execute("ALTER TABLE employees ADD COLUMN performance_score REAL")
    cursor.execute("ALTER TABLE employees ADD COLUMN performance_comments TEXT")
except sqlite3.OperationalError:
    # Ignore error if columns already exist
    pass

conn.commit()
conn.close()

def configure_styles():
    style = ttk.Style()
    style.theme_use("clam")  # Use a nicer theme

    # Combobox (Dropdown) Style
    style.configure("TCombobox",
                    padding=5,
                    relief="flat",
                    foreground="#E1BEE7",
                    background="#E1BEE7",
                    fieldbackground="#f9f9f9",
                    bordercolor="#ccc")

    # Button Style
    style.configure("TButton",
                    padding=6,
                    relief="flat",
                    background="#4CAF50",  # Green
                    foreground="#fff",
                    borderwidth=0)

    style.map("TButton",
              background=[('active', '#45a049')],
              foreground=[('active', '#fff')])



# Color constants
class Colors:
    PRIMARY = '#2E0854'      # Vibrant Purple
    SECONDARY = '#FF6584'    # Pinkish Red (active state)
    SUCCESS = '#00C897'      # Teal Green
    WARNING = '#FFA41B'      # Vibrant Orange
    BACKGROUND = '#E1BEE7'     # Soft Light Grey
    TEXT = '#2C3E50'         # Dark Text
    WHITE = '#FFFFFF'

# Configure tkinter styles
def configure_styles():
    style = ttk.Style()
    style.theme_use('clam')  # For full customizability

    # Set window background color
    root.configure(bg=Colors.BACKGROUND)

    # Default font
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family="Segoe UI", size=11)

    # Treeview
    style.configure("Treeview",
                    background=Colors.WHITE,
                    foreground=Colors.TEXT,
                    rowheight=34,
                    fieldbackground=Colors.WHITE,
                    borderwidth=0)
    style.map("Treeview",
              background=[('selected', Colors.PRIMARY)],
              foreground=[('selected', 'white')])
    style.configure("Treeview.Heading",
                    background=Colors.PRIMARY,
                    foreground='white',
                    font=("Segoe UI", 11, "bold"),
                    relief='flat')

    # Buttons
    style.configure("TButton",
                    background=Colors.PRIMARY,
                    foreground='white',
                    font=("Segoe UI", 10, "bold"),
                    padding=8,
                    borderwidth=0)
    style.map("TButton",
              background=[('active', Colors.SECONDARY)],
              foreground=[('active', 'white')])

    # Combobox
    style.configure("TCombobox",
                    fieldbackground='white',
                    bordercolor=Colors.PRIMARY,
                    arrowsize=15,
                    relief="flat",
                    padding=4)
    style.map("TCombobox",
              fieldbackground=[('readonly', 'white')],
              background=[('readonly', 'white')])

    # Entry
    style.configure("TEntry",
                    padding=6,
                    relief="solid",
                    borderwidth=1,
                    bordercolor=Colors.PRIMARY)

    # LabelFrame Title
    style.configure("TLabelframe.Label",
                    font=("Segoe UI", 12, "bold"),
                    foreground=Colors.PRIMARY)
    style.configure("TLabelframe",
                    background=Colors.BACKGROUND,
                    borderwidth=2,
                    relief="groove")

    # Labels
    style.configure("TLabel",
                    background=Colors.BACKGROUND,
                    foreground=Colors.TEXT,
                    font=("Segoe UI", 10))

# Initialize database
def init_db():
    conn = sqlite3.connect("employee_management.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    salary REAL NOT NULL,
    joining_date TEXT,
    gender TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees (id)
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        review_date TEXT NOT NULL,
        score INTEGER NOT NULL,
        comments TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees (id)
    )""")
    conn.commit()
    conn.close()

def add_employee():
    name = name_entry.get()
    department = department_entry.get()
    salary = salary_entry.get()
    joining_date = joining_date_entry.get()
    gender = gender_entry.get()

    if not name or not department or not salary or not joining_date or not gender:
        messagebox.showerror("Error", "All fields are required!")
        return

    conn = sqlite3.connect("employee_management.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO employees (name, department, salary, joining_date, gender) VALUES (?, ?, ?, ?, ?)",
        (name, department, float(salary), joining_date, gender)
    )
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Employee added successfully!")

    # Clear form
    name_entry.delete(0, END)
    department_entry.delete(0, END)
    salary_entry.delete(0, END)
    joining_date_entry.delete(0, END)
    gender_entry.delete(0, END)

    load_employees()


def load_employees():
    for row in employee_tree.get_children():
        employee_tree.delete(row)

    conn = sqlite3.connect("employee_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, department, salary, joining_date, gender FROM employees")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        employee_tree.insert("", END, values=row)


def record_attendance():
    selected = employee_tree.focus()
    if not selected:
        messagebox.showerror("Error", "Select an employee to record attendance!")
        return

    employee_id = employee_tree.item(selected)["values"][0]
    status = status_combobox.get()
    date = date_entry.get()
    if not status or not date:
        messagebox.showerror("Error", "Date and Status are required!")
        return

    conn = sqlite3.connect("employee_management.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance (employee_id, date, status) VALUES (?, ?, ?)", (employee_id, date, status))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Attendance recorded successfully!", icon="info")
    status_combobox.set("")
    date_entry.delete(0, END)

def add_performance():
    selected = employee_tree.focus()
    if not selected:
        messagebox.showerror("Error", "Select an employee to add performance review!")
        return

    employee_id = employee_tree.item(selected)["values"][0]
    score = score_entry.get()
    comments = comments_entry.get()
    if not score:
        messagebox.showerror("Error", "Score is required!")
        return

    review_date = review_date_entry.get()
    conn = sqlite3.connect("employee_management.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO performance (employee_id, review_date, score, comments) VALUES (?, ?, ?, ?)",
                   (employee_id, review_date, int(score), comments))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Performance review added successfully!", icon="info")
    score_entry.delete(0, END)
    comments_entry.delete(0, END)
    review_date_entry.delete(0, END)
    
def delete_employee():
    selected = employee_tree.focus()
    if not selected:
        messagebox.showerror("Error", "Please select an employee to delete!")
        return

    employee_id = employee_tree.item(selected)["values"][0]
    
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this employee?")
    if confirm:
        conn = sqlite3.connect("employee_management.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        cursor.execute("DELETE FROM attendance WHERE employee_id = ?", (employee_id,))
        cursor.execute("DELETE FROM performance WHERE employee_id = ?", (employee_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Employee deleted successfully!")
        load_employees()

def delete_all_employees():
    confirm = messagebox.askyesno("Confirm Delete All", "Are you sure you want to delete ALL employees? This cannot be undone.")
    if confirm:
        conn = sqlite3.connect("employee_management.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees")
        cursor.execute("DELETE FROM attendance")
        cursor.execute("DELETE FROM performance")
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "All employee records have been deleted.")
        load_employees()

def on_tree_select(event):
    selected = employee_tree.focus()
    if selected:
        values = employee_tree.item(selected, 'values')
        name_entry.delete(0, END)
        name_entry.insert(0, values[1])
        department_entry.delete(0, END)
        department_entry.insert(0, values[2])
        salary_entry.delete(0, END)
        salary_entry.insert(0, values[3])

        # Debug:
        print(f"Selected: {selected}")
        print(f"Loaded Values -> Name: {values[1]}, Department: {values[2]}, Salary: {values[3]}")


def update_employee():
    selected = employee_tree.focus()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select an employee to update.")
        return

    name = name_entry.get().strip()
    department = department_entry.get().strip()
    salary = salary_entry.get().strip()

    print(f"Selected: {selected}")
    print(f"Name entry: '{name}' Department entry: '{department}' Salary entry: '{salary}'")

    if not name or not department or not salary:
        messagebox.showerror("Input Error", "All fields are required.")
        return

    # ✅ Update the data in the Treeview **BEFORE clearing fields**
    current_values = employee_tree.item(selected, 'values')
    employee_tree.item(selected, values=(current_values[0], name, department, salary))

    # ✅ THEN clear the entries AFTER updating
    name_entry.delete(0, END)
    department_entry.delete(0, END)
    salary_entry.delete(0, END)

    # ✅ Clear selection
    employee_tree.selection_remove(selected)

def clear_entries():
    name_entry.delete(0, END)
    department_entry.delete(0, END)
    salary_entry.delete(0, END)

def search_employee():
    search_term = search_var.get().strip()
    
    conn = sqlite3.connect("employee_management.db")
    cursor = conn.cursor()

    query = """
        SELECT * FROM employees
        WHERE name LIKE ? OR department LIKE ? OR CAST(salary AS TEXT) LIKE ?
    """
    like_term = f"%{search_term}%"
    cursor.execute(query, (like_term, like_term, like_term))

    rows = cursor.fetchall()
    conn.close()

    # Clear the Treeview before showing new search results
    for item in employee_tree.get_children():
        employee_tree.delete(item)

    for row in rows:
        employee_tree.insert('', END, values=row)

def display_all_employees():
    load_employees()



def open_analysis_window():
    analysis_win = Toplevel(root)
    analysis_win.title("Data Analysis")
    analysis_win.geometry("400x300")

    Label(analysis_win, text="Select Analysis", font=("Arial", 14)).pack(pady=10)

    ttk.Button(analysis_win, text="Department Distribution", command=show_department_distribution).pack(pady=5)
    ttk.Button(analysis_win, text="Salary Distribution", command=show_salary_distribution).pack(pady=5)
    ttk.Button(analysis_win, text="Avg salary per Distribution", command=show_avg_salary_per_department).pack(pady=5)
    ttk.Button(analysis_win, text="Joining date", command=show_new_joinees_over_time).pack(pady=5)
    ttk.Button(analysis_win, text="Gender statistics", command=show_gender_statistics).pack(pady=5)
    # similarly add other buttons for salary, avg salary, etc.


def show_department_distribution():
    conn = sqlite3.connect("employee_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT department, COUNT(*) FROM employees GROUP BY department")
    data = cursor.fetchall()
    conn.close()

    departments = [row[0] for row in data]
    counts = [row[1] for row in data]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(departments, counts, color="skyblue")
    ax.set_title("Employees per Department")
    ax.set_xlabel("Department")
    ax.set_ylabel("Number of Employees")


    # Embed matplotlib figure into Tkinter
    chart_window = Toplevel(root)
    chart_window.title("Department Distribution")
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

def show_salary_distribution():
    conn = sqlite3.connect("employee_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT salary FROM employees")
    salaries = [row[0] for row in cursor.fetchall()]
    conn.close()

    plt.figure(figsize=(8, 5))
    plt.hist(salaries, bins=10, color='skyblue', edgecolor='black')
    plt.title("Salary Distribution")
    plt.xlabel("Salary")
    plt.ylabel("Number of Employees")
    plt.show()

def show_avg_salary_per_department():
    conn = sqlite3.connect("employee_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT department, AVG(salary) FROM employees GROUP BY department")
    data = cursor.fetchall()
    conn.close()

    departments = [row[0] for row in data]
    avg_salaries = [row[1] for row in data]

    plt.figure(figsize=(8, 5))
    plt.bar(departments, avg_salaries, color='orange')
    plt.title("Average Salary per Department")
    plt.xlabel("Department")
    plt.ylabel("Average Salary")
    plt.show()

def show_new_joinees_over_time():
    conn = sqlite3.connect("employee_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT joining_date FROM employees")
    dates = [row[0] for row in cursor.fetchall()]
    conn.close()

    from collections import Counter
    from datetime import datetime

    formatted_dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in dates]
    count_by_date = Counter(formatted_dates)
    sorted_dates = sorted(count_by_date.keys())
    counts = [count_by_date[d] for d in sorted_dates]

    plt.figure(figsize=(8, 5))
    plt.plot(sorted_dates, counts, marker='o')
    plt.title("New Joinees Over Time")
    plt.xlabel("Date")
    plt.ylabel("Number of Joinees")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()



def show_gender_statistics():
    conn = sqlite3.connect("employee_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT gender, COUNT(*) FROM employees GROUP BY gender")
    data = cursor.fetchall()
    conn.close()

    labels = [row[0] for row in data]
    counts = [row[1] for row in data]

    plt.figure(figsize=(6, 6))
    plt.pie(counts, labels=labels, autopct="%1.1f%%", startangle=140)
    plt.title("Gender Distribution")
    plt.show()


def export_full_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="full_employee_report.csv",
                                             filetypes=[("CSV files", "*.csv")])
    if file_path:
        conn = sqlite3.connect("employee_management.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id, e.name, e.department, e.salary, e.joining_date, e.gender,
                   a.date as attendance_date, a.status as attendance_status,
                   p.review_date, p.score, p.comments
            FROM employees e
            LEFT JOIN attendance a ON e.id = a.employee_id
            LEFT JOIN performance p ON e.id = p.employee_id
        """)
        rows = cursor.fetchall()
        conn.close()
        
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Name", "Department", "Salary", "Joining Date", "Gender",
                             "Attendance Date", "Attendance Status",
                             "Review Date", "Score", "Comments"])
            writer.writerows(rows)
        
        messagebox.showinfo("Success", f"CSV saved:\n{file_path}")


def record_attendance():
    employee_name = attendance_name_entry.get()
    date = date_entry.get()
    status = status_combobox.get()

    # ⚠️ Debugging tip — Print to Terminal to see what's empty
    print(f"Employee: {employee_name}, Date: {date}, Status: {status}")

    if not employee_name or not date or not status:
        messagebox.showerror("Error", "Please fill all fields!")
        return

    employee_id = employee_name_map.get(employee_name)
    if not employee_id:
        messagebox.showerror("Error", "Employee not found in database!")
        return

    conn = sqlite3.connect("employee_management.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO attendance (employee_id, date, status)
        VALUES (?, ?, ?)
    """, (employee_id, date, status))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Attendance recorded for {employee_name} on {date}")





def add_performance():
    employee_name = performance_name_entry.get()
    review_date = review_date_entry.get()
    score = score_entry.get()
    comments = comments_entry.get()

    # Verify employee exists
    conn = sqlite3.connect("employee_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM employees WHERE name = ?", (employee_name,))
    employee = cursor.fetchone()

    if employee:
        employee_id = employee[0]
        cursor.execute("""
            UPDATE employees
            SET performance_date = ?, performance_score = ?, performance_comments = ?
            WHERE id = ?
        """, (review_date, score, comments, employee_name))
        conn.commit()
        messagebox.showinfo("Success", "Performance added successfully!")
    else:
        messagebox.showerror("Error", "Employee not found.")
    conn.close()

def load_employee_names():
    conn = sqlite3.connect("employee_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return employees  # List of (id, name)
def load_full_employee_data():
    conn = sqlite3.connect("employee_management.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT e.id, e.name, e.department, e.salary, e.joining_date, e.gender,
               a.date as attendance_date, a.status as attendance_status,
               p.review_date, p.score, p.comments
        FROM employees e
        LEFT JOIN attendance a ON e.id = a.employee_id
        LEFT JOIN performance p ON e.id = p.employee_id
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    # Clear current tree
    for item in employee_tree.get_children():
        employee_tree.delete(item)
    
    for row in rows:
        employee_tree.insert("", "end", values=row)




# Tkinter Window Setup
root = Tk()
root.title("Employee Management System")
root.geometry("950x700")

configure_styles()

# Frames
top_frame = Frame(root, bg=Colors.BACKGROUND, pady=10)
top_frame.pack()

employee_frame = ttk.LabelFrame(root, text="Employees", padding=10)
employee_frame.pack(fill="both", expand=True, padx=10, pady=10)


attendance_frame = ttk.LabelFrame(root, text="Attendance & Performance", padding=10)
attendance_frame.pack(fill="both", expand=True, padx=10, pady=10)


# Add Employee Section
Label(top_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
name_entry = ttk.Entry(top_frame)
name_entry.grid(row=0, column=1, padx=5, pady=5)

Label(top_frame, text="Department:").grid(row=0, column=2, padx=5, pady=5)
department_entry = ttk.Entry(top_frame)
department_entry.grid(row=0, column=3, padx=5, pady=5)

Label(top_frame, text="Salary:").grid(row=0, column=4, padx=5, pady=5)
salary_entry = ttk.Entry(top_frame)
salary_entry.grid(row=0, column=5, padx=5, pady=5)


# --- NEW: Joining Date ---
Label(top_frame, text="Joining Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
joining_date_entry = ttk.Entry(top_frame)
joining_date_entry.grid(row=1, column=1, padx=5, pady=5)

# --- ✅ NEW: Gender Dropdown ---
Label(top_frame, text="Gender:").grid(row=1, column=2, padx=5, pady=5)
gender_entry = Combobox(top_frame, values=["Male", "Female", "Other"], state="readonly")
gender_entry.grid(row=1, column=3, padx=5, pady=5)

ttk.Button(top_frame, text="Add Employee", command=add_employee).grid(row=1, column=6, padx=5, pady=5)


# ---- Search Section ----
search_frame = Frame(employee_frame, bg=Colors.BACKGROUND)
search_frame.pack(pady=8)

search_var = StringVar()

search_entry = Entry(search_frame, textvariable=search_var, width=30)
search_entry.grid(row=0, column=0, padx=5)

ttk.Button(search_frame, text="Search", command=lambda: search_employee()).grid(row=0, column=1, padx=5)
ttk.Button(search_frame, text="Clear Search", command=lambda: display_all_employees()).grid(row=0, column=2, padx=5)


# Employee Table
employee_tree = ttk.Treeview(employee_frame, columns=("ID", "Name", "Department", "Salary","joining_date", "gender"), show="headings")
employee_tree.heading("ID", text="ID")
employee_tree.heading("Name", text="Name")
employee_tree.heading("Department", text="Department")
employee_tree.heading("Salary", text="Salary")
employee_tree.heading("joining_date", text="Joining Date") 
employee_tree.heading("gender", text="Gender") 
employee_tree.bind("<<TreeviewSelect>>", on_tree_select)
employee_tree.pack(fill="both", expand=True)
employee_tree.pack(fill="both", expand=True)

button_frame = Frame(employee_frame, bg=Colors.BACKGROUND)
button_frame.pack(pady=8)

ttk.Button(button_frame, text="Delete Employee", command=delete_employee).grid(row=0, column=0, padx=5)
ttk.Button(button_frame, text="Delete All Employees", command=delete_all_employees).grid(row=0, column=1, padx=5)
        
ttk.Button(button_frame, text="Show Analysis", command=open_analysis_window).grid(row=0, column=5, padx=5)

ttk.Button(button_frame, text="Export Full CSV", command=export_full_csv).grid(row=0, column=4, padx=5)


conn = sqlite3.connect("employee_management.db")
cursor = conn.cursor()
cursor.execute("SELECT id, name FROM employees")
employee_list = cursor.fetchall()
conn.close()

employee_name_map = {name: emp_id for emp_id, name in employee_list}
employee_names = list(employee_name_map.keys())

# Attendance and Performance Section
Label(attendance_frame, text="Employee Name (Attendance):", bg="#e5c4f5").grid(row=0, column=0, padx=5, pady=5)
attendance_name_entry = ttk.Combobox(attendance_frame, values=employee_names, state="readonly")
attendance_name_entry.grid(row=0, column=1, padx=5, pady=5)

Label(attendance_frame, text="Date (YYYY-MM-DD):", bg="#e5c4f5").grid(row=0, column=2, padx=5, pady=5)
date_entry = ttk.Entry(attendance_frame)
date_entry.grid(row=0, column=3, padx=5, pady=5)

Label(attendance_frame, text="Status:", bg="#e5c4f5").grid(row=0, column=4, padx=5, pady=5)
status_combobox = ttk.Combobox(attendance_frame, values=["Present", "Absent", "Leave"], state="readonly")
status_combobox.grid(row=0, column=5, padx=5, pady=5)

ttk.Button(attendance_frame, text="Record Attendance", command=record_attendance).grid(row=0, column=6, padx=5, pady=5)

# ------------- Performance Section (Separate entries) ----------------
Label(attendance_frame, text="Employee Name (Performance):", bg="#e5c4f5").grid(row=1, column=0, padx=5, pady=5)
performance_name_entry = ttk.Combobox(attendance_frame, values=employee_names, state="readonly")
performance_name_entry.grid(row=1, column=1, padx=5, pady=5)

Label(attendance_frame, text="Review Date:", bg="#e5c4f5").grid(row=1, column=2, padx=5, pady=5)
review_date_entry = ttk.Entry(attendance_frame)
review_date_entry.grid(row=1, column=3, padx=5, pady=5)

Label(attendance_frame, text="Score:", bg="#e5c4f5").grid(row=1, column=4, padx=5, pady=5)
score_entry = ttk.Entry(attendance_frame)
score_entry.grid(row=1, column=5, padx=5, pady=5)

Label(attendance_frame, text="Comments:", bg="#e5c4f5").grid(row=1, column=6, padx=5, pady=5)
comments_entry = ttk.Entry(attendance_frame)
comments_entry.grid(row=1, column=7, padx=5, pady=5)

ttk.Button(attendance_frame, text="Add Performance", command=add_performance).grid(row=1, column=8, padx=5, pady=5)



# Initialize DB and Load Data
init_db()
load_employees()

root.mainloop()
