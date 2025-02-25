import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class Transaction:
    def __init__(self, amount: float, category: str, date: str, description: str, is_income: bool = False):
        self.amount = amount
        self.category = category
        self.date = datetime.strptime(date, '%Y-%m-%d')
        self.description = description
        self.is_income = is_income

class FinanceManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Manager")
        self.root.geometry("1000x700")
        
        self.data_file = "data/finance_data.json"
        self.transactions = []
        self.budgets = {}
        self.load_data()
        
        self.create_widgets()
        self.style_widgets()

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.transactions = [Transaction(**t) for t in data.get('transactions', [])]
                    self.budgets = data.get('budgets', {})
            else:
                self.save_data()  # Create file if it doesn't exist
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Data file corrupted. Starting fresh.")
            self.transactions = []
            self.budgets = {}
            self.save_data()

    def save_data(self):
        data = {
            'transactions': [{
                'amount': t.amount,
                'category': t.category,
                'date': t.date.strftime('%Y-%m-%d'),
                'description': t.description,
                'is_income': t.is_income
            } for t in self.transactions],
            'budgets': self.budgets
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)

    def style_widgets(self):
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("TLabel", padding=3)
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Transaction Tab
        self.transaction_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.transaction_frame, text="Transactions")
        self.create_transaction_tab()

        # Budget Tab
        self.budget_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.budget_frame, text="Budget")
        self.create_budget_tab()

        # Reports Tab
        self.reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="Reports")
        self.create_reports_tab()

    def create_transaction_tab(self):
        # Input Frame
        input_frame = ttk.LabelFrame(self.transaction_frame, text="Add Transaction", padding="10")
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(input_frame, text="Amount:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5)
        self.category_entry = ttk.Entry(input_frame)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Description:").grid(row=2, column=0, padx=5, pady=5)
        self.desc_entry = ttk.Entry(input_frame)
        self.desc_entry.grid(row=2, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Add Income", 
                  command=lambda: self.add_transaction(True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Add Expense", 
                  command=lambda: self.add_transaction(False)).pack(side=tk.LEFT, padx=5)

        # Transaction Viewer
        viewer_frame = ttk.LabelFrame(self.transaction_frame, text="Transaction History", padding="10")
        viewer_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(viewer_frame, columns=('Date', 'Type', 'Amount', 'Category', 'Description'),
                                show='headings', height=10)
        self.tree.heading('Date', text='Date')
        self.tree.heading('Type', text='Type')
        self.tree.heading('Amount', text='Amount')
        self.tree.heading('Category', text='Category')
        self.tree.heading('Description', text='Description')
        self.tree.column('Date', width=100)
        self.tree.column('Type', width=80)
        self.tree.column('Amount', width=100)
        self.tree.column('Category', width=120)
        self.tree.column('Description', width=200)
        self.tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(viewer_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.update_transaction_view()

    def create_budget_tab(self):
        budget_input = ttk.LabelFrame(self.budget_frame, text="Set Budget", padding="10")
        budget_input.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(budget_input, text="Category:").grid(row=0, column=0, padx=5, pady=5)
        self.budget_cat_entry = ttk.Entry(budget_input)
        self.budget_cat_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(budget_input, text="Budget Amount:").grid(row=1, column=0, padx=5, pady=5)
        self.budget_amount_entry = ttk.Entry(budget_input)
        self.budget_amount_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(budget_input, text="Set Budget", 
                  command=self.set_budget).grid(row=2, column=1, pady=10)

    def create_reports_tab(self):
        reports_frame = ttk.Frame(self.reports_frame, padding="10")
        reports_frame.pack(fill=tk.X)

        ttk.Button(reports_frame, text="Show Balance", 
                  command=self.show_balance).pack(side=tk.LEFT, padx=5)
        ttk.Button(reports_frame, text="Spending Pie Chart", 
                  command=self.show_spending_chart).pack(side=tk.LEFT, padx=5)
        ttk.Button(reports_frame, text="Budget Progress", 
                  command=self.show_budget_progress).pack(side=tk.LEFT, padx=5)

    def update_transaction_view(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in sorted(self.transactions, key=lambda x: x.date, reverse=True):
            self.tree.insert('', tk.END, values=(
                t.date.strftime('%Y-%m-%d'),
                'Income' if t.is_income else 'Expense',
                f"${t.amount:.2f}",
                t.category,
                t.description
            ))

    def add_transaction(self, is_income: bool):
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Amount must be positive")
            category = self.category_entry.get().strip()
            description = self.desc_entry.get().strip()
            
            if not category or not description:
                raise ValueError("All fields must be filled")
                
            transaction = Transaction(amount, category, datetime.now().strftime('%Y-%m-%d'), 
                                   description, is_income)
            self.transactions.append(transaction)
            self.save_data()
            self.update_transaction_view()
            
            self.amount_entry.delete(0, tk.END)
            self.category_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            messagebox.showinfo("Success", "Transaction added successfully!")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def set_budget(self):
        try:
            category = self.budget_cat_entry.get().strip()
            amount = float(self.budget_amount_entry.get())
            if amount <= 0:
                raise ValueError("Budget must be positive")
            if not category:
                raise ValueError("Category must be filled")
                
            self.budgets[category] = amount
            self.save_data()
            
            self.budget_cat_entry.delete(0, tk.END)
            self.budget_amount_entry.delete(0, tk.END)
            messagebox.showinfo("Success", "Budget set successfully!")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def get_balance(self) -> float:
        income = sum(t.amount for t in self.transactions if t.is_income)
        expenses = sum(t.amount for t in self.transactions if not t.is_income)
        return income - expenses

    def get_category_spending(self) -> dict:
        spending = {}
        for t in self.transactions:
            if not t.is_income:
                spending[t.category] = spending.get(t.category, 0) + t.amount
        return spending

    def show_balance(self):
        balance = self.get_balance()
        messagebox.showinfo("Balance", f"Current Balance: ${balance:.2f}")

    def show_spending_chart(self):
        spending = self.get_category_spending()
        if not spending:
            messagebox.showwarning("Warning", "No expenses to display")
            return

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(spending.values(), labels=spending.keys(), autopct='%1.1f%%', startangle=90)
        ax.set_title('Spending by Category')
        
        window = tk.Toplevel(self.root)
        window.title("Spending Distribution")
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_budget_progress(self):
        spending = self.get_category_spending()
        categories = list(set(spending.keys()) & set(self.budgets.keys()))
        if not categories:
            messagebox.showwarning("Warning", "No budget data to compare")
            return

        spent = [spending.get(cat, 0) for cat in categories]
        budgeted = [self.budgets[cat] for cat in categories]

        fig, ax = plt.subplots(figsize=(8, 6))
        x = range(len(categories))
        ax.bar(x, budgeted, width=0.4, label='Budget', alpha=0.7)
        ax.bar([i + 0.4 for i in x], spent, width=0.4, label='Spent', alpha=0.7)
        ax.set_xlabel('Categories')
        ax.set_ylabel('Amount')
        ax.set_title('Budget vs Actual Spending')
        ax.set_xticks([i + 0.2 for i in x])
        ax.set_xticklabels(categories, rotation=45)
        ax.legend()
        plt.tight_layout()

        window = tk.Toplevel(self.root)
        window.title("Budget Progress")
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def main():
    root = tk.Tk()
    app = FinanceManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()