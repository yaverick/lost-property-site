from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import func
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
    creator_name = db.Column(db.String(30), nullable=False)
    creator_phone_number = db.Column(db.String(20), nullable=False)
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
@app.route('/home', methods=['POST', 'GET'])
def home():
    items = LostItem.query.order_by(LostItem.date_posted.desc()).all()
    title_search = request.args.get('title-search', '').strip()
    return render_template('home.html', items=items)

@app.route('/all-items', methods=['POST', 'GET'])
def all_items():
    items = LostItem.query.order_by(LostItem.date_posted.desc()).all()

    title_search = request.args.get('title-search', '').strip()
    city_search = request.args.get('city-search', '').strip()
    sort_type = request.args.get('sort', 'newest')

    items = LostItem.query

    if title_search:
        items = items.filter(
            (LostItem.title.contains(title_search)) |
            (LostItem.text.contains(title_search))
        )
    if city_search:
        items = items.filter(
            (LostItem.city.contains(city_search)) |
            (LostItem.address.contains(city_search))
        )
    if sort_type == 'oldest':
        items = items.order_by(LostItem.date_posted.asc())
    else:
        items = items.order_by(LostItem.date_posted.desc())

    items = items.all()

    return render_template('all_items.html',
                           items=items,
                           title_search=title_search,
                           city_search=city_search,
                           sort_type=sort_type)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = (request.form['name']).rstrip()
        email = (request.form['email']).rstrip()
        phone_number = (request.form['phone']).rstrip()
        password = (request.form['password']).strip()
        confirm_password = (request.form['confirm-password']).strip()

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
                return redirect(url_for('login'))
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

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = (request.form['email']).rstrip()
        password = (request.form['password']).rstrip()

        user = Profile.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect('/home')
        else:
            return render_template('login.html', error='Неправильна пошта або пароль')

    return render_template('login.html')

@app.route('/my-profile')
@login_required
def my_profile():
    items = LostItem.query.filter_by(creator_id=current_user.id)
    items = items.order_by(LostItem.date_posted.desc()).all()
    return render_template('my_profile.html', items=items)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

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
        creator_name = current_user.name
        creator_phone_number = current_user.phone_number

        new_lost_item = LostItem(
            title=title,
            text=text,
            city=city,
            address=address,
            creator_id = creator_id,
            creator_name=creator_name,
            creator_phone_number=creator_phone_number)

        try:
            db.session.add(new_lost_item)
            db.session.commit()
            return redirect(url_for('home'))
        except:
            return render_template('error.html',
                                       error='Під час свторення знахідки виникла помилка.')

    return render_template('report.html')

@app.route('/item-<int:item_id>')
def item_detail(item_id):
    item = LostItem.query.get_or_404(item_id)
    return render_template('item_detail.html', item=item)

@app.route('/delete-item-<int:item_id>>', methods=['POST', 'GET'])
@login_required
def delete_item(item_id):
    item = LostItem.query.get_or_404(item_id)
    if current_user.id == item.creator_id:
        try:
            db.session.delete(item)
            db.session.commit()
        except:
            db.session.rollback()

    return redirect(url_for('all_items'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)