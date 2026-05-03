import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"
CATEGORIES = ["еда", "транспорт", "развлечения"]

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Express Tracker – Трекер расходов")
        self.root.geometry("800x550")

        # Данные
        self.expenses = self.load_data()

        # Переменные для ввода
        self.amount_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.date_var = tk.StringVar()

        # Переменные для фильтров
        self.filter_cat_var = tk.StringVar(value="Все")
        self.filter_start_var = tk.StringVar()
        self.filter_end_var = tk.StringVar()
        self.total_label_var = tk.StringVar(value="Сумма за период: 0.00")

        self.create_widgets()
        self.refresh_table()

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return []
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)

    def create_widgets(self):
        # Фрейм добавления
        add_frame = ttk.LabelFrame(self.root, text="Добавить расход", padding=10)
        add_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(add_frame, text="Сумма:").grid(row=0, column=0, sticky="w")
        ttk.Entry(add_frame, textvariable=self.amount_var, width=12).grid(row=0, column=1, padx=5)

        ttk.Label(add_frame, text="Категория:").grid(row=0, column=2, sticky="w")
        cat_combo = ttk.Combobox(add_frame, textvariable=self.category_var, values=CATEGORIES, state="readonly", width=15)
        cat_combo.grid(row=0, column=3, padx=5)
        cat_combo.current(0)

        ttk.Label(add_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, sticky="w")
        ttk.Entry(add_frame, textvariable=self.date_var, width=14).grid(row=0, column=5, padx=5)

        ttk.Button(add_frame, text="Добавить расход", command=self.add_expense).grid(row=0, column=6, padx=10)

        # Фрейм фильтров и итога
        filter_frame = ttk.LabelFrame(self.root, text="Фильтры и подсчёт суммы", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, sticky="w")
        filter_cat = ttk.Combobox(filter_frame, textvariable=self.filter_cat_var,
                                  values=["Все"] + CATEGORIES, state="readonly", width=15)
        filter_cat.grid(row=0, column=1, padx=5)
        filter_cat.current(0)

        ttk.Label(filter_frame, text="С даты:").grid(row=0, column=2, sticky="w")
        ttk.Entry(filter_frame, textvariable=self.filter_start_var, width=12).grid(row=0, column=3, padx=5)

        ttk.Label(filter_frame, text="По дату:").grid(row=0, column=4, sticky="w")
        ttk.Entry(filter_frame, textvariable=self.filter_end_var, width=12).grid(row=0, column=5, padx=5)

        ttk.Button(filter_frame, text="Применить", command=self.apply_filter).grid(row=0, column=6, padx=5)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filter).grid(row=0, column=7, padx=5)

        ttk.Label(filter_frame, textvariable=self.total_label_var, font=("Arial", 10, "bold")).grid(row=1, column=0, columnspan=8, pady=8)

        # Таблица
        table_frame = ttk.LabelFrame(self.root, text="История расходов", padding=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("amount", "category", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        self.tree.column("amount", width=100)
        self.tree.column("category", width=150)
        self.tree.column("date", width=150)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def validate_input(self, amount_str, date_str):
        # Проверка суммы
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом.")
                return None
        except ValueError:
            messagebox.showerror("Ошибка", "Сумма должна быть числом.")
            return None

        # Проверка даты
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД (например, 2026-05-03).")
            return None

        return amount

    def add_expense(self):
        amount_str = self.amount_var.get().strip()
        category = self.category_var.get().strip()
        date_str = self.date_var.get().strip()

        if not category:
            messagebox.showerror("Ошибка", "Выберите категорию.")
            return

        amount = self.validate_input(amount_str, date_str)
        if amount is None:
            return

        expense = {
            "amount": amount,
            "category": category,
            "date": date_str
        }
        self.expenses.append(expense)
        self.save_data()

        # Очистка полей
        self.amount_var.set("")
        self.date_var.set("")
        self.refresh_table()
        messagebox.showinfo("Успех", "Расход добавлен.")

    def apply_filter(self):
        cat_filter = self.filter_cat_var.get()
        start_date = self.filter_start_var.get().strip()
        end_date = self.filter_end_var.get().strip()

        # Валидация дат фильтра (нестрогая)
        if start_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Начальная дата фильтра должна быть в формате ГГГГ-ММ-ДД.")
                return
        if end_date:
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Конечная дата фильтра должна быть в формате ГГГГ-ММ-ДД.")
                return

        # Фильтрация
        filtered = self.expenses
        if cat_filter != "Все":
            filtered = [e for e in filtered if e["category"] == cat_filter]
        if start_date or end_date:
            if start_date and end_date:
                filtered = [e for e in filtered if start_date <= e["date"] <= end_date]
            elif start_date:
                filtered = [e for e in filtered if e["date"] >= start_date]
            elif end_date:
                filtered = [e for e in filtered if e["date"] <= end_date]

        # Подсчёт суммы
        total = sum(e["amount"] for e in filtered)
        self.total_label_var.set(f"Сумма за период: {total:.2f}")

        # Отображение
        self.tree.delete(*self.tree.get_children())
        for e in filtered:
            self.tree.insert("", "end", values=(e["amount"], e["category"], e["date"]))

    def reset_filter(self):
        self.filter_cat_var.set("Все")
        self.filter_start_var.set("")
        self.filter_end_var.set("")
        self.total_label_var.set("Сумма за период: 0.00")
        self.refresh_table()

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for e in self.expenses:
            self.tree.insert("", "end", values=(e["amount"], e["category"], e["date"]))
        self.total_label_var.set("Сумма за период: 0.00")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
