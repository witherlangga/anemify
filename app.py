try:
    from flask import Flask, render_template, request, redirect, url_for, flash, make_response
    from flask_sqlalchemy import SQLAlchemy
    from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
    from werkzeug.security import generate_password_hash, check_password_hash
    Flask_available = True
except Exception as e:
    Flask = None
    Flask_available = False
    print(f"Flask import error: {e}")

from utils import prediction as prediction_service

if Flask_available:
    app = Flask(__name__)
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/anemiadb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    
    db = SQLAlchemy(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    # User model
    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        predictions = db.relationship('PredictionRecord', backref='user', lazy=True, cascade='all, delete-orphan')
        profile_image = db.Column(db.String(255), nullable=True)
        
        def set_password(self, password):
            self.password_hash = generate_password_hash(password)
        
        def check_password(self, password):
            return check_password_hash(self.password_hash, password)
    
    # Prediction model
    class PredictionRecord(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        timestamp = db.Column(db.DateTime, default=lambda: __import__('datetime').datetime.now())
        model_name = db.Column(db.String(50), nullable=False)
        gender = db.Column(db.Integer, nullable=False)
        hemoglobin = db.Column(db.Float, nullable=False)
        mch = db.Column(db.Float, nullable=False)
        mchc = db.Column(db.Float, nullable=False)
        mcv = db.Column(db.Float, nullable=False)
        prediction_label = db.Column(db.String(50), nullable=False)
        probability_proba = db.Column(db.String(255), nullable=True)  # Store as JSON string
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create tables only when explicitly needed (in __main__ or init_db script)
    
else:
    app = None
    db = None


if app is not None:
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if not username or not email or not password:
                flash('Semua field harus diisi.', 'danger')
                return redirect(url_for('register'))
            
            if password != confirm_password:
                flash('Password tidak cocok.', 'danger')
                return redirect(url_for('register'))
            
            if User.query.filter_by(username=username).first():
                flash('Username sudah terdaftar.', 'danger')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('Email sudah terdaftar.', 'danger')
                return redirect(url_for('register'))
            
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                flash(f'Selamat datang, {username}!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Username atau password salah.', 'danger')
        
        return render_template('login.html')
    
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Anda telah logout.', 'info')
        return redirect(url_for('login'))
    
    
    @app.route('/')
    @login_required
    def home():
        return render_template('home.html', active='home')


    @app.route('/prediction', methods=['GET', 'POST'])
    @login_required
    def prediction():
        if request.method == 'POST':
            import json
            import traceback
            from datetime import datetime
            
            try:
                model = request.form.get('model')
                gender = int(request.form.get('gender'))
                hemoglobin = float(request.form.get('hemoglobin') or 0)
                mch = float(request.form.get('mch') or 0)
                mchc = float(request.form.get('mchc') or 0)
                mcv = float(request.form.get('mcv') or 0)

                if model == 'All Models':
                    raw = prediction_service.predict_all(gender, hemoglobin, mch, mchc, mcv)
                    results = {}
                    for k, v in raw.items():
                        if hasattr(v['proba'], 'tolist'):
                            v['proba'] = v['proba'].tolist()
                        label = prediction_service.get_prediction_label(v['prediction'])
                        results[k] = {'label': label, 'proba': v['proba']}
                        # Save to database
                        try:
                            proba_str = json.dumps(v['proba'])
                            pred_record = PredictionRecord(
                                user_id=current_user.id,
                                model_name=k,
                                gender=gender,
                                hemoglobin=hemoglobin,
                                mch=mch,
                                mchc=mchc,
                                mcv=mcv,
                                prediction_label=label,
                                probability_proba=proba_str
                            )
                            db.session.add(pred_record)
                        except Exception as e:
                            app.logger.exception('Error saving prediction for all models')
                    
                    db.session.commit()
                    return render_template('prediction.html', active='prediction', results=results, results_all=True)
                else:
                    pred = prediction_service.predict(model, gender, hemoglobin, mch, mchc, mcv)
                    if model == 'KNN':
                        proba = prediction_service.predict_proba_knn(gender, hemoglobin, mch, mchc, mcv)
                    elif model == 'Random Forest':
                        proba = prediction_service.predict_proba_rf(gender, hemoglobin, mch, mchc, mcv)
                    else:
                        proba = prediction_service.predict_proba_voting(gender, hemoglobin, mch, mchc, mcv)

                    if hasattr(proba, 'tolist'):
                        proba = proba.tolist()

                    label = prediction_service.get_prediction_label(pred)
                    
                    # Save to database
                    try:
                        proba_str = json.dumps(proba)
                        pred_record = PredictionRecord(
                            user_id=current_user.id,
                            model_name=model,
                            gender=gender,
                            hemoglobin=hemoglobin,
                            mch=mch,
                            mchc=mchc,
                            mcv=mcv,
                            prediction_label=label,
                            probability_proba=proba_str
                        )
                        db.session.add(pred_record)
                        db.session.commit()
                    except Exception as e:
                        app.logger.exception('Error saving prediction')
                    
                    return render_template('prediction.html', active='prediction', results={'model':model,'label':label,'proba':proba}, results_all=False)
            except Exception as e:
                app.logger.exception('Prediction route failed')
                error_message = str(e)
                return render_template('prediction.html', active='prediction', error=error_message)

        return render_template('prediction.html', active='prediction')


    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Get predictions for current user from database
        predictions = PredictionRecord.query.filter_by(user_id=current_user.id).order_by(PredictionRecord.timestamp.desc()).all()
        
        history = []
        for pred in predictions:
            import json
            try:
                proba_dict = json.loads(pred.probability_proba) if pred.probability_proba else {}
                proba_str = ', '.join([f"{k}: {v:.2%}" for k, v in proba_dict.items()])
            except:
                proba_str = pred.probability_proba or 'N/A'
            
            history.append({
                'timestamp': pred.timestamp.strftime('%Y-%m-%d %H:%M:%S') if pred.timestamp else '',
                'model': pred.model_name,
                'gender': pred.gender,
                'hemoglobin': pred.hemoglobin,
                'mch': pred.mch,
                'mchc': pred.mchc,
                'mcv': pred.mcv,
                'prediction': pred.prediction_label,
                'probability': proba_str
            })

        return render_template('dashboard.html', active='dashboard', history=history)

    @app.route('/dashboard/download')
    @login_required
    def download_history():
        import io, csv, json, datetime

        # Query predictions for current user
        predictions = PredictionRecord.query.filter_by(user_id=current_user.id).order_by(PredictionRecord.timestamp.desc()).all()

        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(['timestamp','model','gender','hemoglobin','mch','mchc','mcv','prediction','probability'])

        for pred in predictions:
            try:
                proba_dict = json.loads(pred.probability_proba) if pred.probability_proba else {}
                # If proba_dict is mapping label->value, format percentages
                if isinstance(proba_dict, dict):
                    proba_str = '; '.join([f"{k}:{v:.4f}" if isinstance(v, float) else f"{k}:{v}" for k, v in proba_dict.items()])
                else:
                    proba_str = str(proba_dict)
            except Exception:
                proba_str = pred.probability_proba or ''

            ts = pred.timestamp.strftime('%Y-%m-%d %H:%M:%S') if pred.timestamp else ''
            cw.writerow([ts, pred.model_name, pred.gender, pred.hemoglobin, pred.mch, pred.mchc, pred.mcv, pred.prediction_label, proba_str])

        output = make_response(si.getvalue())
        fname = f"history_{current_user.username}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        output.headers['Content-Disposition'] = f'attachment; filename={fname}'
        output.headers['Content-Type'] = 'text/csv; charset=utf-8'
        return output


    @app.route('/about')
    @login_required
    def about():
        return render_template('about.html', active='about')


    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html', active='profile')


    @app.route('/profile/edit', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        import os
        from werkzeug.utils import secure_filename

        UPLOAD_FOLDER = os.path.join('static', 'uploads')
        ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif'}

        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            file = request.files.get('profile_image')

            if username:
                current_user.username = username
            if email:
                current_user.email = email

            if file and file.filename:
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[-1].lower()
                if ext in ALLOWED_EXT:
                    save_path = os.path.join(UPLOAD_FOLDER, f"user_{current_user.id}_{filename}")
                    file.save(save_path)
                    current_user.profile_image = save_path.replace('\\', '/')
                else:
                    flash('Tipe file tidak diizinkan.', 'danger')
                    return redirect(url_for('edit_profile'))

            try:
                db.session.commit()
                flash('Profil diperbarui.', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Gagal memperbarui profil.', 'danger')

            return redirect(url_for('profile'))

        return render_template('edit_profile.html', active='profile')


    if __name__ == '__main__':
        app.run(debug=True)