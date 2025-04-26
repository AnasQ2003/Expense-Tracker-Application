import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from collections import defaultdict

FILE_NAME = "expenses.csv"


def initialize_file():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Category", "Amount", "Description"])


def add_expense():
    date = date_var.get()
    category = category_var.get()
    amount = amount_var.get()
    description = description_var.get()

    if not category or not amount or not description:
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Amount must be a positive number!")
        return

    with open(FILE_NAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, category, amount, description])

    messagebox.showinfo("Success", "Expense added successfully!")
    category_var.set("")
    amount_var.set("")
    description_var.set("")
    view_expenses()


def delete_expense():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select an expense to delete!")
        return

    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?")
    if not confirm:
        return

    values = tree.item(selected_item, 'values')
    expenses = []

    with open(FILE_NAME, mode='r') as file:
        reader = csv.reader(file)
        expenses = [row for row in reader]

    with open(FILE_NAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Category", "Amount", "Description"])
        for row in expenses:
            if row != list(values):
                writer.writerow(row)

    messagebox.showinfo("Success", "Expense deleted successfully!")
    view_expenses()


def view_expenses():
    for row in tree.get_children():
        tree.delete(row)

    if not os.path.exists(FILE_NAME):
        return

    with open(FILE_NAME, mode='r') as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            tree.insert("", "end", values=row)


def generate_report():
    if not os.path.exists(FILE_NAME):
        messagebox.showerror("Error", "No expenses recorded yet!")
        return

    category_totals = defaultdict(float)
    monthly_totals = defaultdict(float)
    month_labels = []

    with open(FILE_NAME, mode='r') as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            if len(row) < 3:
                continue
            try:
                date = datetime.strptime(row[0], "%Y-%m-%d")
                category = row[1]
                amount = float(row[2])

                category_totals[category] += amount
                month_key = date.strftime("%b %Y")
                monthly_totals[month_key] += amount

                if month_key not in month_labels:
                    month_labels.append(month_key)
            except ValueError:
                continue

    if not category_totals:
        messagebox.showinfo("Report", "No expenses to report!")
        return

    categories = list(category_totals.keys())
    category_values = list(category_totals.values())
    months = sorted(month_labels, key=lambda x: datetime.strptime(x, "%b %Y"))
    month_values = [monthly_totals[m] for m in months]

    fig, axs = plt.subplots(1, 2, figsize=(14, 6))

    # Pie Chart
    colors_pie = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff6666', '#c2c2f0']
    axs[0].pie(category_values, labels=categories, autopct='%1.1f%%', colors=colors_pie)
    axs[0].set_title("Expense Distribution by Category")

    # Bar Chart
    colors_bar = ['#4CAF50', '#008CBA', '#FF5733', '#FFC300', '#9C27B0', '#E91E63']
    axs[1].bar(months, month_values, color=colors_bar[:len(months)], alpha=0.7, edgecolor='black')
    axs[1].set_xlabel("Month")
    axs[1].set_ylabel("Total Amount Spent")
    axs[1].set_title("Monthly Expense Trend")
    axs[1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.show()

root = tk.Tk()
root.title("Expense Tracker")
root.geometry("800x600")
root.configure(bg="#f0f8ff")
initialize_file()

frame = tk.Frame(root, bg="#f0f8ff")
frame.pack(pady=10)

tk.Label(frame, text="Date", bg="#f0f8ff").grid(row=0, column=0)
date_var = tk.StringVar()
date_entry = DateEntry(frame, textvariable=date_var, date_pattern='yyyy-MM-dd')
date_entry.grid(row=0, column=1)

fields = ["Category", "Amount", "Description"]
variables = [tk.StringVar(), tk.StringVar(), tk.StringVar()]
category_var, amount_var, description_var = variables

for i, (label, var) in enumerate(zip(fields, variables)):
    tk.Label(frame, text=label, bg="#f0f8ff").grid(row=i + 1, column=0)
    tk.Entry(frame, textvariable=var).grid(row=i + 1, column=1)

button_frame = tk.Frame(root, bg="#f0f8ff")
button_frame.pack()

tk.Button(button_frame, text="Add Expense", command=add_expense, bg="#4CAF50", fg="white", width=15).pack(pady=5)
tk.Button(button_frame, text="Delete Expense", command=delete_expense, bg="#f44336", fg="white", width=15).pack(pady=5)
tk.Button(button_frame, text="View Report", command=generate_report, bg="#008CBA", fg="white", width=15).pack(pady=5)

columns = ("Date", "Category", "Amount", "Description")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=160, anchor="center")
tree.pack(fill="both", expand=True, pady=10)

view_expenses()
root.mainloop()
