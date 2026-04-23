"""
Модуль управления данными трекера прочитанных книг.
Содержит класс BookTracker для работы с записями, JSON и валидацией.
"""

import json
import os
from typing import List, Dict, Tuple, Optional

DATA_FILE = "books.json"


class BookTracker:
    """Класс для управления списком прочитанных книг."""

    def __init__(self):
        self.books: List[Dict] = []
        self.load_books()

    def load_books(self) -> None:
        """Загружает книги из JSON-файла с проверкой структуры."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        # Валидация структуры каждой записи
                        valid_books = []
                        for book in data:
                            if self._is_valid_book_structure(book):
                                # Конвертация старых записей, если нужно
                                if 'pages' not in book and 'page_count' in book:
                                    book['pages'] = book['page_count']
                                valid_books.append(book)
                        self.books = valid_books
                    else:
                        self.books = []
            except (json.JSONDecodeError, IOError):
                self.books = []
        else:
            self.books = []

    def _is_valid_book_structure(self, book: Dict) -> bool:
        """Проверяет, что запись содержит все необходимые поля."""
        required_fields = ['title', 'author', 'genre', 'pages']
        return all(field in book for field in required_fields)

    def save_books(self) -> None:
        """Сохраняет все книги в JSON-файл с форматированием."""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.books, f, ensure_ascii=False, indent=4)

    def validate_book(self, title: str, author: str, 
                      genre: str, pages: str) -> Tuple[bool, str]:
        """
        Проверяет корректность введённых данных о книге.
        
        Args:
            title: Название книги
            author: Автор
            genre: Жанр
            pages: Количество страниц (строка для проверки)
        
        Returns:
            (bool, str): (Успех, Сообщение об ошибке или успехе)
        """
        # Проверка названия
        if not title or len(title.strip()) == 0:
            return False, "Название книги не может быть пустым"
        
        if len(title.strip()) > 200:
            return False, "Название книги слишком длинное (макс. 200 символов)"

        # Проверка автора
        if not author or len(author.strip()) == 0:
            return False, "Имя автора не может быть пустым"
        
        if len(author.strip()) > 100:
            return False, "Имя автора слишком длинное (макс. 100 символов)"

        # Проверка жанра
        if not genre or len(genre.strip()) == 0:
            return False, "Жанр не может быть пустым"

        # Проверка количества страниц
        if not pages:
            return False, "Количество страниц не может быть пустым"
        
        try:
            pages_int = int(pages)
            if pages_int <= 0:
                return False, "Количество страниц должно быть положительным числом"
            if pages_int > 10000:
                return False, "Количество страниц не может превышать 10000"
        except ValueError:
            return False, "Количество страниц должно быть целым числом"

        return True, "Данные корректны"

    def add_book(self, title: str, author: str, 
                 genre: str, pages: str) -> Tuple[bool, str]:
        """
        Добавляет новую книгу после валидации.
        
        Returns:
            (bool, str): (Успех, Сообщение)
        """
        # Валидация
        is_valid, message = self.validate_book(title, author, genre, pages)
        if not is_valid:
            return False, message

        # Проверка на дубликат
        title_lower = title.strip().lower()
        author_lower = author.strip().lower()
        for book in self.books:
            if (book['title'].lower() == title_lower and 
                book['author'].lower() == author_lower):
                return False, "Такая книга уже есть в списке"

        # Создание записи
        book = {
            'id': self._generate_id(),
            'title': title.strip(),
            'author': author.strip(),
            'genre': genre.strip(),
            'pages': int(pages),
            'date_added': self._get_current_date()
        }

        self.books.append(book)
        self.save_books()
        return True, f"Книга «{title.strip()}» успешно добавлена"

    def _generate_id(self) -> int:
        """Генерирует уникальный ID для новой книги."""
        if not self.books:
            return 1
        return max(book.get('id', 0) for book in self.books) + 1

    def _get_current_date(self) -> str:
        """Возвращает текущую дату в формате ГГГГ-ММ-ДД."""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d')

    def get_all_books(self) -> List[Dict]:
        """Возвращает все книги."""
        return self.books

    def get_unique_genres(self) -> List[str]:
        """Возвращает список уникальных жанров для выпадающего списка."""
        genres = set()
        for book in self.books:
            genres.add(book['genre'])
        return sorted(list(genres))

    def filter_books(self, genre: str = "", min_pages: Optional[int] = None) -> List[Dict]:
        """
        Фильтрует книги по жанру и минимальному количеству страниц.
        
        Args:
            genre: Жанр для фильтрации (пустая строка = все жанры)
            min_pages: Минимальное количество страниц
        
        Returns:
            Отфильтрованный список книг
        """
        result = self.books.copy()
        
        if genre:
            result = [b for b in result if b['genre'].lower() == genre.lower()]
        
        if min_pages is not None:
            result = [b for b in result if b['pages'] >= min_pages]
        
        return result

    def get_statistics(self) -> Dict:
        """Возвращает статистику по прочитанным книгам."""
        if not self.books:
            return {
                'total_books': 0,
                'total_pages': 0,
                'avg_pages': 0,
                'unique_genres': 0,
                'most_productive_author': None
            }
        
        total_pages = sum(b['pages'] for b in self.books)
        avg_pages = total_pages / len(self.books)
        unique_genres = len(set(b['genre'] for b in self.books))
        
        # Поиск самого читаемого автора
        author_counts = {}
        for book in self.books:
            author = book['author']
            author_counts[author] = author_counts.get(author, 0) + 1
        
        most_productive_author = max(author_counts.items(), key=lambda x: x[1])[0]
        
        return {
            'total_books': len(self.books),
            'total_pages': total_pages,
            'avg_pages': round(avg_pages, 1),
            'unique_genres': unique_genres,
            'most_productive_author': most_productive_author
        }

    def delete_book(self, book_id: int) -> Tuple[bool, str]:
        """Удаляет книгу по ID."""
        for i, book in enumerate(self.books):
            if book.get('id') == book_id:
                deleted_title = book['title']
                del self.books[i]
                self.save_books()
                return True, f"Книга «{deleted_title}» удалена"
        return False, "Книга не найдена"
