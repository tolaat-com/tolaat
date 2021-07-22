from flask import render_template, Response, Blueprint, current_app
from os.path import dirname, join, exists
from . import hebrew

static_blueprint = Blueprint('static_blueprint', __name__)


@static_blueprint.route(f'/{hebrew.about}')
def about():
    return render_template('about.html')


@static_blueprint.route(f'/{hebrew.privacy}')
def privacy():
    return render_template('privacy.html')


@static_blueprint.route(f'/{hebrew.no_censorship}')
def no_censorship():
    return render_template('no_censorship.html')


@static_blueprint.route(f'/{hebrew.contact}')
def contact():
    return render_template('contact.html')


@static_blueprint.route(f'/{hebrew.changelog}')
def changelog():
    return render_template('changelog.html')


@static_blueprint.route(f'/{hebrew.bodily_harm_link}')
def bodily_harm_v():
    return render_template('bodily_harm.html')


@static_blueprint.route(f'/{hebrew.search}')
def search():
    return render_template('search.html')

@static_blueprint.route(f'/{hebrew.developers}')
def developers():
    return render_template('developers.html')


@static_blueprint.route('/robots.txt')
def robots():
    return Response(render_template('robots.txt'), mimetype='text/plain')


@static_blueprint.route('/' + hebrew.version)
def version():
    major, minor = current_app.config['MAJOR'], current_app.config['MINOR']
    from os import environ
    stage = environ.get('STAGE')
    root = dirname(dirname(__file__))
    deployed_f = join(root, 'instance', 'deployed.txt')
    try:
        deployed_ts = open(deployed_f, 'r').read()
    except:
        deployed_ts = '?'
    return f'{major}.{minor} {stage} {deployed_ts}'