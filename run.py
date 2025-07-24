from app import create_app, db
import os

app = create_app()

# with app.app_context():
#     db.create_all()  # This line creates all tables defined in models.py
#     print('mmmm: db.create_all() ')

if __name__ == '__main__':
    app.run(debug=True)
