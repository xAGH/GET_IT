from flask import Flask
app = Flask(__name__)
#alejo
@app.route('/')
def index():
    return render_template('index.html')
    