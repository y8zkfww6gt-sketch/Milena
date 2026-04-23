import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Имя файла данных
DATA_FILE = "books.json"

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.books = []  # Список для хранения словарей книг

        # --- Фрейм ввода данных ---
        input_frame = ttk.LabelFrame(root, text="Добавить книгу", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Поля ввода (Пункт 1)
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w")
        self.entry_title = ttk.Entry(input_frame, width=30)
        self.entry_title.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Автор:").grid(row=1, column=0, sticky="w")
        self.entry_author = ttk.Entry(input_frame, width=30)
        self.entry_author.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Жанр:").grid(row=2, column=0, sticky="w")
        self.combo_genre = ttk.Combobox(input_frame, values=["Фантастика", "Детектив", "Роман", "Научная"], width=28)
        self.combo_genre.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Страниц:").grid(row=3, column=0, sticky="w")
        self.entry_pages = ttk.Entry(input_frame, width=30)
        self.entry_pages.grid(row=3, column=1, padx=5, pady=2)

        # Кнопка Добавить (Пункт 2)
        ttk.Button(input_frame, text="Добавить книгу", command=self.add_book).grid(row=4, column=0, columnspan=2, pady=10)

        # --- Таблица (Treeview) ---
        tree_frame = ttk.LabelFrame(root, text="Список книг", padding=10)
        tree_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        columns = ("title", "author", "genre", "pages")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Страниц")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # --- Фильтры и управление данными (Пункт 3 и 4) ---
        control_frame = ttk.Frame(root)
        control_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(control_frame, text="Фильтр по жанру:").pack(side="left", padx=5)
        self.filter_genre = ttk.Combobox(control_frame, values=["Все", "Фантастика", "Детектив", "Роман", "Научная"], state="readonly", width=15)
        self.filter_genre.set("Все")
        self.filter_genre.pack(side="left", padx=5)
        self.filter_genre.bind("<<ComboboxSelected>>", self.apply_filter)

        ttk.Label(control_frame, text="Мин. страниц:").pack(side="left", padx=(20,5))
        self.filter_pages = ttk.Entry(control_frame, width=8)
        self.filter_pages.insert(0, "0")
        self.filter_pages.pack(side="left", padx=5)
        ttk.Button(control_frame, text="Применить", command=self.apply_filter).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Сбросить", command=self.reset_filter).pack(side="left", padx=5)

        # Кнопки Сохранить / Загрузить
        ttk.Button(control_frame, text="Сохранить в JSON", command=self.save_data).pack(side="right", padx=5)
        ttk.Button(control_frame, text="Загрузить JSON", command=self.load_data).pack(side="right", padx=5)

        # При запуске пытаемся загрузить данные
        self.load_data()

    # Пункт 5: Проверка корректности ввода
    def add_book(self):
        title = self.entry_title.get().strip()
        author = self.entry_author.get().strip()
        genre = self.combo_genre.get().strip()
        pages_str = self.entry_pages.get().strip()

        if not title or not author or not genre or not pages_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
            return

        # Добавляем в список и таблицу
        book = {"title": title, "author": author, "genre": genre, "pages": pages}
        self.books.append(book)
        self.update_table(self.books)
        
        # Очистка полей
        self.entry_title.delete(0, tk.END)
        self.entry_author.delete(0, tk.END)
        self.combo_genre.set("")
        self.entry_pages.delete(0, tk.END)

    def update_table(self, data):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Заполнение
        for book in data:
            self.tree.insert("", tk.END, values=(book["title"], book["author"], book["genre"], book["pages"]))

    # Пункт 3: Фильтрация
    def apply_filter(self, event=None):
        genre_filter = self.filter_genre.get()
        pages_filter = self.filter_pages.get()

        try:
            min_pages = int(pages_filter) if pages_filter else 0
        except ValueError:
            min_pages = 0

        filtered_books = []
        for book in self.books:
            # Проверка жанра
            if genre_filter != "Все" and book["genre"] != genre_filter:
                continue
            # Проверка страниц
            if book["pages"] < min_pages:
                continue
            filtered_books.append(book)
        
        self.update_table(filtered_books)

    def reset_filter(self):
        self.filter_genre.set("Все")
        self.filter_pages.delete(0, tk.END)
        self.filter_pages.insert(0, "0")
        self.update_table(self.books)

    # Пункт 4: Работа с JSON
    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.books = json.load(f)
            self.update_table(self.books)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    app = BookTracker(root)
    root.mainloop()
