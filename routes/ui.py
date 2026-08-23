from flask import Blueprint, render_template, redirect, url_for

ui_bp = Blueprint('ui', __name__)

@ui_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('ui.dashboard'))

@ui_bp.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@ui_bp.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@ui_bp.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

@ui_bp.route('/upload', methods=['GET'])
def upload():
    return render_template('upload.html')

@ui_bp.route('/result/<video_id>', methods=['GET'])
def result(video_id):
    return render_template('result.html', video_id=video_id)
