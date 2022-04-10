from flask import Flask, render_template, request, url_for, redirect, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bootstrap import Bootstrap
import os
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from forms import LoginForm, RegisterForm, CreateForm, CommentForm
from flask_migrate import Migrate

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

    # cafe_author = relationship('Cafe', backref='cafe_author')
    # commenter = relationship('Comment', backref='commenter')

    def __repr__(self):
        return '<User: {}>'.format(self.id)


class Cafe(db.Model):
    __tablename__ = 'cafe'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(250))
    img_url = db.Column(db.String(250))
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.Boolean)
    has_toilet = db.Column(db.Boolean)
    has_wifi = db.Column(db.Boolean)
    can_take_calls = db.Column(db.Boolean)
    seats = db.Column(db.String(250))
    coffee_price = db.Column(db.String(250))

    # author_id = db.Column(db.Integer, db.ForeignKey('users.id'))#connect to table named "users", get id
    # author= relationship("User", backref = "author", foreign_keys = [author_id])
    # comments = relationship("Comment", backref ='cafe_posts')

    def __repr__(self):
        return '<Cafe: {}>'.format(self.id)


# class Comment(db.Model):
#     __tablename__ = "comments"
#     id = db.Column(db.Integer, primary_key=True)
#     cafe_id = db.Column(db.Integer, db.ForeignKey("cafe.id"))
#     author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
#     cafes = relationship("Cafe", backref="cafe_comments", foreign_keys=[cafe_id])
#     # author = relationship("User", backref="author", foreign_keys = [author_id])
#     text = db.Column(db.Text, nullable=False)
#
#
#     def __repr__(self):
#         return '<Comment: {}>'.format(self.id)

db.create_all()


# for deleting posts
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def home():
    all_cafes = Cafe.query.all()
    return render_template('index.html', all_cafes=all_cafes, current_user=current_user)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))

    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/<int:cafe_id>', methods=['POST', 'GET'])
def open_cafe_page(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=form.comment_text.data,
            comment_author=current_user,
            cafe_post=cafe
        )
        db.session.add(new_comment)
        db.session.commit()

    return render_template('coffee_details.html', cafe=cafe, form=form, current_user=current_user)


@app.route('/add_new_cafe', methods=['POST', 'GET'])
def create_new_cafe():
    form = CreateForm()
    if form.validate_on_submit():
        try:
            new_cafe = Cafe(
                name=form.name.data,
                map_url=form.map_url.data,
                img_url=form.img_url.data,
                location=form.location.data,
                has_sockets=form.has_sockets.data,
                has_toilet=form.has_toilet.data,
                has_wifi=form.has_wifi.data,
                can_take_calls=form.can_take_calls.data,
                seats=form.seats.data,
                coffee_price=form.coffee_price.data,
            )

            db.session.add(new_cafe)
            db.session.commit()
            return redirect(url_for('home'))

        except:
            flash('Cafe name already added. Try Editing existing entry.')
            return render_template('create_new_cafe.html', form=form, add_new=True)
    return render_template('create_new_cafe.html', form=form, add_new=True)


@app.route('/edit_rating/<int:cafe_id>', methods=['POST', 'GET'])
def edit_rating(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    edit_form = CreateForm(
        name=cafe.name,
        map_url=cafe.map_url,
        img_url=cafe.img_url,
        location=cafe.location,
        has_sockets=cafe.has_sockets,
        has_toilet=cafe.has_toilet,
        has_wifi=cafe.has_wifi,
        can_take_calls=cafe.can_take_calls,
        seats=cafe.seats,
        coffee_price=cafe.coffee_price,

    )
    if edit_form.validate_on_submit():
        cafe.name = edit_form.name.data
        cafe.map_url = edit_form.map_url.data
        cafe.img_url = edit_form.img_url.data
        cafe.location = edit_form.location.data
        cafe.has_sockets = edit_form.has_sockets.data
        cafe.has_toilet = edit_form.has_toilet.data
        cafe.has_wifi = edit_form.has_wifi.data
        cafe.can_take_calls = edit_form.can_take_calls.data
        cafe.seats = edit_form.seats.data
        cafe.coffee_price = edit_form.coffee_price.data
        db.session.commit()
        return render_template('coffee_details.html', id=cafe_id, cafe=cafe)

    return render_template('edit_ratings.html', cafe=cafe, form=edit_form)


@app.route('/about_me')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
