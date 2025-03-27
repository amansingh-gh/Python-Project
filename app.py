from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "secret_key"

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["voting_system"]
users_collection = db["users"]
votes_collection = db["votes"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if users_collection.find_one({"username": username}):
            return "User already exists!"
        
        users_collection.insert_one({"username": username, "password": password})
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({"username": username, "password": password})
        
        if user:
            session['username'] = username
            return redirect('/vote')
        else:
            return "Invalid credentials!"
    return render_template('login.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'username' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        candidate = request.form['candidate']
        username = session['username']
        
        if votes_collection.find_one({"username": username}):
            return "You have already voted!"
        
        votes_collection.insert_one({"username": username, "candidate": candidate})
        return "Vote recorded successfully!"
    
    return render_template('vote.html')

@app.route('/results')
def results():
    vote_counts = votes_collection.aggregate([
        {"$group": {"_id": "$candidate", "count": {"$sum": 1}}}
    ])
    return render_template('results.html', results=vote_counts)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
