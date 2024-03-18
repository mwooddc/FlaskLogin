from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user









db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)




    #A SECRET KEY is required for use of sessions, it is used to encode the session
    # See https://youtu.be/PYILMiGxpAU?t=327 
    # Note we use flask_login to manage sessions but still need this secret key
    app.config['SECRET_KEY'] = "helloworld"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    csrf = CSRFProtect(app)
    db.init_app(app)

    #see files auth.py and views.py for explanation and video link to why blueprints are used
    #These 4 lines are required so that the Blueprints from views.py and auth.py are imported
    #and registered
    from .views import views
    from .auth import auth
    from .player import player
    from .coach import coach
    #You can change the prefix if needed e.g. url_prefix="/moon/" would mean that all routes
    #from that blueprint can only be accessed first by going to the prefix URL
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(player, url_prefix="/")
    app.register_blueprint(coach, url_prefix="/")

    from .models import User, count_unread_notifications

    with app.app_context():
        db.create_all()

        # Assuming count_unread_notifications is defined as shown previously
    @app.context_processor
    def inject_unread_notifications_count():
        if current_user.is_authenticated:
            unread_count = count_unread_notifications(current_user.id)
        else:
            unread_count = 0
        return dict(unread_notifications_count=unread_count)

    #The line below will call the function on line 54 to create the database
    #Obviously we don't want to do this EVERY time otherwise it will create
    #A blank new databse each time
    # create_database(app)

    #Next 6 lines of code are required to use login manager
    #see this video: https://youtu.be/2dEM-s3mRLE
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)
    #To understand this specifically see: https://youtu.be/2dEM-s3mRLE?t=432
    #This special function maps login managers abstract user with
    #an actual user in your database
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

#see comment above on line 34
# def create_database(app):
#     if not path.exists("website/" + DB_NAME):
#         db.create_all()
#         print("Created database!")


