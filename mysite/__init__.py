from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
Migrate(app,db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

from mysite.blog_posts.views import blog_posts
app.register_blueprint(blog_posts)

from mysite.core.views import core
app.register_blueprint(core)

from mysite.error_pages.handlers import error_pages
app.register_blueprint(error_pages)

from mysite.users.views import users
app.register_blueprint(users)
