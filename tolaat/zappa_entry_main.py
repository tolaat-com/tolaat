from os import environ
from website import create_app


app = create_app()
app.run(port=environ.get('PORT', 5000))