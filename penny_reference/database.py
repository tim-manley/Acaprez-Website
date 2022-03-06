#!/usr/bin/env python

#-----------------------------------------------------------------------
# database.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

from sqlite3 import connect
from contextlib import closing
from book import Book

#-----------------------------------------------------------------------

_DATABASE_URL = 'file:penny.sqlite?mode=ro'

def search(author):

    books = []

    with connect(_DATABASE_URL, uri=True) as connection:

        with closing(connection.cursor()) as cursor:

            query_str = "SELECT author, title, price FROM books "
            query_str += "WHERE author LIKE ?"
            cursor.execute(query_str, [author+'%'])

            row = cursor.fetchone()
            while row is not None:
                book = Book(str(row[0]), str(row[1]), float(row[2]))
                books.append(book)
                row = cursor.fetchone()

    return books

#-----------------------------------------------------------------------

# For testing:

def _test():
    books = search('Kernighan')
    for book in books:
        print(book.get_author())
        print(book.get_title())
        print(book.get_price())
        print()

if __name__ == '__main__':
    _test()
