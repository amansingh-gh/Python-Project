from flask import Flask, render_template, request, redirect, session, flash, url_for
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your-secret-key-123"

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["voting_db"]
users = db.users
votes = db.votes

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if users.find_one({"username": username}):
            flash("Username already exists. Please choose another.", "error")
        else:
            users.insert_one({
                "username": username,
                "password": password,
                "created_at": datetime.now()
            })
            flash("Registration successful! Please login to continue.", "success")
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({"username": username, "password": password})
        
        if user:
            session['username'] = username
            return redirect(url_for('vote'))
        else:
            flash("Invalid username or password. Please try again.", "error")
    
    return render_template('login.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        candidate = request.form['candidate']
        votes.insert_one({
            "username": session['username'],
            "candidate": candidate,
            "voted_at": datetime.now()
        })
        flash("Your vote has been submitted successfully!", "success")
        return redirect(url_for('results'))
    
    return render_template('vote.html')

@app.route('/results')
def results():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    results = list(votes.aggregate([
        {"$group": {"_id": "$candidate", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]))
    
    total_votes = sum(result['count'] for result in results)
    
    return render_template('results.html', 
                         results=results, 
                         total_votes=total_votes)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)