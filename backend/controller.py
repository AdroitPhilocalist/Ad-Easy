from flask import render_template, request, redirect, url_for
from flask import current_app as app
# backend/controller.py
from backend.models import db, User, Campaign, AdRequest, Influencer, Sponsor, CampaignRequest


@app.route('/')
def role_selection():
    return render_template('role_selection.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Redirect to respective dashboard based on role
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'sponsor':
            return redirect(url_for('sponsor_dashboard'))
        elif role == 'influencer':
            return redirect(url_for('influencer_dashboard'))
    
    if role == 'admin':
        return render_template('admin_login.html')
    elif role == 'sponsor':
        return render_template('sponsor_login.html')
    elif role == 'influencer':
        return render_template('influencer_login.html')
    return redirect(url_for('role_selection'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usr=User.query.filter_by(username=username,password=password).first()
        if usr and usr.id==0:
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html',msg="Invalid Credentials!!",credentials="false")
    return render_template('admin_login.html',msg="")
        
    

@app.route('/sponsor_login', methods=['GET', 'POST'])
def sponsor_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usr=User.query.filter_by(username=username,password=password).first()
        if usr and usr.role=='sponsor':
            return redirect(url_for('sponsor_dashboard'))
        else:
            return render_template('sponsor_login.html',msg="Invalid Credentials!!",credentials="false")
    return render_template('sponsor_login.html',msg="")
        
    

@app.route('/influencer_login', methods=['GET', 'POST'])
def influencer_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usr=User.query.filter_by(username=username,password=password).first()
        if usr and usr.role=='influencer':
            return redirect(url_for('influencer_dashboard'))
        else:
            return render_template('influencer_login.html',msg="Invalid Credentials!!",credentials="false")
    return render_template('influencer_login.html',msg="")

@app.route('/sponsor_registration', methods=['GET', 'POST'])
def sponsor_registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        company = request.form['company']
        industry = request.form['industry']
        usr=User.query.filter_by(username=username).first()
        
        if not usr:
            # Create new User
            new_user = User(
                username=username,
                password=password,
                email=email,
                role='sponsor'
            )
            db.session.add(new_user)
            db.session.commit()

            # Create new Sponsor
            new_sponsor = Sponsor(
                name=username,
                email=email,
                company=company,
                industry=industry,
                user_id=new_user.id
            )
            db.session.add(new_sponsor)
            db.session.commit()
            return render_template('sponsor_login.html')
        else:
            return render_template('sponsor_registration.html',msg="Sorry, User already exists!!")

    return render_template('sponsor_registration.html',msg="")

@app.route('/influencer_registration', methods=['GET', 'POST'])
def influencer_registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        full_name = request.form['full_name']
        niche = request.form['niche']
        reach = request.form['reach']
        social_media_platforms = request.form.getlist('social_media')
        
        # Combine the selected social media platforms into a comma-separated string
        platforms = ', '.join(social_media_platforms)
        usr=User.query.filter_by(username=username).first()
        if not usr:
        # Create new User
            new_user = User(
                username=username,
                password=password,
                email=email,
                role='influencer'
            )
            db.session.add(new_user)
            db.session.commit()

            # Create new Influencer
            new_influencer = Influencer(
                name=full_name, 
                email=email,
                niche=niche,
                reach=reach,
                platform=platforms,
                user_id=new_user.id
            )
            db.session.add(new_influencer)
            db.session.commit()
            return render_template('influencer_login.html')
        else:
            return render_template('influencer_registration.html',msg="Sorry, User already exists!!")

    return render_template('influencer_registration.html',msg="")

@app.route('/admin_dashboard')
def admin_dashboard():
    # Fetch relevant statistics from the database (placeholder comment)
    return render_template('admin_dashboard.html')

@app.route('/sponsor_dashboard')
def sponsor_dashboard():
    return render_template('sponsor_dashboard.html')

@app.route('/influencer_dashboard')
def influencer_dashboard():
    return render_template('influencer_dashboard.html')

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if request.method == 'POST':
        # Logic to update profile details
        return redirect(url_for('influencer_dashboard'))
    return render_template('update_profile.html')

@app.route('/logout')
def logout():
    # Here you can implement any session clearing or logout logic if necessary
    return redirect(url_for('role_selection'))