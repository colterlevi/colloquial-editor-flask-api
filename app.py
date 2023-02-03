import os
import redis
from datetime import timedelta
from flask import Flask, send_file, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from models import db, Author, Article
from pprint import pprint
import platform
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, get_jwt

ACCESS_EXPIRES = timedelta(hours=1)

app = Flask(__name__, static_folder='public')
CORS(app, origins=['*'])
app.config.from_object(Config)
jwt = JWTManager(app)
db.init_app(app)
migrate = Migrate(app, db)

# In Rails, controller actions and routes are separate
# Here in Flask, they are put together
@app.get('/')
def home():
    return send_file('welcome.html')


@app.get('/info')
def info():
    print(dir(platform))
    return {'machine': platform.node()}


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
    author = Author(data['first_name'], data['last_name'], data['email'], data['username'], data['password'], data['admin'])
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
    author.username = request.form['username']
    db.session.commit()
    return jsonify(author.to_dict())

@app.get('/articles')
def all_articles():
    articles = Article.query.all()
    Article.query.count()
    return jsonify([article.to_dict() for article in articles])


@app.get('/articles/<int:id>')
def show_post(id):
    article = Article.query.get(id)
    return jsonify(article.to_dict())


@app.patch('/articles/<int:id>')
def update_article(id):
    article = Article.query.get_or_404(id)
    # currently only updates the username. Add more as you see fit
    article.title = request.json['title']
    article.content = request.json['content']
    db.session.commit()
    return jsonify(article.to_dict())


if __name__ == '__main__':
    app.run(host="localhost", port = os.environ.get('PORT', 3000))
