from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    username = db.Column(db.String(20), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    feedback = db.relationship('Feedback', backref='user', cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', first_name='{self.first_name}', last_name='{self.last_name}')>"

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)

    def __repr__(self):
        return f"<Feedback(id='{self.id}', title='{self.title}', content='{self.content}', username='{self.username}')>"
