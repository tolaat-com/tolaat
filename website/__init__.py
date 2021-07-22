import os

from flask import Flask


from . import logconfig
from . import hebrew
from . import db
from . import bodily_harm
from . ugc import Ugc

from . import infrastructure
from . import login

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_pyfile('config.py', silent=True)


    from .bp_search import search_blueprint
    from .bp_document import doc_blueprint
    from .bp_view import view_blueprint
    from .bp_static import static_blueprint
    from .bp_preview import preview_blueprint
    from .bp_ugc import ugc_blueprint
    from .bp_scrap import scrap_blueprint
    from .bp_incoming import incoming_email_blueprint
    from .bp_rest import rest_blueprint

    app.register_blueprint(search_blueprint)
    app.register_blueprint(doc_blueprint)
    app.register_blueprint(view_blueprint)
    app.register_blueprint(static_blueprint)
    app.register_blueprint(preview_blueprint)
    app.register_blueprint(ugc_blueprint)
    app.register_blueprint(scrap_blueprint)
    app.register_blueprint(incoming_email_blueprint)
    app.register_blueprint(rest_blueprint)



    infrastructure.add_infrastructure(app)
    login.add_login(app)

    return app
