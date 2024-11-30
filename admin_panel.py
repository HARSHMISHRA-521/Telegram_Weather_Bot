
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from app import create_app, db, login_manager
from app.models import User, AdminUser
from app.forms import LoginForm, UpdateSettingsForm

app = create_app()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = AdminUser.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Update settings route
@app.route('/update_settings', methods=['GET', 'POST'])
@login_required
def update_settings():
    form = UpdateSettingsForm()
    if form.validate_on_submit():
        # Update settings logic here
        # For simplicity, we'll just flash a message
        # To persist settings, consider storing them in the database or updating the .env file
        flash('Settings updated successfully.')
        return redirect(url_for('dashboard'))
    return render_template('update_settings.html', form=form)

# Manage users route
@app.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users)

# Block user route
@app.route('/block_user/<int:user_id>')
@login_required
def block_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.subscribed = False
        db.session.commit()
        flash(f'User {user_id} has been blocked.')
    return redirect(url_for('manage_users'))

# Delete user route
@app.route('/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user_id} has been deleted.')
    return redirect(url_for('manage_users'))

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
