from flask_sqlalchemy import SQLAlchemy
from app import app

# Connect to a cloud Postgres database
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://yhkrulyb:E3SjR2v11GFmcwaPQocMF0PWHOVGRpIf@jelani.db.elephantsql.com/yhkrulyb"
db = SQLAlchemy(app)

class News(db.Model):
    __tablename__ = "news"
    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.String(10), nullable=False)
    time = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(10), nullable=True)
    url = db.Column(db.String(10), nullable=True)
    comments = db.Column(db.ARRAY(db.Integer), nullable=True)


    def __repr__(self):
        return f'<News: id- {self.id} type- {self.type} title- {self.title} >'

db.create_all()