import tkinter as tk
from tkinter import ttk

def populate_treeview():
    # Insert data into the Treeview widget
    for i in range(1, 101):
        treeview.insert("", "end", values=(f"Item {i}", f"Category {i % 5}"))

# Create the main window
root = tk.Tk()
root.title("Scrollable List with Categories")

# Create a frame for the table categories
category_frame = ttk.LabelFrame(root, text="Categories")
category_frame.pack(padx=10, pady=10, fill="x")

# Create labels for the table categories
categories = ["Item Name", "Category"]
for col, category in enumerate(categories):
    label = ttk.Label(category_frame, text=category)
    label.grid(row=0, column=col, padx=5)

# Create a Treeview widget for the scrollable list
treeview = ttk.Treeview(root, columns=categories, show="headings")
treeview.pack(padx=10, pady=10, fill="both", expand=True)

# Set column headings for the Treeview
for col, category in enumerate(categories):
    treeview.heading(category, text=category)
    treeview.column(category, width=100)

# Create a scrollable scrollbar for the Treeview
scrollbar = ttk.Scrollbar(treeview, orient="vertical", command=treeview.yview)
treeview.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Populate the Treeview with sample data
populate_treeview()

# Create a frame for numbered index buttons
index_frame = ttk.Frame(root)
index_frame.pack(padx=10, pady=10, fill="x")

# Create numbered index buttons
for i in range(1, 11):
    button = ttk.Button(index_frame, text=str(i))
    button.grid(row=0, column=i - 1, padx=5)

# Start the Tkinter main loop
root.mainloop()
