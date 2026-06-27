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

import config
from utils import prediction as prediction_service

if Flask_available:
    app = Flask(__name__)
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = config.SECRET_KEY
    
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
        patient_name = db.Column(db.String(100), nullable=True, default='Pasien Noname')
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
    def get_default_user():
        try:
            # Auto update schema if patient_name column is missing in prediction_record table
            try:
                from sqlalchemy import inspect, text
                inspector = inspect(db.engine)
                if 'prediction_record' in inspector.get_table_names():
                    columns = [c['name'] for c in inspector.get_columns('prediction_record')]
                    if 'patient_name' not in columns:
                        with db.engine.connect() as conn:
                            conn.execute(text("ALTER TABLE prediction_record ADD COLUMN patient_name VARCHAR(100) DEFAULT 'Pasien Noname'"))
                            conn.commit()
            except Exception:
                pass

            user = User.query.first()
            if not user:
                user = User(username='Pengguna', email='user@anemify.local')
                user.set_password('default_password')
                db.session.add(user)
                db.session.commit()
            return user
        except Exception:
            return None

    @app.route('/login')
    @app.route('/register')
    def redirect_to_home():
        return redirect(url_for('home'))
    
    
    @app.route('/')
    def home():
        return render_template('home.html', active='home')


    @app.route('/prediction', methods=['GET', 'POST'])
    def prediction():
        default_user = get_default_user()
        user_id = default_user.id if default_user else 1

        if request.method == 'POST':
            import json
            import traceback
            from datetime import datetime
            
            try:
                patient_name = request.form.get('patient_name', '').strip() or 'Pasien Noname'
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
                                user_id=user_id,
                                patient_name=patient_name,
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
                    return render_template('prediction.html', active='prediction', results=results, results_all=True, patient_name=patient_name)
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
                            user_id=user_id,
                            patient_name=patient_name,
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
                    
                    return render_template('prediction.html', active='prediction', results={'model':model,'label':label,'proba':proba}, results_all=False, patient_name=patient_name)
            except Exception as e:
                app.logger.exception('Prediction route failed')
                error_message = str(e)
                return render_template('prediction.html', active='prediction', error=error_message)

        return render_template('prediction.html', active='prediction')


    @app.route('/dashboard')
    def dashboard():
        default_user = get_default_user()
        user_id = default_user.id if default_user else 1

        # Query predictions for all users or default user from database
        predictions = PredictionRecord.query.order_by(PredictionRecord.timestamp.desc()).all()
        
        history = []
        for pred in predictions:
            import json
            try:
                proba_dict = json.loads(pred.probability_proba) if pred.probability_proba else {}
                if isinstance(proba_dict, list):
                    proba_str = f"Berisiko: {proba_dict[1]:.1%}, Normal: {proba_dict[0]:.1%}"
                elif isinstance(proba_dict, dict):
                    proba_str = ', '.join([f"{k}: {v:.2%}" for k, v in proba_dict.items()])
                else:
                    proba_str = str(proba_dict)
            except:
                proba_str = pred.probability_proba or 'N/A'
            
            history.append({
                'timestamp': pred.timestamp.strftime('%Y-%m-%d %H:%M:%S') if pred.timestamp else '',
                'patient_name': getattr(pred, 'patient_name', None) or 'Pasien Noname',
                'model': pred.model_name,
                'gender': 'Laki-laki' if pred.gender == 1 else 'Perempuan',
                'hemoglobin': pred.hemoglobin,
                'mch': pred.mch,
                'mchc': pred.mchc,
                'mcv': pred.mcv,
                'prediction': pred.prediction_label,
                'probability': proba_str
            })

        return render_template('dashboard.html', active='dashboard', history=history)

    @app.route('/dashboard/download')
    def download_history():
        import io, csv, json, datetime

        predictions = PredictionRecord.query.order_by(PredictionRecord.timestamp.desc()).all()

        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(['timestamp','patient_name','model','gender','hemoglobin','mch','mchc','mcv','prediction','probability'])

        for pred in predictions:
            try:
                proba_dict = json.loads(pred.probability_proba) if pred.probability_proba else {}
                if isinstance(proba_dict, dict):
                    proba_str = '; '.join([f"{k}:{v:.4f}" if isinstance(v, float) else f"{k}:{v}" for k, v in proba_dict.items()])
                else:
                    proba_str = str(proba_dict)
            except Exception:
                proba_str = pred.probability_proba or ''

            ts = pred.timestamp.strftime('%Y-%m-%d %H:%M:%S') if pred.timestamp else ''
            pname = getattr(pred, 'patient_name', None) or 'Pasien Noname'
            cw.writerow([ts, pname, pred.model_name, 'Laki-laki' if pred.gender == 1 else 'Perempuan', pred.hemoglobin, pred.mch, pred.mchc, pred.mcv, pred.prediction_label, proba_str])

        output = make_response(si.getvalue())
        fname = f"anemify_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        output.headers['Content-Disposition'] = f'attachment; filename={fname}'
        output.headers['Content-Type'] = 'text/csv; charset=utf-8'
        return output


    @app.route('/about')
    def about():
        return render_template('about.html', active='about')


    if __name__ == '__main__':
        app.run(debug=True)