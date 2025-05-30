from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from models import db, User, Campaign, AdRequest, Influencer, Sponsor, CampaignRequest

app = Flask(__name__)
api = Api(app)

class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if user:
            return jsonify({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            })
        return {'message': 'User not found'}, 404

    def post(self):
        data = request.get_json()
        new_user = User(
            username=data['username'],
            password=data['password'],
            email=data['email'],
            role=data['role']
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created', 'id': new_user.id})

    def put(self, user_id):
        data = request.get_json()
        user = User.query.get(user_id)
        if user:
            user.username = data.get('username', user.username)
            user.password = data.get('password', user.password)
            user.email = data.get('email', user.email)
            user.role = data.get('role', user.role)
            db.session.commit()
            return jsonify({'message': 'User updated'})
        return {'message': 'User not found'}, 404

    def delete(self, user_id):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return {'message': 'User deleted'}
        return {'message': 'User not found'}, 404

class CampaignResource(Resource):
    def get(self, campaign_id):
        campaign = Campaign.query.get(campaign_id)
        if campaign:
            return jsonify({
                'id': campaign.id,
                'name': campaign.name,
                'description': campaign.description,
                'start_date': str(campaign.start_date),
                'end_date': str(campaign.end_date),
                'budget': campaign.budget,
                'visibility': campaign.visibility,
                'goals': campaign.goals,
                'niche': campaign.niche,
                'status': campaign.status,
                'flagged': campaign.flagged,
                'user_id': campaign.user_id
            })
        return {'message': 'Campaign not found'}, 404

    def post(self):
        data = request.get_json()
        new_campaign = Campaign(
            name=data['name'],
            description=data['description'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            budget=data['budget'],
            visibility=data['visibility'],
            goals=data['goals'],
            niche=data['niche'],
            status=data['status'],
            flagged=data.get('flagged', False),
            user_id=data['user_id']
        )
        db.session.add(new_campaign)
        db.session.commit()
        return jsonify({'message': 'Campaign created', 'id': new_campaign.id})

    def put(self, campaign_id):
        data = request.get_json()
        campaign = Campaign.query.get(campaign_id)
        if campaign:
            campaign.name = data.get('name', campaign.name)
            campaign.description = data.get('description', campaign.description)
            campaign.start_date = data.get('start_date', campaign.start_date)
            campaign.end_date = data.get('end_date', campaign.end_date)
            campaign.budget = data.get('budget', campaign.budget)
            campaign.visibility = data.get('visibility', campaign.visibility)
            campaign.goals = data.get('goals', campaign.goals)
            campaign.niche = data.get('niche', campaign.niche)
            campaign.status = data.get('status', campaign.status)
            campaign.flagged = data.get('flagged', campaign.flagged)
            db.session.commit()
            return jsonify({'message': 'Campaign updated'})
        return {'message': 'Campaign not found'}, 404

    def delete(self, campaign_id):
        campaign = Campaign.query.get(campaign_id)
        if campaign:
            db.session.delete(campaign)
            db.session.commit()
            return {'message': 'Campaign deleted'}
        return {'message': 'Campaign not found'}, 404

# Repeat similar patterns for AdRequest, Influencer, Sponsor, and CampaignRequest

api.add_resource(UserResource, '/user', '/user/<int:user_id>')
api.add_resource(CampaignResource, '/campaign', '/campaign/<int:campaign_id>')

# Add resources for AdRequest, Influencer, Sponsor, and CampaignRequest

if __name__ == '__main__':
    app.run(debug=True)