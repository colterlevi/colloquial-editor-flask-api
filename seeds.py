from app import app
from models import db, Author, Article

def run_seeds():
    print('Seeding database ... 🌱')
    # Add your seed data here
    with app.app_context():
      user1 = Author("Colter", "Longshore", "colterlevi", "cllongshore@gmail.com", '1111', True)
      user2 = Author("Cooper", "Hall", "coopdoggydog", "cooper@example.com", '2222', False)
      db.session.add_all([user1, user2])
      db.session.commit()
      print('Done! 🌳')

run_seeds()