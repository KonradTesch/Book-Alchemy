from flask import Flask, render_template, request, redirect, url_for, flash
import os
from sqlalchemy import or_
from data_models import db, Author, Book
from datetime import datetime
from api_fetcher import get_book_cover

app = Flask(__name__)
app.secret_key = "supersecretkey"

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

db.init_app(app)

def setup_database():
    with app.app_context():
        db.create_all()

@app.route('/')
def home():
    sort_by = request.args.get('sort_by', 'title')
    search_query = request.args.get('search', '').strip()

    books_query = Book.query.join(Author)

    if search_query:
        books_query = books_query.filter(
            or_(
                Book.title.ilike(f"%{search_query}%"),
                Author.name.ilike(f"%{search_query}%")
            )
        )

    if sort_by == 'title':
        books_query = books_query.order_by(Book.title.asc()).all()
    elif sort_by == 'year':
        books_query = books_query.order_by(Book.publication_year.asc().nullslast()).all()
    elif sort_by == 'author':
        books_query = books_query.order_by(Author.name.asc()).all()


    return render_template('home.html', books=books_query, sort_by=sort_by, search_query=search_query)

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date = request.form.get('birthdate')
        date_of_death = request.form.get('date_of_death')

        birth_date_obj = None
        date_of_death_obj = None

        if birth_date:
            birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d').date()
        if date_of_death:
            date_of_death_obj = datetime.strptime(date_of_death, '%Y-%m-%d').date()

        new_author = Author(
            name=name,
            birth_date=birth_date_obj,
            date_of_death=date_of_death_obj
        )

        db.session.add(new_author)
        db.session.commit()

        return render_template('add_author.html', success=True)

    # GET request
    return render_template('add_author.html', success=False)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.all()

    if request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        if not title or not isbn or not author_id or not publication_year:
            return render_template('add_book.html', authors=authors, success=False)

        author = db.session.query(Author).filter_by(id=author_id).first()
        cover = get_book_cover(isbn, title, author.name)

        new_book = Book(
            title=title,
            isbn=isbn,
            publication_year=int(publication_year),
            author_id=int(author_id),
            cover_url=cover
        )

        db.session.add(new_book)
        db.session.commit()

        return render_template('add_book.html', authors=authors, success=True)

    # GET request
    return render_template('add_book.html', authors=authors, success=False)

@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    author = book.author

    db.session.delete(book)
    db.session.commit()

    remaining_books = Book.query.filter_by(author_id=author.id).count()
    if remaining_books == 0:
        db.session.delete(author)
        db.session.commit()
        flash(f"'{book.title}' wurde gelöscht und Autor '{author.name}' ebenfalls entfernt.", "success")
    else:
        flash(f"'{book.title}' wurde erfolgreich gelöscht.", "success")

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)