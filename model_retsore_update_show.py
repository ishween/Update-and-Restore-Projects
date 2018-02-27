"""
    model to restore project and update detail
"""
from datetime import datetime
from app import db
from sqlalchemy.exc import IntegrityError
from flask import Response
from app.models import story_type, production_type, model_shortlist, business

class CommunicatorProject(db.Model):
    """ class to restore project and update details and show shared details"""
    __tablename__ = 'communicator_project'
    project_id = db.Column(db.String(100), primary_key=True)
    story_type_id = db.Column(db.String(100))
    production_type_id = db.Column(db.String(100))
    value = db.Column(db.Float)
    currency_name = db.Column(db.String(100))
    currency_name_short = db.Column(db.String(100))
    deadline = db.Column(db.DateTime)
    sort_id = db.Column(db.Integer)
    show_single_buisness = db.Column(db.Boolean, default=False)
    show_creative_options_within_bounds = db.Column(db.Boolean, default=False)
    location_name = db.Column(db.String(100))
    location_lattitude = db.Column(db.String(100))
    location_longitude = db.Column(db.String(100))
    location_zoom_level = db.Column(db.Integer)
    location_centre = db.Column(db.String(100))
    languages = db.relationship('CommunicatorProjectLanguage', backref='communicator_project', lazy='joined')

    @staticmethod
    def create_project(**params):
        try:
            new_details = CommunicatorProject(project_id=params.get('project_id'), story_type_id=params.get('story_type_id'), production_type_id=params.get('production_type_id'), value=params.get('value'), deadline=params.get('deadline'), show_single_buisness=params.get('show_single_buisness'))
            db.session.add(new_details)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        #print (new_details)
        response_object = {'id': new_details.project_id, 'sp':new_details.story_type_id, 'pd':new_details.production_type_id}
        return response_object

    @classmethod
    def restore_project(cls, graph, project_id):
        """ to restore the project"""
        response = {}
        communicator_project = CommunicatorProject.query.filter_by(project_id=project_id).first()
        if communicator_project is None:
            return None
        params = {}
        params['communicator_project_id'] = communicator_project.project_id
        params['story_type'] = communicator_project.story_type_id
        params['production_type'] = communicator_project.production_type_id
        params['budget'] = {}
        params['budget']['value'] = communicator_project.value
        params['budget']['currency_name'] = "Indian Rupee"
        params['budget']['currency_name_short'] = "INR"
        params['budget_value'] = communicator_project.budget_value
        params['dealine'] = communicator_project.deadline
        params['location_name'] = communicator_project.location_name
        params['location'] = {}
        params['location']['location_lattitude'] = communicator_project.location_lattitude
        params['location']['location_longitude'] = communicator_project.location_longitude
        params['map'] = {}
        params['map']['centre'] = {}
        params['map']['centre']['lattitude'] = communicator_project.location_lattitude
        params['map']['centre']['longitude'] = communicator_project.location_longitude
        params['location_zoom_level'] = communicator_project.location_zoom_level
        params['language'] = {}
        query = CommunicatorProjectLanguage.query.filter_by(communicator_project_id=project_id)
        for interaction_language in query:
            params['language']['interaction_language_id'] = interaction_language
        query = CommunicatorProjectLanguage.query.filter_by(communicator_project_id=project_id)
        for campaign_language in query:
            params['language']['campaign_language_id'] = campaign_language
        lists = {}
        lists['story_types'] = story_type.get_all_story_types(graph)
        lists['production_types'] = production_type.get_all_production_types(graph)
        params['lists'] = lists
        params['show_single_business'] = communicator_project.show_single_business
        params['show_creative_options_within_bounds'] = communicator_project.show_creative_options_within_bounds
        params['sort_criteria'] = sort_criteria.SortCriteria.get_sort_criteria(sort_id, **params)
        #params['shortlist'] = model_shortlist.ShortList.get_no_of_creative_options()
        creative_options = []
        creative_options.append(business.get_businesses(graph, **params))
        params['creative_options'] = creative_options
        return params

    @classmethod
    def update_details(cls, project_id, **kwargs):
        """ Update the details to select creative"""
        communicator_project = CommunicatorProject.query.filter_by(project_id=project_id).first()
        print(1)
        print(communicator_project)
        if communicator_project is not None:
            changed_parameter = kwargs['changed_parameter']
            if changed_parameter == 'story_type':
                communicator_project.story_type_id = kwargs['story_type']
            elif changed_parameter == 'production_type':
                communicator_project.production_type_id = kwargs['production_type']
            elif changed_parameter == 'sort_criteria':
                communicator_project.sort_id = kwargs['sort_criteria']
            elif changed_parameter == 'value':
                communicator_project.budget_value = kwargs['value']
            elif changed_parameter == 'currency_name':
                communicator_project.currency_name = 'Indian Rupee'
            elif changed_parameter == 'currency_name_short':
                communicator_project.currency_name_short = 'INR'
            elif changed_parameter == 'deadline':
                communicator_project.deadline = kwargs['deadline']
            elif changed_parameter == 'location_name':
                communicator_project.location_name = kwargs['location_name']
            elif changed_parameter == 'location_lattitude':
                communicator_project.location_lattitude = kwargs['location_lattitude']
            elif changed_parameter == 'location_longitude':
                communicator_project.location_longitude = kwargs['location_longitude']
            elif changed_parameter == 'location_zoom_level':
                communicator_project.location_zoom_level = kwargs['location_zoom_level']
            elif changed_parameter == 'location_centre':
                communicator_project.location_centre = kwargs['location_centre']
            elif changed_parameter == 'interaction_language':
                communicator_project.interaction_language = kwargs['interaction_language']
            elif changed_parameter == 'campaign_language':
                communicator_project.campaign_language = kwargs['campaign_language']
            elif changed_parameter == 'show_creative_options_within_bounds':
                communicator_project.show_creative_options_within_bounds = kwargs['show_creative_options_within_bounds']
            elif changed_parameter == 'show_single_buisness':
                communicator_project.show_single_buisness = kwargs['show_single_buisness']

    @classmethod
    def show_shared_details(cls, graph, shared_id):
        """ to show shared details """
        communicator = CommunicatorProject.query.filter_by(project_id=shared_id).first()
        if communicator is None:
            return None
        params = {}
        params['name'] = graph.data('MATCH (buisness:Business)--() WHERE buisness.uuid="{}" RETURN buisness.name'.format('communicator.project_id'))
        params['story_type'] = {}
        params['story_type']['id'] = communicator.story_type_id
        query = 'MATCH (storyType:StoryType) WHERE storyType.uuid="{}" RETURN storyType.name as name'.format(communicator.story_type_id)
        name = graph.data(query)
        params['story_type']['name'] = name[0]['name']
        params['production_type'] = {}
        params['production_type']['id'] = communicator.production_type_id
        query = 'MATCH (productionType:ProductionType)--() WHERE productionType.uuid="{}" RETURN productionType.name as name'.format(communicator.production_type_id)
        name = graph.data(query)
        params['production_type']['name'] = name[0]['name']
        params['budget'] = {}
        params['budget']['value'] = communicator.budget_value
        params['currency_name'] = 'Indian Rupee'
        params['currency_name_short'] = 'INR'
        params['deadline'] = communicator.deadline
        params['location'] = {}
        params['location']['name'] = communicator.location_name
        params['location']['location_lattitude'] = communicator.location_lattitude
        params['location']['location_longitude'] = communicator.location_longitude
        params['location']['location_zoom_level'] = communicator.location_zoom_level
        params['location']['location_centre'] = communicator.location_centre
        params['language'] = {}
        interaction_languages = []
        query = CommunicatorProjectLanguage.query.filter_by(communicator_project_id=shared_id)
        for interaction_language_id in query:
            response = {}
            query = 'MATCH (interactionLanguage:Language)--() WHERE interactionLanguage.uuid="{}" RETURN interactionLanguage.name as name, interactionLanguage.uuid as uuid,interactionLanguage.order as order, interaction_language.internal_identifier as internal_identifier'.format(interactionLanguage_id)
            name  = graph.data(query)
            response['name'] = name[0]['name']
            response['uuid'] = name[0]['uuid']
            response['order'] = name[0]['order']
            response['internal_identifier'] = name[0]['internal_identifier']
            interaction_languages.append(response)
            params['language'] = interaction_languages
        campaign_languages = []
        query = CommunicatorProjectLanguage.query.filter_by(communicator_project_id=shared_id)
        for campaign_language_id in query:
            response = {}
            query = 'MATCH (campaignLanguage:Language)--() WHERE campaignLanguage.uuid="{}" RETURN campaignLanguage.name as name,campaignLanguage.uuid as uuid,campaignLanguage.order as order,campaign_language.internal_identifier as internal_identifier'.format(campaignLanguage_id)
            name  = graph.data(query)
            response['name'] = name[0]['name']
            response['uuid'] = name[0]['uuid']
            response['order'] = name[0]['order']
            response['internal_identifier'] = name[0]['internal_identifier']
            campaign_languages.append(response)
            params['language'] = campaign_languages
        return params

class CommunicatorProjectLanguage(db.Model):
    __tablename__ = 'Communicator_Project_language'
    id = db.Column(db.String(100), primary_key=True)
    interaction_language_id = db.Column(db.String(100))
    campaign_language_id = db.Column(db.String(100))
    communicator_project_id = db.Column(db.String(100), db.ForeignKey('communicator_project.project_id'))