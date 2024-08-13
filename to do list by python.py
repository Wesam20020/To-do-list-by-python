import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import threading
import time

class Task:
    def __init__(self, description, priority, category, reminder, completed=False):
        self.description = description
        self.priority = priority
        self.category = category
        self.reminder = reminder
        self.completed = completed

    def __str__(self):
        status = "✔️" if self.completed else "❌"
        return f"{status} [{self.priority}] {self.description} ({self.category}) - Reminder: {self.reminder.strftime('%d-%m-%Y %H:%M')}"

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Application")

        self.tasks = []

        # Create a frame for task input
        self.task_frame = ttk.LabelFrame(root, text="Add Task")
        self.task_frame.pack(padx=10, pady=5, fill="x")

        # Task description entry
        self.task_label = ttk.Label(self.task_frame, text="Task:")
        self.task_label.grid(row=0, column=0, padx=5, pady=5)
        self.task_entry = ttk.Entry(self.task_frame, width=40)
        self.task_entry.grid(row=0, column=1, padx=5, pady=5)

        # Priority dropdown
        self.priority_label = ttk.Label(self.task_frame, text="Priority:")
        self.priority_label.grid(row=0, column=2, padx=5, pady=5)
        self.priority_var = tk.StringVar(value="Medium")
        self.priority_menu = ttk.Combobox(self.task_frame, textvariable=self.priority_var, values=["Low", "Medium", "High"])
        self.priority_menu.grid(row=0, column=3, padx=5, pady=5)

        # Category dropdown
        self.category_label = ttk.Label(self.task_frame, text="Category:")
        self.category_label.grid(row=0, column=4, padx=5, pady=5)
        self.category_var = tk.StringVar(value="General")
        self.category_menu = ttk.Combobox(self.task_frame, textvariable=self.category_var, values=["General", "Work", "Personal", "Urgent"])
        self.category_menu.grid(row=0, column=5, padx=5, pady=5)

        # Reminder date and time
        self.reminder_label = ttk.Label(self.task_frame, text="Reminder Date:")
        self.reminder_label.grid(row=1, column=0, padx=5, pady=5)
        self.date_entry = DateEntry(self.task_frame, width=12, date_pattern='dd-mm-yyyy')
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)

        self.time_label = ttk.Label(self.task_frame, text="Reminder Time (HH:MM):")
        self.time_label.grid(row=1, column=2, padx=5, pady=5)
        self.time_entry = ttk.Entry(self.task_frame, width=10)
        self.time_entry.grid(row=1, column=3, padx=5, pady=5)
        self.time_entry.insert(0, "HH:MM")

        # Add Task button
        self.add_task_button = ttk.Button(self.task_frame, text="Add Task", command=self.add_task)
        self.add_task_button.grid(row=1, column=4, padx=5, pady=5)

        # Create a frame for task display and controls
        self.display_frame = ttk.LabelFrame(root, text="Tasks")
        self.display_frame.pack(padx=10, pady=5, fill="both", expand=True)

        # Tasks treeview
        self.tasks_tree = ttk.Treeview(self.display_frame, columns=("Description", "Priority", "Category", "Reminder"), show='headings')
        self.tasks_tree.pack(padx=10, pady=5, fill="both", expand=True)

        self.tasks_tree.heading("Description", text="Description")
        self.tasks_tree.heading("Priority", text="Priority")
        self.tasks_tree.heading("Category", text="Category")
        self.tasks_tree.heading("Reminder", text="Reminder")

        # Configure tags for priority colors
        self.tasks_tree.tag_configure('Low', background='lightgreen')
        self.tasks_tree.tag_configure('Medium', background='lightyellow')
        self.tasks_tree.tag_configure('High', background='lightcoral')

        # Control buttons
        self.mark_completed_button = ttk.Button(self.display_frame, text="Mark Completed", command=self.mark_task_completed)
        self.mark_completed_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.edit_task_button = ttk.Button(self.display_frame, text="Edit Task", command=self.edit_task)
        self.edit_task_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_task_button = ttk.Button(self.display_frame, text="Delete Task", command=self.delete_task)
        self.delete_task_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Bind the Delete key to the delete_task function
        self.root.bind('<Delete>', self.delete_task_event)

    def add_task(self):
        description = self.task_entry.get()
        priority = self.priority_var.get()
        category = self.category_var.get()
        date_str = self.date_entry.get()
        time_str = self.time_entry.get()
        
        try:
            reminder = datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M")
            if description:
                task = Task(description, priority, category, reminder)
                self.tasks.append(task)
                self.update_tasks_tree()
                self.task_entry.delete(0, tk.END)
                threading.Thread(target=self.set_reminder, args=(task,)).start()
            else:
                messagebox.showwarning("Warning", "Task description cannot be empty.")
        except ValueError:
            messagebox.showwarning("Warning", "You must enter a valid reminder time in HH:MM format.")

    def update_tasks_tree(self):
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)
        for task in self.tasks:
            tag = task.priority
            self.tasks_tree.insert("", tk.END, values=(task.description, task.priority, task.category, task.reminder.strftime('%d-%m-%Y %H:%M')), tags=(tag,))

    def mark_task_completed(self):
        try:
            selected_item = self.tasks_tree.selection()[0]
            selected_task_index = self.tasks_tree.index(selected_item)
            self.tasks[selected_task_index].completed = True
            self.update_tasks_tree()
        except IndexError:
            messagebox.showwarning("Warning", "You must select a task.")

    def edit_task(self):
        try:
            selected_item = self.tasks_tree.selection()[0]
            selected_task_index = self.tasks_tree.index(selected_item)
            task = self.tasks[selected_task_index]
            
            new_description = simpledialog.askstring("Edit Task", "Task description:", initialvalue=task.description)
            if new_description:
                task.description = new_description

            new_priority = simpledialog.askstring("Edit Task", "Task priority (Low, Medium, High):", initialvalue=task.priority)
            if new_priority:
                task.priority = new_priority

            new_category = simpledialog.askstring("Edit Task", "Task category (General, Work, Personal, Urgent):", initialvalue=task.category)
            if new_category:
                task.category = new_category

            new_reminder = simpledialog.askstring("Edit Task", "Reminder time (dd-mm-yyyy HH:MM):", initialvalue=task.reminder.strftime('%d-%m-%Y %H:%M'))
            if new_reminder:
                task.reminder = datetime.strptime(new_reminder, "%d-%m-%Y %H:%M")

            self.update_tasks_tree()
        except IndexError:
            messagebox.showwarning("Warning", "You must select a task.")

    def delete_task(self):
        try:
            selected_item = self.tasks_tree.selection()[0]
            selected_task_index = self.tasks_tree.index(selected_item)
            self.tasks.pop(selected_task_index)
            self.update_tasks_tree()
        except IndexError:
            messagebox.showwarning("Warning", "You must select a task.")

    def delete_task_event(self, event):
        self.delete_task()

    def set_reminder(self, task):
        time_to_wait = (task.reminder - datetime.now()).total_seconds()
        if time_to_wait > 0:
            time.sleep(time_to_wait)
        messagebox.showinfo("Reminder", f"Reminder: {task.description}")

# Run the application
root = tk.Tk()
app = TodoApp(root)
root.mainloop()
