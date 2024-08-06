from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin, sponsor, influencer

    # Relationships
    influencer = db.relationship('Influencer', backref='user_influencer', uselist=False)
    sponsor = db.relationship('Sponsor', backref='user_sponsor', uselist=False)
    ad_requests = db.relationship('AdRequest', backref='user_ad_request')  # Ensure unique backref name
    campaigns = db.relationship('Campaign', backref='user_campaign')  # Ensure unique backref name


class Campaign(db.Model):
    __tablename__ = 'campaign'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(10), nullable=False)  # public, private
    goals = db.Column(db.Text, nullable=False)
    niche = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    flagged = db.Column(db.Boolean, default=False, nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    ad_requests = db.relationship('AdRequest', backref='campaigns_ad_requests')
    campaign_requests = db.relationship('CampaignRequest', backref='campaign_campaign_requests')



class AdRequest(db.Model):
    __tablename__ = 'ad_request'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # Pending, Accepted, Rejected
    complete = db.Column(db.Boolean, default=False, nullable=False)
    complete_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    payment = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    influencer = db.relationship('User', backref='ad_requests_user', foreign_keys=[influencer_id])
    campaign = db.relationship('Campaign', backref='ad_requests_campaign', foreign_keys=[campaign_id])



class Influencer(db.Model):
    __tablename__ = 'influencer'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    profile_picture = db.Column(db.String(150), nullable=True)
    niche = db.Column(db.String(50), nullable=False)
    reach = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(150), nullable=False)  # This will store the social media platforms as a comma-separated string
    flagged = db.Column(db.Boolean, default=False)
    # Relationships
    user = db.relationship('User', backref='influencer_user', uselist=False)

class Sponsor(db.Model):
    __tablename__ = 'sponsor'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    user = db.relationship('User', backref='sponsor_user', uselist=False)


class CampaignRequest(db.Model):
    __tablename__ = 'campaign_request'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)  # Added this field
    messages = db.Column(db.Text, nullable=True)
    payment_amount = db.Column(db.Float, nullable=False)  # Added this field
    status = db.Column(db.String(10), nullable=False)  # Pending, Accepted, Rejected
    complete = db.Column(db.Boolean, default=False, nullable=False)
    complete_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    payment = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    # Relationships
    campaign = db.relationship('Campaign', backref='campaign_requests_campaign', lazy=True)
    influencer = db.relationship('User', backref='campaign_requests', foreign_keys=[influencer_id])
    sponsor = db.relationship('Sponsor', backref='campaign_requests_sponsor', foreign_keys=[sponsor_id])

