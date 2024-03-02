class BookExample:
    def __init__(self, seller_id=0, title="test_title", author="test_author", count_pages=1, year=2000):
        self.seller_id = seller_id
        self.title = title
        self.author = author
        self.count_pages = count_pages
        self.year = year

    def to_dict(self):
        return {
            "seller_id": self.seller_id,
            "title": self.title,
            "author": self.author,
            "count_pages": self.count_pages,
            "year": self.year,
        }

    def gen_new_book_data(self):
        return {
            "seller_id": self.seller_id,
            "title": self.title + "new",
            "author": self.author + "new",
            "count_pages": self.count_pages + 1,
            "year": self.year + 1,
        }
