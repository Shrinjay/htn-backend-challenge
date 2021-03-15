import flask as fk
from controller import controller

PORT = 5000

app = fk.Flask(__name__)
app.register_blueprint(controller)

app.run(port=PORT)
