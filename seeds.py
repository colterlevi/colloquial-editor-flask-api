from app import app
from models import db, Author, Article
from faker import Faker

def run_seeds():
    fake = Faker()
    print('Seeding database ... 🌱')
    # Add your seed data here
    with app.app_context():
      user1 = Author("Colter", "Longshore", "colterlevi", "cllongshore@gmail.com", '1111', True)
      user2 = Author("Cooper", "Hall", "coopdoggydog", "cooper@example.com", '2222', False)
      db.session.add_all([user1, user2])
      db.session.commit()
      user = Author.query.first()
      seeded_posts = []
      for _ in range(5):
        post = Article(fake.text())
        post.author_id = 1
        seeded_posts.append(post)
      db.session.add_all(seeded_posts)
      db.session.commit()
      print('Done! 🌳')

run_seeds()