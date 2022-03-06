from app import db

# Creating table for User login/register
class user(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    items = db.relationship('storage', backref='owned_user', lazy=True)
    time = db.relationship('history', backref='owner_history', lazy=True)
    def __repr__(self):
        return f'user {self.id, self.username, self.password_hash}'

#Creating table to store data from user's storage
class storage(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    item = db.Column(db.String(length=30), nullable=False)
    quantity = db.Column(db.Integer(), nullable=False)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    def __repr__(self):
        return f'storage {self.id, self.item, self.quantity, self.owner}'

# Creating table for user's history of adds/removes
class history(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    item = db.Column(db.String(length=30), nullable=False)
    type = db.Column(db.String(length=7), nullable=False)
    quantity = db.Column(db.Integer(), nullable=False)
    price = db.Column(db.Integer())
    date = db.Column(db.String(length=12), nullable=False)
    time = db.Column(db.String(length=5), nullable=False)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    def __repr__(self):
        return f'history {self.id, self.item, self.type, self.quantity, self.price, self.time, self.owner}'

# Creating table for contact form
class contact(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(length=400), nullable=False)
    message = db.Column(db.Integer(), nullable=False)
    def __repr__(self):
        return f'contact {self.id, self.email, self.message}'