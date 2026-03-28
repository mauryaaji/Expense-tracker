import tkinter as tk
from tkinter import messagebox
import json
import matplotlib.pyplot as plt

USER_FILE = "users.json"
FILE = "expenses.json"

# ---------- USER SYSTEM ----------
def load_users():
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def signup():
    u = user_entry.get()
    p = pass_entry.get()

    if not u or not p:
        messagebox.showwarning("Warning", "Fill all fields")
        return

    users = load_users()

    if u in users:
        messagebox.showerror("Error", "User exists")
    else:
        users[u] = p
        save_users(users)
        messagebox.showinfo("Success", "Account Created")

def login():
    u = user_entry.get()
    p = pass_entry.get()

    users = load_users()

    if u in users and users[u] == p:
        messagebox.showinfo("Success", "Login Successful")
        login_window.destroy()
        open_main_app()
    else:
        messagebox.showerror("Error", "Invalid Login")

# ---------- DATA ----------
def load_data():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

# ---------- CORE ----------
def add_expense():
    if not date_entry.get() or not category_entry.get() or not amount_entry.get():
        messagebox.showwarning("Warning", "All fields required!")
        return

    try:
        data = load_data()

        expense = {
            "date": date_entry.get(),
            "category": category_entry.get(),
            "description": desc_entry.get(),
            "amount": float(amount_entry.get())
        }

        data.append(expense)
        save_data(data)

        clear_inputs()
        show_expenses()
        update_total()

    except:
        messagebox.showerror("Error", "Invalid amount")

def show_expenses(filtered=None):
    data = filtered if filtered else load_data()
    listbox.delete(0, tk.END)

    for i, exp in enumerate(data, start=1):
        listbox.insert(tk.END, f"{i}. {exp['date']} | {exp['category']} | ₹{exp['amount']}")

def delete_expense():
    selected = listbox.curselection()
    if not selected:
        return

    if not messagebox.askyesno("Confirm", "Delete this expense?"):
        return

    data = load_data()
    data.pop(selected[0])
    save_data(data)

    show_expenses()
    update_total()

def update_total():
    total = sum(exp["amount"] for exp in load_data())
    total_label.config(text=f"Total: ₹{total}")

def search_expense():
    keyword = search_entry.get().lower()
    data = load_data()

    filtered = [
        exp for exp in data
        if keyword in exp["category"].lower() or keyword in exp["description"].lower()
    ]
    show_expenses(filtered)

def category_wise():
    result = {}
    for exp in load_data():
        result[exp["category"]] = result.get(exp["category"], 0) + exp["amount"]

    msg = "\n".join([f"{k}: ₹{v}" for k, v in result.items()])
    messagebox.showinfo("Category Wise", msg)

def clear_inputs():
    date_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    desc_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    suggestion_box.place_forget()

# ---------- CATEGORY AUTO ----------
def get_categories():
    default = ["Food", "Travel", "Shopping", "Bills"]
    saved = list(set(exp["category"] for exp in load_data()))
    return list(set(default + saved))

def suggest(event):
    text = category_entry.get().lower()
    suggestion_box.delete(0, tk.END)

    if text == "":
        suggestion_box.place_forget()
        return

    matches = [c for c in get_categories() if text in c.lower()]

    if matches:
        for m in matches:
            suggestion_box.insert(tk.END, m)
        suggestion_box.place(x=160, y=100)
    else:
        suggestion_box.place_forget()

def select_suggestion(event):
    if suggestion_box.curselection():
        val = suggestion_box.get(suggestion_box.curselection())
        category_entry.delete(0, tk.END)
        category_entry.insert(0, val)
        suggestion_box.place_forget()

# ---------- GRAPH ----------
def show_pie_chart():
    data = load_data()
    if not data:
        return

    cat = {}
    for e in data:
        cat[e["category"]] = cat.get(e["category"], 0) + e["amount"]

    plt.pie(cat.values(), labels=cat.keys(), autopct='%1.1f%%')
    plt.title("Expense Distribution")
    plt.show()

def show_bar_chart():
    data = load_data()
    if not data:
        return

    cat = {}
    for e in data:
        cat[e["category"]] = cat.get(e["category"], 0) + e["amount"]

    plt.bar(cat.keys(), cat.values())
    plt.title("Category Wise Expense")
    plt.show()

# ---------- MAIN APP ----------
def open_main_app():
    global date_entry, category_entry, desc_entry, amount_entry
    global listbox, total_label, search_entry, suggestion_box

    root = tk.Tk()
    root.title("💸 Expense Tracker PRO")
    root.geometry("450x650")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Label(frame, text="Date").grid(row=0, column=0)
    date_entry = tk.Entry(frame)
    date_entry.grid(row=0, column=1)

    tk.Label(frame, text="Category").grid(row=1, column=0)
    category_entry = tk.Entry(frame)
    category_entry.grid(row=1, column=1)

    suggestion_box = tk.Listbox(root, height=4)
    category_entry.bind("<KeyRelease>", suggest)
    suggestion_box.bind("<<ListboxSelect>>", select_suggestion)

    tk.Label(frame, text="Description").grid(row=2, column=0)
    desc_entry = tk.Entry(frame)
    desc_entry.grid(row=2, column=1)

    tk.Label(frame, text="Amount").grid(row=3, column=0)
    amount_entry = tk.Entry(frame)
    amount_entry.grid(row=3, column=1)

    tk.Button(frame, text="Add", command=add_expense).grid(row=4, column=0)
    tk.Button(frame, text="Clear", command=clear_inputs).grid(row=4, column=1)

    search_entry = tk.Entry(root)
    search_entry.pack()
    tk.Button(root, text="Search", command=search_expense).pack()

    listbox = tk.Listbox(root, width=50)
    listbox.pack()

    tk.Button(root, text="Delete", command=delete_expense).pack()
    tk.Button(root, text="Category Wise", command=category_wise).pack()
    tk.Button(root, text="Pie Chart", command=show_pie_chart).pack()
    tk.Button(root, text="Bar Chart", command=show_bar_chart).pack()

    total_label = tk.Label(root, text="Total: ₹0")
    total_label.pack()

    show_expenses()
    update_total()

    root.mainloop()

# ---------- LOGIN UI ----------
login_window = tk.Tk()
login_window.title("Login")

tk.Label(login_window, text="Username").pack()
user_entry = tk.Entry(login_window)
user_entry.pack()

tk.Label(login_window, text="Password").pack()
pass_entry = tk.Entry(login_window, show="*")
pass_entry.pack()

tk.Button(login_window, text="Login", command=login).pack()
tk.Button(login_window, text="Signup", command=signup).pack()

login_window.mainloop()