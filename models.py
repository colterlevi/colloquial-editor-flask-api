from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy() # create an instance of a database connection
migrate = Migrate(db) # associate migration functions to it

# This ORM has the migration and the model together
class Author(db.Model):
    # This is the migration part
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    admin = db.Column(db.Boolean, server_default='f', nullable=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    articles = db.relationship('Article', backref='author', lazy=True)
    edits = db.relationship('Edit', backref='author', lazy=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    # This is regular old Python classes
    # Right here is where we "whitelist" what can be set when creating a user
    # any column omitted cannot be set by the user/app manually
    def __init__(self, first_name, last_name, username, email, password, admin):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password = password
        self.admin = admin

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'bio': self.bio,
            'username': self.username,
            'email': self.email,
            'admin': self.admin,
            'articles': [article.to_dict() for article in Article.query.filter_by(author_id=self.id)]
        }

    def __repr__(self):
        return '<User %r>' % self.username


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    excerpt = db.Column(db.String(120))
    slug = db.Column(db.String(80))
    content = db.Column(db.Text)
    status = db.Column(db.String, nullable=True, server_default='draft')
    tags = db.Column(db.String, nullable=True, server_default='draft')
    category = db.Column(db.String, nullable=True, server_default='draft')
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=True)
    edits = db.relationship('Edit', backref='article', cascade='all, delete-orphan', lazy=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, content, title, author_id):
        self.content = content
        self.title = title
        self.author_id = author_id

    def to_dict(self):
        # author = Author.query.filter_by(id=self.author_id)
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'status': self.status,
            'content': self.content,
            'excerpt': self.excerpt,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'author_id': self.author_id,
            'author': self.author.username,
            'edits': [edit.to_dict() for edit in Edit.query.filter_by(article_id=self.id)]
        }

    def __repr__(self):
        return f'<Article {self.id}>'

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True)
    count = db.Column(db.Integer, default=0)


    def __init__(self, name):
            self.name = name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'count': self.count,
        }

    def __repr__(self):
        return f'<Category {self.id}>'

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True)
    count = db.Column(db.Integer, default=0)


    def __init__(self, name):
            self.name = name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'count': self.count,
        }

    def __repr__(self):
        return f'<Tag {self.id}>'

class Edit(db.Model):
    __tablename__ = 'edits'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())


    def __init__(self, article_id, author_id):
            self.article_id = article_id
            self.author_id = author_id

    def to_dict(self):
        return {
            'id': self.id,
            'article': self.article.title,
            'editor': self.author.username,
            'updated_at': self.updated_at,
        }

    def __repr__(self):
        return f'<Edit {self.id}>'
