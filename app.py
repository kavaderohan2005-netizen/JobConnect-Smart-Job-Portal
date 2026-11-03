import os
from datetime import datetime, date
from flask import Flask, render_template
from flask_login import LoginManager, current_user
from config import Config
from database import db, init_database
from models import User, Notification

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize Database with MySQL & auto-fallback support
    init_database(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.seeker import seeker_bp
    from routes.employer import employer_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(seeker_bp)
    app.register_blueprint(employer_bp)
    app.register_blueprint(admin_bp)

    # Global Template Context
    @app.context_processor
    def inject_global_data():
        unread_notifications_count = 0
        recent_notifications = []
        if current_user.is_authenticated:
            unread_notifications_count = Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
            recent_notifications = Notification.query.filter_by(
                user_id=current_user.id
            ).order_by(Notification.created_at.desc()).limit(5).all()

        return {
            'now': datetime.utcnow(),
            'current_year': datetime.utcnow().year,
            'active_db': app.config.get('ACTIVE_DB_NAME', 'MySQL / SQLite'),
            'unread_notifications_count': unread_notifications_count,
            'recent_notifications': recent_notifications
        }

    # Custom Jinja Filters
    @app.template_filter('format_date')
    def format_date_filter(val, format='%b %d, %Y'):
        if not val:
            return ''
        if isinstance(val, (datetime, date)):
            return val.strftime(format)
        return str(val)

    @app.template_filter('time_ago')
    def time_ago_filter(val):
        if not val:
            return ''
        now = datetime.utcnow()
        if isinstance(val, date) and not isinstance(val, datetime):
            val = datetime.combine(val, datetime.min.time())
        diff = now - val
        seconds = diff.total_seconds()
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes}m ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours}h ago"
        elif seconds < 604800:
            days = int(seconds // 86400)
            return f"{days}d ago"
        elif seconds < 2592000:
            weeks = int(seconds // 604800)
            return f"{weeks}w ago"
        else:
            return val.strftime('%b %d, %Y')

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def access_forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        # Seed realistic data if clean DB
        from seed_data import seed_database
        seed_database()

    print("=" * 60)
    print("[STARTUP] JobConnect Smart Job Portal is starting up!")
    print("[INFO] Open in browser: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
