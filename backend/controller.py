from flask import render_template, request, redirect, url_for
from flask import current_app as app
import os
from flask import jsonify
from io import BytesIO
from PIL import Image
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
        
        # Authenticate user
        usr = User.query.filter_by(username=username, password=password).first()
        
        if usr and usr.role == 'sponsor':
            # Fetch the sponsor details using the user's ID
            sponsor = Sponsor.query.filter_by(user_id=usr.id).first()
            
            if sponsor:
                sponsor_campaigns=fetch_campaigns(usr.id).campaigns
                # Redirect to the dashboard with query parameters
                return render_template("sponsor_dashboard.html",
                                        username=usr.username,
                                        name=sponsor.name,
                                        email=sponsor.email,
                                        company=sponsor.company,
                                        industry=sponsor.industry,
                                        campaigns=sponsor_campaigns)
            else:
                # Handle case where sponsor details are not found
                return render_template('sponsor_login.html', msg="Sponsor details not found.", credentials="false")
        else:
            return render_template('sponsor_login.html', msg="Invalid Credentials!!", credentials="false")
    
    return render_template('sponsor_login.html', msg="")


def fetch_campaigns(id):
            user_campaigns=User.query.filter_by(id=id).first()
            return user_campaigns
    

@app.route('/influencer_login', methods=['GET', 'POST'])
def influencer_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Authenticate user
        usr = User.query.filter_by(username=username, password=password).first()
        
        if usr and usr.role == 'influencer':
            # Fetch the influencer details using the user's ID
            influencer = Influencer.query.filter_by(user_id=usr.id).first()
            
            if influencer:
                # Redirect to the dashboard with query parameters
                return redirect(url_for('influencer_dashboard',
                                        username=usr.username,
                                        profile_image=influencer.profile_picture if influencer.profile_picture else 'default_profile_image_url',
                                        name=influencer.name,
                                        niche=influencer.niche,
                                        social_media_platforms=influencer.platform,
                                        reach=influencer.reach))
            else:
                # Handle case where influencer details are not found
                return render_template('influencer_login.html', msg="Influencer details not found.", credentials="false")
        else:
            return render_template('influencer_login.html', msg="Invalid Credentials!!", credentials="false")
    
    return render_template('influencer_login.html', msg="")

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

@app.route('/admin/dashboard')
def admin_dashboard():
    total_users = User.query.count()-1
    total_influencers = Influencer.query.count()
    total_sponsors = Sponsor.query.count()
    total_campaigns = Campaign.query.count()
    
    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_influencers=total_influencers,
        total_sponsors=total_sponsors,
        total_campaigns=total_campaigns
    )

@app.route('/admin/stats')
def stats():
    
    total_users = User.query.count()
    total_influencers = Influencer.query.count()
    total_sponsors = Sponsor.query.count()
    total_campaigns = Campaign.query.count()

    stats_data = [total_users, total_influencers, total_sponsors, total_campaigns]

    return render_template('stats.html', stats_data=stats_data)



@app.route('/sponsor_dashboard', methods=['GET', 'POST'])
@app.route('/sponsor_dashboard/<username>', methods=['GET', 'POST'])
def sponsor_dashboard(username=None):
    if request.method == 'POST':
        username = request.form.get('username')
        company = request.form.get('company')
        industry = request.form.get('industry')

        user = User.query.filter_by(username=username).first()
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()

        if sponsor:
            sponsor.name = username
            sponsor.company = company
            sponsor.industry = industry
            
            db.session.commit()

        return redirect(url_for('sponsor_dashboard', 
                                username=username, 
                                company=company, 
                                industry=industry))

    # Retrieve query parameters
    username = username or request.args.get('username')
    company = request.args.get('company')
    industry = request.args.get('industry')
    usr = User.query.filter_by(username=username).first()
    if usr and usr.role == 'sponsor':
            # Fetch the sponsor details using the user's ID
            sponsor = Sponsor.query.filter_by(user_id=usr.id).first()
            
            if sponsor:
                sponsor_campaigns=fetch_campaigns(usr.id).campaigns
                # Redirect to the dashboard with query parameters
                return render_template("sponsor_dashboard.html",
                                        username=usr.username,
                                        name=sponsor.name,
                                        email=sponsor.email,
                                        company=sponsor.company,
                                        industry=sponsor.industry,
                                        campaigns=sponsor_campaigns)
            

@app.route('/sponsor_ad_requests/<string:username>')
def sponsor_ad_requests(username):
    # Fetch the sponsor user
    user = User.query.filter_by(username=username).first()
    if user is None:
        return "User not found", 404
    
    sponsor = Sponsor.query.filter_by(user_id=user.id).first()
    if sponsor is None:
        return "Sponsor not found", 404
    
    # Fetch all ad requests associated with the sponsor
    ad_requests = AdRequest.query.join(Campaign).filter(
        Campaign.user_id == sponsor.user_id
    ).all()

    return render_template('sponsor_ad_requests.html', username=username, ad_requests=ad_requests)




@app.route('/sponsor_influencers/<username>', methods=['GET'])
def sponsor_influencers(username):
    usr = User.query.filter_by(username=username).first()
    if usr and usr.role == 'sponsor':
        # Fetch all influencers
        influencers = Influencer.query.all()
        
        # Additional code to handle filters if needed
        filter_params = {
            'niche': request.args.get('niche'),
            'reach': request.args.get('reach')
            # Add more filters as needed
        }
        
        # Filter influencers based on query parameters
        if filter_params['niche']:
            influencers = [i for i in influencers if i.niche == filter_params['niche']]
        if filter_params['reach']:
            influencers = [i for i in influencers if i.reach >= int(filter_params['reach'])]
        
        return render_template('sponsor_influencers.html',
                               username=usr.username,
                               influencers=influencers)
    return redirect(url_for('login'))  # Redirect to login if not authorized

@app.route('/submit_ad_request/<username>', methods=['POST'])
def submit_ad_request(username):
    user = User.query.filter_by(username=username).first()
    if not user or user.role != 'sponsor':
        
        return redirect(url_for('sponsor_dashboard', username=username))

    campaign_id = request.form.get('campaign_id')
    influencer_id = request.form.get('influencer_id')
    messages = request.form.get('messages')
    requirements = request.form.get('requirements')
    payment_amount = float(request.form['payment_amount'])
    status = 'Pending'

    campaign = Campaign.query.get(campaign_id)
    influencer = Influencer.query.get(influencer_id)

    

    ad_request = AdRequest(
        campaign_id=campaign_id,
        influencer_id=influencer_id,
        messages=messages,
        requirements=requirements,
        payment_amount=payment_amount,
        status=status
    )

    db.session.add(ad_request)
    db.session.commit()
    return redirect(url_for('sponsor_dashboard', username=username))
@app.route('/get_campaigns_for_influencer/<int:influencer_id>')
def get_campaigns_for_influencer(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        return jsonify({'error': 'Influencer not found'}), 404

    campaigns = Campaign.query.all()
    campaign_list = [{
        'id': campaign.id,
        'name': campaign.name,
        'description': campaign.description,
        'start_date': campaign.start_date.strftime('%Y-%m-%d'),
        'end_date': campaign.end_date.strftime('%Y-%m-%d')
    } for campaign in campaigns]

    return jsonify({'campaigns': campaign_list})

    

@app.route('/sponsor_campaigns/<username>', methods=['GET'])
def campaigns_page(username):
    user = User.query.filter_by(username=username).first()
    if user and user.role == 'sponsor':
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        if sponsor:
            sponsor_campaigns=fetch_campaigns(user.id).campaigns
            return render_template('sponsor_campaigns.html', campaigns=sponsor_campaigns, username=username)
    return redirect(url_for('sponsor_dashboard', username=username))


from datetime import datetime

@app.route('/create_campaign/<string:username>', methods=['POST'])
def create_campaign(username):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        budget = float(request.form['budget'])
        visibility = request.form['visibility']
        niche = request.form['niche']
        goals = request.form['goals']
        sponsor = Sponsor.query.join(User).filter(User.username == username).first()
        user_id = sponsor.user_id
        # Convert date strings to date objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Create a new campaign instance
        new_campaign = Campaign(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            visibility=visibility,
            niche=niche,
            goals=goals,
            status='Active',
            flagged=False,
            user_id=user_id
        )

        # Add to the session and commit
        db.session.add(new_campaign)
        db.session.commit()

        return redirect(f'/sponsor_campaigns/{username}')

    return render_template('create_campaign.html')


@app.route('/edit_campaign/<username>', methods=['POST'])
def edit_campaign(username):
    if request.method == 'POST':
        campaign_id = request.form['campaign_id']
        campaign = Campaign.query.get(campaign_id)
        if campaign:
            start_date_str = request.form['start_date']
            end_date_str = request.form['end_date']
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            # Update campaign details
            campaign.name = request.form['name']
            campaign.description = request.form['description']
            campaign.start_date = start_date
            campaign.end_date = end_date
            campaign.budget = request.form['budget']
            campaign.visibility = request.form['visibility']
            campaign.niche = request.form['niche']
            
            db.session.commit()
        return redirect(f'/sponsor_campaigns/{username}')

@app.route('/delete_campaign/<username>', methods=['POST'])
def delete_campaign(username):
    if request.method == 'POST':
        campaign_id = request.form['campaign_id']
        campaign = Campaign.query.get(campaign_id)
        if campaign:
            db.session.delete(campaign)
            db.session.commit()
        return redirect(f'/sponsor_campaigns/{username}')
    



@app.route('/influencer_dashboard', methods=['GET', 'POST'])
@app.route('/influencer_dashboard/<username>', methods=['GET', 'POST'])
def influencer_dashboard(username=None):
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        name = request.form['name']
        niche = request.form['niche']
        social_media_platforms = request.form.getlist('platforms')
        reach = request.form['reach']

        # Handle image upload
        upload_folder = 'static/uploads'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        profile_image = request.files.get('profile_image')
        if profile_image:
            image_path = os.path.join(upload_folder, profile_image.filename)
            profile_image.save(image_path)
        else:
            image_path = request.form.get('current_profile_image')

        user = User.query.filter_by(username=username).first()
        influencer = Influencer.query.filter_by(user_id=user.id).first()
        ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id).all()
        if influencer:
            influencer.name = name
            influencer.niche = niche
            influencer.social_media_platforms = ','.join(social_media_platforms)
            influencer.reach = reach
            influencer.profile_picture = image_path

            db.session.commit()

        return redirect(url_for('influencer_dashboard', 
                                username=username, 
                                profile_image=image_path, 
                                name=name, 
                                niche=niche, 
                                social_media_platforms=','.join(social_media_platforms), 
                                reach=reach,
                                ad_requests=ad_requests))

    # Handle GET request
    username = username or request.args.get('username')
    if not username:
        return redirect(url_for('login'))  # Redirect to login if username is not provided

    user = User.query.filter_by(username=username).first()
    influencer = Influencer.query.filter_by(user_id=user.id).first()
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id).all()
    if not user or user.role != 'influencer':
        return redirect(url_for('login'))  # Redirect to login if user is not an influencer

    influencer = Influencer.query.filter_by(user_id=user.id).first()
    if not influencer:
        return redirect(url_for('login'))  # Redirect to login if influencer details are not found

    return render_template('influencer_dashboard.html',
                           username=user.username,
                           profile_image=influencer.profile_picture,
                           name=influencer.name,
                           niche=influencer.niche,
                           social_media_platforms=influencer.platform,
                           reach=influencer.reach,
                           ad_requests=ad_requests)

@app.route('/influencer_campaigns/<username>', methods=['GET'])
def influencer_campaigns(username):
    # Fetch the current influencer based on the username
    user = User.query.filter_by(username=username).first()
    current_influencer = Influencer.query.filter_by(user_id=user.id).first()

    # Get query parameters for filtering
    name_filter = request.args.get('name', '')
    niche_filter = request.args.get('niche', '')

    # Fetch all campaigns
    campaigns = Campaign.query.all()

    # Filter campaigns based on the influencer's niche and query parameters
    filtered_campaigns = []
    for campaign in campaigns:
        if campaign.visibility == 'public':
            filtered_campaigns.append(campaign)
        elif campaign.visibility == 'private' and campaign.niche == current_influencer.niche:
            filtered_campaigns.append(campaign)
    # Apply additional filters based on name and niche
    if name_filter:
        filtered_campaigns = [c for c in filtered_campaigns if name_filter.lower() in c.name.lower()]
    if niche_filter:
        filtered_campaigns = [c for c in filtered_campaigns if c.niche == niche_filter]
    

    return render_template('influencer_campaigns.html',
                           username=username,
                           campaigns=filtered_campaigns)
@app.route('/accept_ad_request/<int:ad_request_id>/<string:username>', methods=['POST'])
def accept_ad_request(ad_request_id,username):
    ad_request = AdRequest.query.get(ad_request_id)
    if ad_request:
        ad_request.status = "Accepted and Active"
        db.session.commit()
        return redirect(url_for('influencer_dashboard', username=username))
    return "Ad Request not found", 404

@app.route('/reject_ad_request/<int:ad_request_id>/<string:username>', methods=['POST'])
def reject_ad_request(ad_request_id,username):
    ad_request = AdRequest.query.get(ad_request_id)
    if ad_request:
        db.session.delete(ad_request)
        db.session.commit()
        return redirect(url_for('influencer_dashboard', username=username))
    return "Ad Request not found", 404

@app.route('/active_campaigns/<string:username>')
def active_campaigns(username):
    # Fetch the user and influencer based on username
    user = User.query.filter_by(username=username).first()
    if user is None:
        return "User not found", 404
    
    current_influencer = Influencer.query.filter_by(user_id=user.id).first()
    if current_influencer is None:
        return "Influencer not found", 404
    
    influencer_id = current_influencer.id

    # Query to get active campaigns for the influencer
    active_campaigns = db.session.query(Campaign).join(AdRequest).filter(
        AdRequest.influencer_id == influencer_id,
        AdRequest.status == "Accepted and Active"
    ).all()
    
    # Fetch the company names of the sponsors
    campaigns_with_sponsors = []
    for campaign in active_campaigns:
        # Get the sponsor's user object
        sponsor_user = User.query.filter_by(id=campaign.user_id).first()
        sponsor_company = 'Unknown'  # Default if no sponsor is found
        if sponsor_user:
            sponsor_sponsor = Sponsor.query.filter_by(user_id=sponsor_user.id).first()
            if sponsor_sponsor:
                sponsor_company = sponsor_sponsor.company
        
        # Append campaign info with sponsor company
        campaigns_with_sponsors.append({
            'campaign': campaign,
            'sponsor_company': sponsor_company
        })

    return render_template('active_campaigns.html', username=username, campaigns=campaigns_with_sponsors)







@app.route('/logout')
def logout():
    # Here you can implement any session clearing or logout logic if necessary
    return redirect(url_for('role_selection'))