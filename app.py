from flask import Flask, render_template, request, redirect, url_for, session
import pickle

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load the trained model
model = pickle.load(open('crop_model.pkl', 'rb'))

# In-memory user database
users_db = {}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users_db and users_db[username]['password'] == password:
            session['user_id'] = username
            return redirect(url_for('profile'))
        return "Invalid credentials!"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if username in users_db:
            return "User already exists!"
        users_db[username] = {'password': password, 'email': email}
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = session['user_id']
    email = users_db[user]['email']
    return render_template('profile.html', username=user, email=email)

@app.route('/crop-recommendation', methods=['GET', 'POST'])
def crop_recommendation():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            # Collect input data
            features = [
                float(request.form[key])
                for key in [
                    'Winter_MAX_TEMP', 'Summer_MAX_TEMP', 'Rainy_MAX_TEMP', 'Autumn_MAX_TEMP',
                    'Winter_MIN_TEMP', 'Summer_MIN_TEMP', 'Rainy_MIN_TEMP', 'Autumn_MIN_TEMP',
                    'Winter_PERCIP', 'Summer_PERCIP', 'Rainy_PERCIP', 'Autumn_PERCIP',
                    'Winter_WINDSPEED', 'Summer_WINDSPEED', 'Rainy_WINDSPEED', 'Autumn_WINDSPEED',
                    'NITROGEN_CONSUMPTION', 'PHOSPHATE_CONSUMPTION', 'POTASH_CONSUMPTION'
                ]
            ]
            # Predict crop
            crop = model.predict([features])[0]
            return render_template('result.html', crop=crop)
        except Exception as e:
            return f"Error: {e}", 400
    return render_template('crop_recommendation.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
