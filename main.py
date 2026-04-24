from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///profiles.db'
db = SQLAlchemy(app)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password = db.Column(db.Text, nullable=False)


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        full_name = request.form['full-name']
        email = request.form['email']
        phone_number = request.form['phone']
        password = (request.form['password']).rstrip()
        confirm_password = (request.form['confirm-password']).rstrip()

        hashed_password = generate_password_hash(password)

        print(hashed_password)

        new_profile = Profile(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            password=hashed_password)

        error = False
        if password == confirm_password:
            try:
                db.session.add(new_profile)
                db.session.commit()
                return redirect('/succesfuly-registered')
            except:
                return 'Error occurred while creating profile.'

        else:
            error = True
            return render_template('register.html',
                                   error=error,
                                   full_name=full_name,
                                   email=email,
                                   phone_number=phone_number)

    else:
        return render_template('register.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/report')
def report():
    return render_template('report.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)