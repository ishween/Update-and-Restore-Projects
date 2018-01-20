from flask import Flask
from py2neo import Graph,Node,Relationship
from config import graph

def get_buisnesses(graph,**kwargs):
	
	get_ids = graph.data('MATCH (s:StoryType)-[:IS_MAPPED_TO]-(sp:StoryTypeForPreference)-[:HAS_STORY_TYPE_FOR_PREFERENCE|:HAS_STORY_TYPE_WITH_STORY_BUDGET|:HAS_STORY_TYPE_WITH_PRODUCTION_BUDGET|:HAS_STORY_TYPE_WITH_COMPLETE_BUDGET]-(b:Business)-[:HAS_PRODUCTION_TYPE]-(p:ProductionType) WHERE s.uuid = "{}" AND p.uuid = "{}" WITH sp, p, b MATCH (b)-[:WantsProjectStage]-(ps:ProjectStagesDesired) RETURN sp.uuid AS story_type_id, sp.classification AS story_type_classification, p.uuid AS production_type_id, b.uuid AS business_id, b.name AS business_name, b.profilePhoto AS business_profile_photo, COLLECT( DISTINCT ps) AS stages'.format(kwargs['story_type']['id'], kwargs['production_type']['id']))

	buisnesses_list = []
	for objects in get_ids:
		if len(objects['stages']) > 1:
			if objects['story_type_classification'] == 'major':
				story = {}
				production = {}
				query = graph.data('MATCH (s:StoryTypeForPreference)-[r:HAS_STORY_TYPE_WITH_STORY_BUDGET]-(b:Business) WHERE s.uuid = "{}" AND b.uuid = "{}" RETURN r.minimum_budget AS budget, r.minimum_time AS time, r.proposal_deposit AS proposal_deposit, r.proposal_free AS first_proposal_free'.format(objects['story_type_id'], objects['business_id']))
				if len(query) > 0:
					story['budget'] = query[0]['budget']
					story['time'] = query[0]['time']
					story['proposal_deposit'] = query[0]['proposal_deposit'] if obj[0]['proposal_deposit'] else 0
					story['first_proposal_free'] = query[0]['first_proposal_free']
				else:
					story['budget'] = None
					story['time'] = None

				query = graph.data('MATCH (s:StoryTypeForPreference)-[r:HAS_STORY_TYPE_WITH_PRODUCTION_BUDGET]-(b:Business) WHERE s.uuid = "{}" AND b.uuid = "{}" RETURN r.minimum_budget AS budget, r.minimum_time AS time, r.proposal_deposit AS proposal_deposit, r.proposal_free AS first_proposal_free'.format(entity['story_type_id'], entity['business_id']))
				if len(query) > 0:
					production['budget'] = query[0]['budget']
					production['time'] = query[0]['time']
					production['proposal_deposit'] = query[0]['proposal_deposit'] if obj[0]['proposal_deposit'] else 0
					production['first_proposal_free'] = query[0]['first_proposal_free']
				else:
					production['budget'] = None
					production['time'] = None

				if story['budget'] and production['budget'] and story['time'] and production['time']:
					objects['budget'] = story['budget'] + production['budget']
					objects['time'] = story['time'] + production['time']
					objects['proposal_deposit'] = story['proposal_deposit'] + production['proposal_deposit']
					objects['first_proposal_free'] = story['first_proposal_free'] | production['first_proposal_free']
					buisnesses_list.append(objects.copy())
			else:
				query = graph.data('MATCH (s:StoryTypeForPreference)-[r:HAS_STORY_TYPE_WITH_COMPLETE_BUDGET]-(b:Business) WHERE s.uuid = "{}" AND b.uuid = "{}" RETURN r.minimum_budget AS budget, r.minimum_time AS time, r.proposal_deposit AS proposal_deposit, r.proposal_free AS first_proposal_free'.format(entity['story_type_id'], entity['business_id']))
				budget_and_time = {}
				if len(query) > 0:
					budget_and_time = query[0]
				else:
					budget_and_time['budget'] = None
					budget_and_time['time'] = None
				if budget_and_time['budget'] and budget_and_time['time']:
					objects['budget'] = budget_and_time['budget']
					objects['time'] = budget_and_time['time']
					buisnesses_list.append(objects.copy())

			city = {}
			city = graph.data('MATCH (b:Business)-[h:Has_city] WHERE b.uuid="{}" RETURN h.name'.format(objects['business_id']))

			decoration_data = graph.data('MATCH (b:Business)-[:HAS_BUSINESS_PROFILE]-(p) WHERE b.uuid = "{}" WITH b, p MATCH (b)-[:BUDGET_CURRENCY]-(c) RETURN p.profileURL AS profile_url, c AS currency'.format(objects['business_id']))

			obj = {}
			obj['id'] = entity['business_id']
			obj['name'] = entity['business_name']
			obj['profile_photo'] = entity['business_profile_photo']
			obj['profile_url'] = decoration_data[0]['profile_url']
			obj['minimum_budget'] = {}
			obj['minimum_budget']['value'] = entity['budget']
			obj['minimum_budget']['currency'] = decoration_data[0]['currency']
			obj['minimum_time'] = entity['time']
			obj['proposal_deposit'] = entity['proposal_deposit']
			obj['first_proposal_free'] = entity['first_proposal_free']
			obj['location'] = {}
			obj['location']['city'] = city['name']
			#obj['location']['country'] = country['name']

	return obj


