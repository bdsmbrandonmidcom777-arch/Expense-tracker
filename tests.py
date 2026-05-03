import tkinter as tk
import os
import json
from datetime import datetime

# Импортируем основной класс приложения
from main import ExpenseTracker

class TestExpenseTracker(ExpenseTracker):
    """Переопределяем путь к файлу данных для тестов."""
    DATA_FILE = "test_expenses.json"

def run_tests():
    print("=== ТЕСТИРОВАНИЕ EXPRESS TRACKER ===")

    # Удаляем остатки тестового файла перед запуском
    if os.path.exists(TestExpenseTracker.DATA_FILE):
        os.remove(TestExpenseTracker.DATA_FILE)

    # Создаём скрытое окно Tkinter для экземпляра трекера
    root = tk.Tk()
    root.withdraw()  # окно не показывается

    tracker = TestExpenseTracker(root)

    # ---------- Позитивный тест: добавление корректного расхода ----------
    tracker.amount_var.set("350.50")
    tracker.category_var.set("еда")
    tracker.date_var.set("2026-05-03")
    prev_count = len(tracker.expenses)
    tracker.add_expense()
    assert len(tracker.expenses) == prev_count + 1, "Ошибка: расход не добавился"
    last = tracker.expenses[-1]
    assert last["amount"] == 350.50, "Ошибка: сумма не совпадает"
    assert last["category"] == "еда", "Ошибка: категория не совпадает"
    assert last["date"] == "2026-05-03", "Ошибка: дата не совпадает"
    print("✅ Позитивный тест пройден")

    # ---------- Негативные тесты: валидация ввода ----------
    # Неверная сумма (не число)
    tracker.amount_var.set("abc")
    tracker.category_var.set("транспорт")
    tracker.date_var.set("2026-05-03")
    prev_count = len(tracker.expenses)
    tracker.add_expense()  # должно появиться сообщение об ошибке и запись не добавится
    assert len(tracker.expenses) == prev_count, "Ошибка: расход с неверной суммой не должен был добавиться"

    # Отрицательная сумма
    tracker.amount_var.set("-100")
    tracker.add_expense()
    assert len(tracker.expenses) == prev_count, "Ошибка: отрицательная сумма недопустима"

    # Сумма ноль
    tracker.amount_var.set("0")
    tracker.add_expense()
    assert len(tracker.expenses) == prev_count, "Ошибка: нулевая сумма недопустима"

    # Неверный формат даты
    tracker.amount_var.set("100")
    tracker.date_var.set("03-05-2026")
    tracker.add_expense()
    assert len(tracker.expenses) == prev_count, "Ошибка: неверный формат даты не распознан"

    # Пустая дата
    tracker.date_var.set("")
    tracker.add_expense()
    assert len(tracker.expenses) == prev_count, "Ошибка: пустая дата не распознана"

    # Пустая категория (хотя по умолчанию она выбрана, но проверим сброс)
    # tracker.category_var.set("")  # не даст ошибку, потому что combobox read-only, но проверим на прямую вызов validate_input
    # Проверка validate_input напрямую
    assert tracker.validate_input("abc", "2026-05-03") is None, "Ошибка: validate_input не вернул None для нечисла"
    assert tracker.validate_input("100", "abc") is None, "Ошибка: validate_input не вернул None для плохой даты"
    print("✅ Негативные тесты пройдены")

    # ---------- Граничные тесты ----------
    # Минимально допустимая сумма (0.01)
    tracker.amount_var.set("0.01")
    tracker.category_var.set("развлечения")
    tracker.date_var.set("2024-02-29")  # високосный год
    prev_count = len(tracker.expenses)
    tracker.add_expense()
    assert len(tracker.expenses) == prev_count + 1, "Ошибка: граничная сумма 0.01 не принята"
    assert tracker.expenses[-1]["date"] == "2024-02-29", "Ошибка: дата 29 февраля не прошла"

    # Очень длинная сумма (много цифр)
    tracker.amount_var.set("999999999.99")
    tracker.date_var.set("2026-12-31")
    prev_count = len(tracker.expenses)
    tracker.add_expense()
    assert len(tracker.expenses) == prev_count + 1, "Ошибка: большая сумма не принята"

    # Фильтрация по дате (границы периода)
    # Добавим запись на 2026-01-01
    tracker.amount_var.set("500")
    tracker.date_var.set("2026-01-01")
    tracker.add_expense()
    # Применим фильтр с началом 2026-01-01 и концом 2026-01-01
    tracker.filter_start_var.set("2026-01-01")
    tracker.filter_end_var.set("2026-01-01")
    tracker.filter_cat_var.set("Все")
    tracker.apply_filter()
    # Проверим, что в таблице только одна запись (2026-01-01)
    children = tracker.tree.get_children()
    assert len(children) == 1, f"Ошибка: найдено {len(children)} записей, ожидалась 1"
    # Сумма
    total_text = tracker.total_label_var.get()
    assert "500.00" in total_text, "Ошибка: сумма за период не равна 500.00"

    # Сбросим фильтр
    tracker.reset_filter()
    print("✅ Граничные тесты пройдены")

    # Удаляем тестовый файл
    if os.path.exists(TestExpenseTracker.DATA_FILE):
        os.remove(TestExpenseTracker.DATA_FILE)

    root.destroy()
    print("Все тесты пройдены успешно!")

if __name__ == "__main__":
    run_tests()