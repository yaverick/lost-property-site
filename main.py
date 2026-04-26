from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import pytz


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///profiles.db'
app.config['SQLALCHEMY_BINDS'] = {'lost_items': 'sqlite:///lost_items.db'}
db = SQLAlchemy(app)


def get_kyiv_time():
    return datetime.now(pytz.timezone('Europe/Kyiv'))


class Profile(db.Model, UserMixin):
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password = db.Column(db.Text, nullable=False)


class LostItem(db.Model):
    __bind_key__ = 'lost_items'
    __tablename__ = 'lost_items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.Integer, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=get_kyiv_time)


app.secret_key = '5732857ukklqdl353shdgfs'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Profile, int(user_id))

@app.context_processor
def inject_user():
    return dict(current_user=current_user)


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Profile.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect('/home')
        else:
            return render_template('login.html', error='Неправильна пошта або пароль')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/home')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone_number = request.form['phone']
        password = (request.form['password']).rstrip()
        confirm_password = (request.form['confirm-password']).rstrip()

        hashed_password = generate_password_hash(password)

        new_profile = Profile(
            name=name,
            email=email,
            phone_number=phone_number,
            password=hashed_password)

        error = ''
        if password == confirm_password:
            try:
                db.session.add(new_profile)
                db.session.commit()
                return redirect('/login')
            except:
                return render_template('error.html',
                                       error='Під час свторення акаунту виникла помилка.')

        else:
            return render_template('register.html',
                                   error='Паролі не співпадають',
                                   name=name,
                                   email=email,
                                   phone_number=phone_number)

    return render_template('register.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/report', methods=['POST', 'GET'])
@login_required
def report():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        city = request.form['city']
        address = request.form['address']
        creator_id = current_user.id

        new_lost_item = LostItem(
            title=title,
            text=text,
            city=city,
            address=address,
            creator_id=creator_id)

        try:
            db.session.add(new_lost_item)
            db.session.commit()
            return redirect('/home')
        except:
            return render_template('error.html',
                                       error='Під час свторення знахідки виникла помилка.')

    return render_template('report.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)