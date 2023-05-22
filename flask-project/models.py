from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
loginManager = LoginManager()


class UserModel(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    passwordHash = db.Column(db.String(128), nullable=False)

    def setPassword(self, password):
        self.passwordHash = generate_password_hash(password)

    def checkPassword(self, password):
        return check_password_hash(self.passwordHash, password)


@loginManager.user_loader
def loadUser(id):
    return UserModel.query.get(int(id))
