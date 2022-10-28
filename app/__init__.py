from flask import Flask

app = Flask(__name__)

#app.config.from_pyfile('settings.py')

if __name__ == '__main__':
    app.run(debug=True)

from app import routes