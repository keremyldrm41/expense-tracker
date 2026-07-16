from flask import Flask

app = Flask(__name__)
@app.route('/')
def hello_expense():
    return 'Hello expense-tracker!'

@app.route('/about')
def about_expense():
    return 'About expense-tracker!'