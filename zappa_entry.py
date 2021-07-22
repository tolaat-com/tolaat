from website import create_app

# This is the entry point for
# lambda. All the whole point is
# to expose a flask app called 'app'
# don't call run!
app = create_app()
