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
    type = db.Column(db.String(20), nullable=False)
    source = db.Column(db.String(20), nullable=False)
    time = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(120), nullable=True)
    url = db.Column(db.String(120), nullable=True)
    comments = db.Column(db.ARRAY(db.Integer), nullable=True)


    def __repr__(self):
        return f'<News: id- {self.id} type- {self.type} title- {self.title} >'

