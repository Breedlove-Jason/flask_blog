"""Flask blog: explicit administrator, validated forms, and CSRF-protected writes."""
import os
from datetime import date
from functools import wraps
import bleach
import click
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from markupsafe import Markup
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from journal import NOTES

load_dotenv()
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ['SECRET_KEY'],
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///blog-local.db').replace('postgres://', 'postgresql+psycopg://', 1).replace('postgresql://', 'postgresql+psycopg://', 1),
    ADMIN_USER_ID=int(os.getenv('ADMIN_USER_ID', '0')),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.getenv('APP_ENV') == 'production',
    MAX_CONTENT_LENGTH=1024 * 1024,
)
if os.getenv('VERCEL') and not os.getenv('DATABASE_URL'):
    raise RuntimeError('Set DATABASE_URL to a persistent database before deploying.')
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    posts = db.relationship('BlogPost', backref='user')
    comments = db.relationship('Comment', backref='user')

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments = db.relationship('Comment', backref='blog_post', cascade='all, delete-orphan')

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blogpost_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
    text = db.Column(db.String(250), nullable=False)

def is_admin():
    return current_user.is_authenticated and current_user.id == app.config['ADMIN_USER_ID']

def admin_only(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not is_admin():
            abort(403)
        return fn(*args, **kwargs)
    return wrapped

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None

@app.context_processor
def template_helpers():
    return {'is_admin': is_admin()}

@app.template_filter('safe_body')
def safe_body(value):
    return Markup(bleach.clean(value or '', tags=['p','br','strong','em','ul','ol','li','blockquote','h2','h3','a','pre','code'], attributes={'a':['href','title']}, protocols=['https','http'], strip=True))

@app.route('/')
def get_all_posts():
    return render_template('index.html', all_posts=BlogPost.query.order_by(BlogPost.id.desc()).limit(100).all(), notes=NOTES)

@app.route('/notes/<slug>')
def project_note(slug):
    note = next((item for item in NOTES if item['slug'] == slug), None)
    if note is None:
        abort(404)
    return render_template('note.html', note=note)

@app.route('/editor')
@login_required
def editor():
    if not is_admin():
        return render_template('editor-pending.html', setup_pending=app.config['ADMIN_USER_ID'] == 0), 403
    return render_template('editor.html', posts=BlogPost.query.order_by(BlogPost.id.desc()).all())

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.strip().lower(), name=form.name.data.strip(),
                    password=generate_password_hash(form.password.data))
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Unable to register that email. Try signing in instead.')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('get_all_posts'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('get_all_posts'))
        flash('Email or password is incorrect.')
    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))

@app.route('/post/<int:post_id>', methods=['GET','POST'])
def show_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        db.session.add(Comment(text=form.comment.data, user_id=current_user.id, blogpost_id=post.id))
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))
    return render_template('post.html', post=post, form=form, comments=post.comments)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/new-post', methods=['GET','POST'])
@login_required
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        post = BlogPost(title=form.title.data, subtitle=form.subtitle.data, body=form.body.data,
                        img_url=form.img_url.data, author_id=current_user.id,
                        date=date.today().strftime('%B %d, %Y'))
        db.session.add(post)
        if save_post():
            return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=form)

def save_post():
    try:
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        flash('That title is already in use. Choose another title.')
        return False

@app.route('/edit-post/<int:post_id>', methods=['GET','POST'])
@login_required
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    form = CreatePostForm(obj=post)
    if form.validate_on_submit():
        form.populate_obj(post)
        if save_post():
            return redirect(url_for('show_post', post_id=post.id))
    return render_template('make-post.html', form=form, is_edit=True)

@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
@admin_only
def delete_post(post_id):
    db.session.delete(db.get_or_404(BlogPost, post_id))
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route('/delete-comment/<int:comment_id>', methods=['POST'])
@login_required
@admin_only
def delete_comment(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    post_id = comment.blogpost_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('show_post', post_id=post_id))

@app.cli.command('init-db')
def init_db():
    db.create_all()
    click.echo('Database tables ready.')

@app.cli.command('create-editor')
@click.option('--email', prompt=True)
@click.option('--name', prompt=True)
@click.password_option()
def create_editor(email, name, password):
    if len(password) < 12:
        raise click.ClickException('Use at least 12 characters.')
    email = email.strip().lower()
    if User.query.filter_by(email=email).first():
        raise click.ClickException('Email already exists; no account was modified.')
    user = User(email=email, name=name.strip(), password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    click.echo(f'Set ADMIN_USER_ID={user.id} in the application environment.')

@app.route('/health')
def health():
    return {'status':'ok'}

if __name__ == '__main__':
    app.run()
