from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Date, ForeignKey
from datetime import date
from typing import Optional

# Create database instance
db = SQLAlchemy()


class Author(db.Model):
    """
    Database model for authors in the Library App.

    Represents an author with personal information including birth and death dates.
    """
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    date_of_death: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    def __repr__(self):
        """
        Returns the string representation for debugging purposes.
        :return: Debug string with author ID and name
        """
        return f"<Author(id={self.id}, name='{self.name}')>"

    def __str__(self):
        """
        Returns the human-readable string representation of the author.
        :return: Formatted string with author name and life dates
        """
        birth_str = f" (born {self.birth_date})" if self.birth_date else ""
        death_str = f" (died {self.date_of_death})" if self.date_of_death else ""
        return f"{self.name}{birth_str}{death_str}"


class Book(db.Model):
    """
    Database model for books in the Library App.
    Represents a book with metadata including title, ISBN, publication year,
    and relationship to an author.
    """
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    isbn: Mapped[str] = mapped_column(String(17), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    publication_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('authors.id'), nullable=False)
    cover_url: Mapped[str] = mapped_column(String(200), nullable=True)

    author = db.relationship('Author', backref='books')

    def __repr__(self):
        """
        Returns the string representation for debugging purposes.
        :return: Debug string with book ID, title, and ISBN
        """
        return f"<Book(id={self.id}, title='{self.title}', isbn='{self.isbn}')>"

    def __str__(self):
        """
        Returns the human-readable string representation of the book.
        :return: Formatted string with book title, year, and ISBN
        """
        year_str = f" ({self.publication_year})" if self.publication_year else ""
        return f"{self.title}{year_str} [ISBN: {self.isbn}]"