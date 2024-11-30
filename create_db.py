
from app import create_app, db
from app.models import AdminUser

app = create_app()

with app.app_context():
    db.create_all()
    # Check if admin user already exists
    if not AdminUser.query.filter_by(username='admin').first():
        admin = AdminUser(username='harshMishra')
        admin.set_password('Harsh@HMC')
        db.session.add(admin)
        db.session.commit()
        print('Database initialized and admin user created.')
    else:
        print('Admin user already exists.')
