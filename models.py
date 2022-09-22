from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# Connect to a cloud Postgres database
def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://yhkrulyb:E3SjR2v11GFmcwaPQocMF0PWHOVGRpIf@jelani.db.elephantsql.com/yhkrulyb"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

class News(db.Model):
    __tablename__ = "news"
    id = db.Column(db.Integer, primary_key = True)
    key = db.Column(db.Integer, nullable=True)
    type = db.Column(db.String(), nullable=False)
    author = db.Column(db.String(), nullable=False)
    source = db.Column(db.String(), nullable=False)
    time = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(), nullable=False)
    url = db.Column(db.String(), nullable=False)
    comments = db.relationship("Comments", backref="news")

    def __repr__(self):
        return f'<News: id- {self.id} type- {self.type} title- {self.title} >'

class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key = True)
    key = db.Column(db.Integer, nullable=True)
    time = db.Column(db.Integer, nullable=False)
    text= db.Column(db.String(), nullable=True)
    news_id = db.Column(db.Integer, db.ForeignKey("news.id"))


    def __repr__(self):
        return f'<Comments: id- {self.id} news_id- {self.news_id} text- {self.text} >'

