from flask import render_template, request, redirect, url_for
from flask import current_app as app

import os
from flask import jsonify
from sqlalchemy import or_,and_

from PIL import Image
from backend.models import db, User, Campaign, AdRequest, Influencer, Sponsor, CampaignRequest
from datetime import datetime



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
                campaign_requests = CampaignRequest.query.filter_by(sponsor_id=sponsor.id, status='Pending').all()

                # Redirect to the dashboard with query parameters
                return render_template("sponsor_dashboard.html",
                                        username=usr.username,
                                        name=sponsor.name,
                                        email=sponsor.email,
                                        company=sponsor.company,
                                        industry=sponsor.industry,
                                        campaigns=sponsor_campaigns,
                                        campaign_requests=campaign_requests)
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

@app.route('/admin/info')
def info():
    ad_requests = AdRequest.query.all()
    campaign_requests = CampaignRequest.query.all()
    return render_template('info.html', ad_requests=ad_requests, campaign_requests=campaign_requests)

@app.route('/admin/stats')
def stats():
    # General counts
    total_users = User.query.count()
    total_influencers = Influencer.query.count()
    total_sponsors = Sponsor.query.count()
    total_campaigns = Campaign.query.count()

    # Campaign Requests Status
    completed_campaign_requests = CampaignRequest.query.filter_by(status='Completed').count()
    pending_campaign_requests = CampaignRequest.query.filter_by(status='Pending').count()
    campaign_requests_status_data = [completed_campaign_requests, pending_campaign_requests]

    # Ad Requests Status
    completed_ad_requests = AdRequest.query.filter_by(status='Completed').count()
    pending_ad_requests = AdRequest.query.filter_by(status='Pending').count()
    ad_requests_status_data = [completed_ad_requests, pending_ad_requests]

    # Campaign Visibility
    public_campaigns = Campaign.query.filter_by(visibility='public').count()
    private_campaigns = Campaign.query.filter_by(visibility='private').count()
    campaign_visibility_data = [public_campaigns, private_campaigns]

    # Users by Role
    admins = User.query.filter_by(role='admin').count()
    influencers = User.query.filter_by(role='influencer').count()
    sponsors = User.query.filter_by(role='sponsor').count()
    users_by_role_data = [admins, influencers, sponsors]

    # Aggregate data for bar chart on general stats
    stats_data = [total_users, total_influencers, total_sponsors, total_campaigns]

    return render_template('stats.html', 
                           stats_data=stats_data,
                           campaign_requests_status_data=campaign_requests_status_data,
                           ad_requests_status_data=ad_requests_status_data,
                           campaign_visibility_data=campaign_visibility_data,
                           users_by_role_data=users_by_role_data)

@app.route('/find_all')
def find_all():
    influencers = Influencer.query.all()
    sponsors = Sponsor.query.all()
    campaigns = Campaign.query.all()
    return render_template('find_all.html', influencers=influencers, sponsors=sponsors, campaigns=campaigns)

@app.route('/delete_record/<string:record_type>/<int:record_id>', methods=['POST'])
def delete_record(record_type, record_id):
    try:
        if record_type == 'influencer':
            # Fetch the influencer and associated user
            record = Influencer.query.get_or_404(record_id)
            user = User.query.get(record.user_id)
            
            # Delete the influencer
            db.session.delete(record)
            
            # Delete the associated user if necessary
            if user:
                db.session.delete(user)
            
        elif record_type == 'sponsor':
            # Fetch the sponsor and associated user
            record = Sponsor.query.get_or_404(record_id)
            user = User.query.get(record.user_id)
            
            # Delete the sponsor
            db.session.delete(record)
            
            # Delete the associated user if necessary
            if user:
                db.session.delete(user)
            
        elif record_type == 'campaign':
            # Fetch the campaign and associated ad requests
            record = Campaign.query.get_or_404(record_id)
            ad_requests = AdRequest.query.filter_by(campaign_id=record_id).all()
            
            # Delete all related ad requests
            for ad_request in ad_requests:
                db.session.delete(ad_request)
            
            # Delete the campaign
            db.session.delete(record)
            
        else:
            return "Invalid record type", 400

        db.session.commit()
        return redirect(url_for('find_all'))
    
    except Exception as e:
        db.session.rollback()
        return str(e), 500

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
            # Fetch sponsor's campaigns and campaign requests
            sponsor_campaigns = Campaign.query.filter_by(user_id=usr.id).all()
            campaign_requests = CampaignRequest.query.filter_by(sponsor_id=sponsor.id, status='Pending').all()

            return render_template("sponsor_dashboard.html",
                                    username=usr.username,
                                    name=sponsor.name,
                                    email=sponsor.email,
                                    company=sponsor.company,
                                    industry=sponsor.industry,
                                    campaigns=sponsor_campaigns,
                                    campaign_requests=campaign_requests)

@app.route('/sponsor_campaign_requests/<username>', methods=['GET'])
def sponsor_campaign_requests(username):
    usr = User.query.filter_by(username=username).first()
    
    if usr and usr.role == 'sponsor':
        sponsor = Sponsor.query.filter_by(user_id=usr.id).first()
        
        if sponsor:
            # Fetch campaign requests for the sponsor
            campaign_requests = CampaignRequest.query.filter_by(sponsor_id=sponsor.id).all()
            
            return render_template("sponsor_campaign_requests.html",
                                    username=usr.username,
                                    name=sponsor.name,
                                    email=sponsor.email,
                                    company=sponsor.company,
                                    industry=sponsor.industry,
                                    campaign_requests=campaign_requests)
    
    # Handle cases where user is not found or does not have the correct role
    return redirect(url_for('index'))

@app.route('/handle_campaign_request/<int:request_id>/<action>', methods=['POST'])
def handle_campaign_request(request_id, action):
    campaign_request = CampaignRequest.query.get(request_id)
    
    if campaign_request:
        if action == 'accept':
            # Update the request status
            campaign_request.status = "Accepted and Active"
        elif action == 'reject':
            # Delete the request from the database
            db.session.delete(campaign_request)
        
        db.session.commit()

        # Redirect to sponsor dashboard
        sponsor = Sponsor.query.get(campaign_request.sponsor_id)
        if sponsor:
            return redirect(url_for('sponsor_dashboard', username=sponsor.user.username))
    
    # Handle cases where the request or sponsor is not found
    return redirect(url_for('index'))

@app.route('/edit_ad_request/<int:request_id>', methods=['POST'])
def edit_ad_request(request_id):
    ad_request = AdRequest.query.get(request_id)
    
    if ad_request:
        ad_request.campaign_name = request.form['campaign_name']
        ad_request.messages = request.form['messages']
        ad_request.requirements = request.form['requirements']
        ad_request.payment_amount = request.form['payment_amount']
        ad_request.status = request.form['status']
        ad_request.complete = request.form['complete'] == 'True'
        ad_request.payment = request.form['payment'] == 'True'
        
        db.session.commit()

    return redirect(url_for('sponsor_ad_requests', username=ad_request.sponsor.user.username))

@app.route('/delete_ad_request/<int:request_id>', methods=['POST'])
def delete_ad_request(request_id):
    # Fetch the ad request
    ad_request = AdRequest.query.get(request_id)
    if ad_request is None:
        return "Ad Request not found", 404

    # Delete the ad request
    db.session.delete(ad_request)
    db.session.commit()

    # Find the associated sponsor through the campaign
    campaign = Campaign.query.get(ad_request.campaign_id)
    if campaign is None:
        return "Campaign not found", 404

    sponsor = Sponsor.query.filter_by(user_id=campaign.user_id).first()
    if sponsor is None:
        return "Sponsor not found", 404

    # Redirect to the sponsor ad requests page
    return redirect(url_for('sponsor_ad_requests', username=sponsor.user.username))

@app.route('/sponsor_ad_requests/<string:username>')
def sponsor_ad_requests(username):
    # Fetch the sponsor user
    user = User.query.filter_by(username=username).first()
    if user is None:
        return "User not found", 404
    
    sponsor = Sponsor.query.filter_by(user_id=user.id).first()
    if sponsor is None:
        return "Sponsor not found", 404
    
    # Fetch all ad requests associated with the sponsor's campaigns and include influencer details
    ad_requests = AdRequest.query.join(Campaign).join(User, AdRequest.influencer_id == User.id).filter(
        Campaign.user_id == sponsor.user_id
    ).all()

    return render_template('sponsor_ad_requests.html', username=username, ad_requests=ad_requests)

@app.route('/make_payment/<int:request_id>', methods=['POST'])
def make_payment(request_id):
    # Retrieve the ad request
    ad_request = AdRequest.query.get_or_404(request_id)
    
    # Update the payment status
    ad_request.payment = True
    
    # Commit the changes to the database
    db.session.commit()
    
    # Retrieve the username from the form or session
    username = request.form.get('username')
    
    if username is None:
        # Handle the case where 'username' is not provided
        return redirect(url_for('sponsor_dashboard'))  # Or another appropriate redirect

    return redirect(url_for('sponsor_ad_requests', username=username))

@app.route('/confirm_payment/<int:request_id>', methods=['POST'])
def confirm_payment(request_id):
    campaign_request = CampaignRequest.query.get_or_404(request_id)
    
    campaign_request.payment= True
    db.session.commit()
    username = request.form.get('username')
    
    return redirect(url_for('sponsor_campaign_requests', username=username))

@app.route('/active_campaigns_sponsor/<string:username>')
def active_campaigns_sponsor(username):
    # Fetch the user and sponsor based on username
    user = User.query.filter_by(username=username).first()
    if user is None:
        return "User not found", 404
    
    current_sponsor = Sponsor.query.filter_by(user_id=user.id).first()
    if current_sponsor is None:
        return "Sponsor not found", 404
    
    sponsor_id = current_sponsor.id

    # Query to get active campaigns for the sponsor
    active_campaigns = db.session.query(Campaign).join(AdRequest, isouter=True).join(CampaignRequest, isouter=True).filter(
        or_(
            and_(
                AdRequest.sponsor_id == sponsor_id,
                AdRequest.status == "Accepted and Active",
                AdRequest.campaign_id == Campaign.id
            ),
            and_(
                CampaignRequest.sponsor_id == sponsor_id,
                CampaignRequest.status == "Accepted and Active",
                CampaignRequest.campaign_id == Campaign.id
            )
        )
    ).distinct().all()

    return render_template('sponsor_active_campaigns.html', username=username, campaigns=active_campaigns)



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
    sponsor = Sponsor.query.filter_by(user_id=user.id).first()
    campaign_id = request.form.get('campaign_id')
    influencer_id = request.form.get('influencer_id')
    sponsor_id = sponsor.id
    messages = request.form.get('messages')
    requirements = request.form.get('requirements')
    payment_amount = float(request.form['payment_amount'])
    status = 'Pending'

    campaign = Campaign.query.get(campaign_id)
    influencer = Influencer.query.get(influencer_id)
    sponsor = Sponsor.query.get(sponsor_id) 
    

    ad_request = AdRequest(
        campaign_id=campaign_id,
        influencer_id=influencer_id,
        sponsor_id=sponsor_id,
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
        ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id, status='Pending').all()
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
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id, status='Pending').all()
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
    
    influencer_id = current_influencer.user_id

    # Query to get active campaigns for the influencer
    active_campaigns = db.session.query(Campaign).join(AdRequest, isouter=True).join(CampaignRequest, isouter=True).filter(
        or_(
            and_(
                AdRequest.influencer_id == current_influencer.id,
                AdRequest.status == "Accepted and Active"
            ),
            and_(
                CampaignRequest.influencer_id == influencer_id,
                CampaignRequest.status == "Accepted and Active"
            )
        ),
        or_(
            and_(
                AdRequest.campaign_id == Campaign.id,
                AdRequest.status == "Accepted and Active"
            ),
            and_(
                CampaignRequest.campaign_id == Campaign.id,
                CampaignRequest.status == "Accepted and Active"
            )
        )
    ).distinct().all()
    
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


@app.route('/submit_campaign_request/<string:username>', methods=['POST'])
def submit_campaign_request(username):
    # Fetch the influencer user
    user = User.query.filter_by(username=username).first()
    if user is None:
        return "User not found", 404

    # Get form data
    campaign_id = request.form.get('campaign_id')
    messages = request.form.get('messages')
    payment_amount = request.form.get('payment_amount')
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    if campaign is None:
        return "Campaign not found", 404

    # Get the user_id associated with the campaign
    sponsor_user = User.query.filter_by(id=campaign.user_id).first()
    if sponsor_user is None:
        return "Sponsor user not found", 404

    # Fetch the sponsor using the user_id
    sponsor = Sponsor.query.filter_by(user_id=sponsor_user.id).first()
    if sponsor is None:
        return "Sponsor not found", 404

    # Create new CampaignRequest entry
    campaign_request = CampaignRequest(
        campaign_id=campaign_id,
        influencer_id=user.id,
        sponsor_id=sponsor.id,
        messages=messages,
        payment_amount=payment_amount,
        status='Pending'
    )

    # Add to the database
    db.session.add(campaign_request)
    db.session.commit()

    return redirect(url_for('influencer_campaigns', username=username))

@app.route('/influencer_ad_requests/<string:username>')
def ad_requests(username):
    # Fetch the influencer user
    user = User.query.filter_by(username=username).first()
    if user is None:
        return "User not found", 404
    
    influencer = Influencer.query.filter_by(user_id=user.id).first()
    if influencer is None:
        return "Influencer not found", 404
    
    # Fetch all ad requests associated with the influencer
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id).all()

    return render_template('influencer_ad_requests.html', username=username, ad_requests=ad_requests)

@app.route('/influencer_campaign_requests/<username>', methods=['GET'])
def campaign_requests(username):
    # Fetch the user
    user = User.query.filter_by(username=username).first()
    if user is None:
        return "User not found", 404
    
    # Check if user is an influencer
    if user.role != 'influencer':
        return "Not an influencer", 403
    
    # Fetch the influencer
    influencer = Influencer.query.filter_by(user_id=user.id).first()
    if influencer is None:
        return "Influencer not found", 404

    # Fetch all campaign requests for the influencer
    campaign_requests = CampaignRequest.query.filter_by(influencer_id=influencer.user_id).all()
    
    return render_template('influencer_campaign_requests.html', username=username, campaign_requests=campaign_requests)

@app.route('/mark_campaign_completed/<int:campaign_id>', methods=['POST'])
def mark_campaign_completed(campaign_id):
    # Retrieve the campaign
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Update campaign status
    campaign.status = 'Completed'
    
    # Retrieve and update related CampaignRequests
    campaign_requests = CampaignRequest.query.filter_by(campaign_id=campaign_id).all()
    for req in campaign_requests:
        req.status = 'Completed'
    
    # Retrieve and update related AdRequests
    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()
    for req in ad_requests:
        req.status = 'Completed'
    
    # Commit the changes to the database
    db.session.commit()
    
    # Extract username from the form data
    username = request.form.get('username')
    
    # Redirect back to the active campaigns page
    return redirect(url_for('active_campaigns', username=username))

@app.route('/update_campaign_request', methods=['POST'])
def update_campaign_request():
    request_id = request.form['request_id']
    message = request.form['message']
    payment_amount = request.form['payment_amount']
  
    # Fetch and update the campaign request
    campaign_request = CampaignRequest.query.get(request_id)
    if campaign_request:
        campaign_request.messages = message
        campaign_request.payment_amount = payment_amount
        db.session.commit()
    
    # Redirect to the influencer dashboard
    username = request.form['username']
    return redirect(url_for('influencer_dashboard', username=username))

@app.route('/delete_campaign_request/<int:campaign_request_id>/<string:username>', methods=['POST'])
def delete_campaign_request(campaign_request_id, username):
    campaign_request = CampaignRequest.query.get(campaign_request_id)
    if campaign_request:
        db.session.delete(campaign_request)
        db.session.commit()
    
    # Redirect to the influencer dashboard
    return redirect(url_for('influencer_dashboard', username=username))

@app.route('/logout')
def logout():
    # Here you can implement any session clearing or logout logic if necessary
    return redirect(url_for('role_selection'))