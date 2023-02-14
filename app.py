import os
import redis
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from flask import Flask, send_file, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from models import db, Author, Article, Edit, Category, Tag
from pprint import pprint
import platform
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, get_jwt, set_access_cookies, unset_jwt_cookies

ACCESS_EXPIRES = timedelta(hours=1)

app = Flask(__name__, static_folder='public')
CORS(app, origins=['*'])
app.config.from_object(Config)
jwt = JWTManager(app)
db.init_app(app)
migrate = Migrate(app, db)

@app.get('/')
def home():
    return send_file('welcome.html')

jwt = JWTManager(app)


# # Using an `after_request` callback, we refresh any token that is within 30
# # minutes of expiring. Change the timedeltas to match the needs of your application.
# @app.after_request
# def refresh_expiring_jwts(response):
#     try:
#         exp_timestamp = get_jwt()["exp"]
#         now = datetime.now(timezone.utc)
#         target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
#         if target_timestamp > exp_timestamp:
#             access_token = create_access_token(identity=get_jwt_identity())
#             set_access_cookies(response, access_token)
#         return response
#     except (RuntimeError, KeyError):
#         # Case where there is not a valid JWT. Just return the original response
#         return response


@app.post('/login')
def login():
    data = request.json
    author = Author.query.filter_by(email=data['email']).first()
    if not author:
        return jsonify({'error': 'No author found'}), 404
    given_password = data['password']
    if author.password == given_password:
        # encode JWT as the token variable, signing it with our application's secret key
        # we store only what the token will need while identifying the authors on any given request
        token = create_access_token(identity=author.id)
        return jsonify({'author': author.to_dict(), 'token': token})
    else:
        return jsonify({'error': 'Invalid email or password'}), 422


# Setup our redis connection for storing the blocklisted tokens. You will probably
# want your redis instance configured to persist data to disk, so that a restart
# does not cause your application to forget that a JWT was revoked.
jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)

# Callback function to check if a JWT exists in the redis blocklist
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


# Endpoint for revoking the current users access token. Save the JWTs unique
# identifier (jti) in redis. Also set a Time to Live (TTL)  when storing the JWT
# so that it will automatically be cleared out of redis after the token expires.
@app.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)
    return jsonify(msg="Access token revoked")


@app.get('/authors/<int:id>')
def show(id):
    author = Author.query.get(id)
    if author:
        return jsonify(author.to_dict())
    else:
        return {}, 404


@app.get("/who_am_i")
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    author = Author.query.get(current_user)
    # We can now access our sqlalchemy User object via `current_user`.
    if author:
        print(author)
        return jsonify(author.to_dict())
    else:
        return {}, 404


@app.post('/authors')
def create_author():
    data = request.json
    author = Author(data['first_name'], data['last_name'],
                    data['username'], data['email'], data['password'], data['admin'])
    print(data)
    db.session.add(author)
    db.session.commit()
    return jsonify(author.to_dict()), 201

@app.get('/authors')
def all_authors():
    authors = Author.query.all()
    Author.query.count()
    return jsonify([author.to_dict() for author in authors])


@app.patch('/authors/<int:id>')
def update_author(id):
    author = Author.query.get_or_404(id)
    # currently only updates the username. Add more as you see fit
    author.username = request.json['username']
    author.first_name = request.json['first_name']
    author.last_name = request.json['last_name']
    author.bio = request.json['bio']
    author.admin = request.json['admin']
    db.session.commit()
    return jsonify(author.to_dict())


@app.delete('/authors/<int:id>')
@jwt_required()
def delete_author(id):
    author = Author.query.get(id)
    if author:
        db.session.delete(author)
        db.session.commit()
        print('deleting author')
        return jsonify(author.to_dict())
    else:
        return {'error': 'No user found'}, 404

@app.get('/articles')
def all_articles():
    articles = Article.query.all()
    Article.query.count()
    return jsonify([article.to_dict() for article in articles])


@app.get('/articles/<int:id>')
def show_post(id):
    article = Article.query.get(id)
    return jsonify(article.to_dict())


@app.get('/edits')
def all_edits():
    edits = Edit.query.all()
    Edit.query.count()
    return jsonify([edit.to_dict() for edit in edits])


@app.post('/articles')
@jwt_required()
def create_article():
    current_user = get_jwt_identity()
    data = request.json
    article = Article(data['content'], data['title'],
                      author_id=current_user)
    if article.tags is None:
        article.tags = []
    if article.categories is None:
        article.categories = []
    tags_str = request.json['tags']
    tags = list(map(str, tags_str.split(', ')))
    for t in tags:
        tag = Tag.query.filter_by(name=t).first()
        if tag:
            tag.count += 1
            article.tags.append(tag.id)
        else:
            tag = Tag(name=t)
            db.session.add(tag)
            article.tags.append(tag.id)
    cat_str = request.json['categories']
    categories = list(map(str, cat_str.split(',')))
    for cat in categories:
        category = Category.query.filter_by(name=cat).first()
        if category:
            category.count += 1
            article.categories.append(category.id)
        else:
            category = Category(name=cat)
            db.session.add(category)
            article.categories.append(category.id)
    print(article)
    db.session.add(article)
    db.session.commit()
    return jsonify(article.to_dict()), 201


@app.patch('/articles/<int:id>')
@jwt_required()
def update_article(id):
    current_user = get_jwt_identity()
    article = Article.query.get_or_404(id)
    if article.tags is None:
        article.tags = []
    if article.categories is None:
        article.categories = []
    tags_str = request.json['tags']
    tags = list(map(str, tags_str.split(', ')))
    for t in tags:
        tag = Tag.query.filter_by(name=t).first()
        if tag.id not in article.tags:
            tag.count += 1
            article.tags.append(tag.id)
        else:
            tag = Tag(name=t)
            db.session.add(tag)
            article.tags.append(tag.id)
    cat_str = request.json['categories']
    categories = list(map(str, cat_str.split(',')))
    for cat in categories:
        category = Category.query.filter_by(name=cat).first()
        if category.id not in article.categories:
            category.count += 1
            article.categories.append(category.id)
        else:
            category = Category(name=cat)
            db.session.add(category)
            article.categories.append(category.id)
    article.content = request.json['content']
    article.title = request.json['title']
    edit = Edit(article_id=article.id, author_id=current_user)
    db.session.add(edit)
    db.session.commit()
    return jsonify(article.to_dict())


@app.delete('/articles/<int:id>')
@jwt_required()
def delete_article(id):
    article = Article.query.get(id)
    if article:
        db.session.delete(article)
        db.session.commit()
        print('deleting article')
        return jsonify(msg="Article DELETED"), 201
    else:
        return {'error': 'No article found'}, 404


@app.get('/categories')
def all_categories():
    categories = Category.query.all()
    Category.query.count()
    return jsonify([category.to_dict() for category in categories])


@app.get('/tags')
def all_tags():
    tags = Tag.query.all()
    Tag.query.count()
    return jsonify([tag.to_dict() for tag in tags])


if __name__ == '__main__':
    app.run(host="localhost", port = os.environ.get('PORT', 3000))
