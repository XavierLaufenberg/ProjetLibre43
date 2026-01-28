from flask import Flask, render_template

app = Flask("Pikapp")

@app.route('/')
def index():
    return render_template("index.html")

app.run(host='0.0.0.0', port=81)