import os
from flask import Flask, send_file, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from models import db, Author, Article
from pprint import pprint
import platform
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, current_user

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


@app.get('/example')
def example():
    return {'message': 'Your app is running Python'}


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


@app.get('/authors/<int:id>')
@jwt_required()
def show(id):
    author = Author.query.get(id)
    if author:
        return jsonify(author.to_dict())
    else:
        return {}, 404


@app.route("/who_am_i", methods=["GET"])
@jwt_required()
def protected():
    # We can now access our sqlalchemy User object via `current_user`.
    return jsonify(current_user.to_dict())


# run user.to_dict() for every user in authors
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


@app.get('/articles/<int:id>')
def show_post(id):
    article = Article.query.get(id)
    return jsonify(article.to_dict())



if __name__ == '__main__':
    app.run(host="localhost", port = os.environ.get('PORT', 3000))
