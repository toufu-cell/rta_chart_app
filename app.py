from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rta_chart.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大16MB

db = SQLAlchemy(app)

# アップロードディレクトリの作成
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

class Chart(db.Model):
    __tablename__ = 'charts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    steps = db.relationship('Step', backref='chart', lazy=True)

class Step(db.Model):
    __tablename__ = 'steps'
    id = db.Column(db.Integer, primary_key=True)
    chart_id = db.Column(db.Integer, db.ForeignKey('charts.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    memo = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    charts = Chart.query.all()
    return render_template('chart_list.html', charts=charts)

@app.route('/chart/create', methods=['GET', 'POST'])
def create_chart():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        
        new_chart = Chart(title=title, category=category)
        db.session.add(new_chart)
        db.session.commit()
        
        return redirect(url_for('chart_detail', chart_id=new_chart.id))
    
    return render_template('chart_form.html')

@app.route('/chart/<int:chart_id>')
def chart_detail(chart_id):
    chart = Chart.query.get_or_404(chart_id)
    steps = Step.query.filter_by(chart_id=chart_id).order_by(Step.order).all()
    return render_template('chart_detail.html', chart=chart, steps=steps)

@app.route('/chart/<int:chart_id>/edit', methods=['GET', 'POST'])
def edit_chart(chart_id):
    chart = Chart.query.get_or_404(chart_id)
    if request.method == 'POST':
        chart.title = request.form.get('title')
        chart.category = request.form.get('category')
        db.session.commit()
        return redirect(url_for('chart_detail', chart_id=chart_id))
    
    return render_template('chart_detail.html', chart=chart)

@app.route('/chart/<int:chart_id>/delete', methods=['POST'])
def delete_chart(chart_id):
    chart = Chart.query.get_or_404(chart_id)
    Step.query.filter_by(chart_id=chart_id).delete()
    db.session.delete(chart)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/chart/<int:chart_id>/step/create', methods=['GET', 'POST'])
def create_step(chart_id):
    if request.method == 'POST':
        order = request.form.get('order', type=int)
        title = request.form.get('title')
        memo = request.form.get('memo')
        
        if not order or order < 1:
            order = 1
            
        new_step = Step(chart_id=chart_id, order=order, title=title, memo=memo)
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                base, ext = os.path.splitext(filename)
                filename = f"{base}_{int(time.time())}{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_step.image_path = filename

        db.session.add(new_step)
        db.session.commit()
        return redirect(url_for('chart_detail', chart_id=chart_id))

    chart = Chart.query.get_or_404(chart_id)
    max_order = db.session.query(db.func.max(Step.order)).filter_by(chart_id=chart_id).scalar()
    next_order = (max_order or 0) + 1
    return render_template('step_form.html', chart=chart, step=None, next_order=next_order)

@app.route('/chart/<int:chart_id>/step/<int:step_id>/edit', methods=['GET', 'POST'])
def edit_step(chart_id, step_id):
    step = Step.query.get_or_404(step_id)
    if request.method == 'POST':
        step.order = request.form.get('order', type=int)
        step.title = request.form.get('title')
        step.memo = request.form.get('memo')
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                if step.image_path:
                    old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], step.image_path)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                filename = secure_filename(file.filename)
                base, ext = os.path.splitext(filename)
                filename = f"{base}_{int(time.time())}{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                step.image_path = filename
        
        elif request.form.get('remove_image'):
            if step.image_path:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], step.image_path)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
                step.image_path = None

        db.session.commit()
        return redirect(url_for('chart_detail', chart_id=chart_id))

    chart = Chart.query.get_or_404(chart_id)
    return render_template('step_form.html', chart=chart, step=step)

@app.route('/chart/<int:chart_id>/step/<int:step_id>/delete', methods=['POST'])
def delete_step(chart_id, step_id):
    step = Step.query.get_or_404(step_id)
    if step.image_path:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], step.image_path)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(step)
    db.session.commit()
    return redirect(url_for('chart_detail', chart_id=chart_id))

@app.route('/update_step_orders', methods=['POST'])
def update_step_orders():
    updates = request.json.get('updates', [])
    for update in updates:
        step = Step.query.get(update['stepId'])
        if step:
            step.order = update['newOrder']
    
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/chart/<int:chart_id>/step/<int:step_id>')
def step_detail(chart_id, step_id):
    chart = Chart.query.get_or_404(chart_id)
    step = Step.query.get_or_404(step_id)
    return render_template('step_detail.html', chart=chart, step=step)

if __name__ == '__main__':
    app.run(debug=True)