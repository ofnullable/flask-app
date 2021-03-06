from flask import Flask
from flask_apispec import FlaskApiSpec

from bugbounty.domain.program.controller import bp as program_bp, get_programs
from bugbounty.domain.user.controller import bp as user_bp
from bugbounty.env.exceptions import Commons
from bugbounty.env.extensions import db, bcrypt, cors, migrate
from bugbounty.settings import DevConfig


def create_app(config=DevConfig):
    # create and configure the bugbounty app
    print('create and configure the bugbounty app', config)
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_object(config)

    register_extensions(app)
    register_blueprints(app)
    register_error_handler(app)

    register_router_documents(app)

    return app


def register_extensions(app):
    print('register extensions...')
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.drop_all()
        db.create_all()


def register_blueprints(app):
    print('register blueprints...')
    origins = ['http://localhost:3000']
    cors.init_app(user_bp, origins=origins)
    cors.init_app(program_bp, origins=origins)

    app.register_blueprint(user_bp)
    app.register_blueprint(program_bp)


def register_error_handler(app):
    @app.errorhandler(404)
    def not_found_handler(_):
        return {'message': 'API not found'}, 404

    @app.errorhandler(422)
    def bad_request_handler(e):
        return {'message': 'wrong or missing request property', 'fields': e.data['messages']}, 400

    def error_handler(error):
        res = error.to_json()
        res.status_code = error.status_code
        return res

    app.errorhandler(Commons)(error_handler)


def register_router_documents(app):
    print('register api documentations')
    spec = FlaskApiSpec(app=app)
    spec.register_existing_resources()
