"""
Utilities for file manipulation, graph processing, etc.
"""

import json
import itertools
from collections import Counter, defaultdict
from datetime import date

import networkx
import numpy
import matplotlib
import math
from matplotlib import pyplot
from readability.readability import Readability


def join_dictionaries(dictionaries_1, dictionaries_2, join_key):
	"""
	Given two lists of dictionaries, returns a list of new dictionaries that
	are the original dictionaries joined by join_key.
	NOTE: dictionaries_2 must be a superset of dictionaries_1.
	"""
	pairs_to_join = {dictionary[join_key]: [dictionary, None] for dictionary in dictionaries_1}
	for dictionary in dictionaries_2:
		if dictionary[join_key] in pairs_to_join:
			pairs_to_join[dictionary[join_key]][1] = dictionary
	pairs_to_join = pairs_to_join.values()

	joined_dictionaries = []
	for dictionary_1, dictionary_2 in pairs_to_join:
		joined_dictionaries += [ dict( dictionary_1.items() + dictionary_2.items() ) ]

	return joined_dictionaries


def make_attribute_boolean(users, attribute):
	"""
	Given a list of user dictionaries and an attribute name, returns a new list
	of users whose designated attribute is transformed as follows:
		value <= 0	-->		new value = 0
		value > 0	-->		new value = 1
	and all other attributes are copied without change.
	"""
	transformed_users = []
	for user in users:
		user_copy = {key: value for key, value in user.items() if key != attribute}
		user_copy[attribute] = 1 if user[attribute] > 0 else 0
		transformed_users += [user_copy]
	return transformed_users


def designate_attribute_as_label(users, attribute):
	"""
	Given a list of user dictionaries and an attribute name, returns a new list
	of users whose designated attribute is named 'label', and all other attributes
	are copied without change.
	"""
	labeled_users = []
	for user in users:
		user_copy = {key: value for key, value in user.items() if key != attribute}
		user_copy['label'] = user[attribute]
		labeled_users += [user_copy]
	return labeled_users


def remove_labels(users, label_name='label'):
	"""
	Given a list of user dictionaries, returns a new list of users without
	the label attribute, but with all other attributes copied.
	"""
	unlabeled_users = []
	for user in users:
		unlabeled_users += [{key: value for key, value in user.items() if key != label_name}]
	return unlabeled_users


def normalize_users(users, excluded_attributes=[]):
	"""
	Given a list of user dictionaries whose attributes are numeric values, returns a list of
	users in which all attributes, EXCEPT those whose names are in excluded_attributes,
	are normalized to [0, 1].

	Normalization is done using min-max.
	"""
	excluded_attributes = set(excluded_attributes)

	# Find extreme values for each attribute
	max_user = {attribute: float('-infinity') for attribute in users[0].keys()}
	min_user = {attribute: float('infinity') for attribute in users[0].keys()}
	for user in users:
		for attribute, value in user.items():
			if attribute not in excluded_attributes:
				max_user[attribute] = max(max_user[attribute], value)
				min_user[attribute] = min(min_user[attribute], value)

	# Normalize users
	for user in users:
		for attribute, value in user.items():
			if attribute not in excluded_attributes:
				user[attribute] = float(value - min_user[attribute]) / (max_user[attribute] - min_user[attribute])

	return users


def print_first_items(values, k=1):
	"""Prints the first k values on separate lines."""
	for i in xrange(0,k):
		print values[i]
	print ''


def unique_values(values):
	"""Given a list of values, returns a list of unique values."""
	return list(set(values))


def most_frequent_values_and_frequencies(values, k):
	"""
	Given a list of values, returns a list of tuples:
		[ (most common value, its frequency), ..., (kth most common value, its frequency) ]
	"""
	return Counter(values).most_common(k)


def smallest_unique_values(values, k):
	"""Given a list of values, returns a list of the k smallest unique values."""
	return sorted(unique_values(values))[0:k]


def largest_unique_values(values, k):
	"""Given a list of values, returns a list of the k largest unique values."""
	return sorted(unique_values(values))[-k:]


def frequencies(values):
	"""Given a list of values, returns a dictionary mapping each unique value to the frequency with which it occurs."""
	return Counter(values)


def remove_low_degree_nodes(graph, minimum_degree=1):
	"""Removes all nodes in a graph with degree less than minimum_degree."""
	for node in graph.nodes():
		if graph.degree(node) < minimum_degree:
			graph.remove_node(node)


def highest_degree_node_in_graph(graph):
	"""Given a graph, returns the node with highest degree."""
	return max(graph.degree_iter(), key=lambda (node,degree): degree)[0]


def show_histogram(values, value_name='Value', bins=100, range_to_display=(0,0), normed=False):
	if range_to_display == (0,0):
		n, bins, patches = pyplot.hist(values, bins=bins, normed=normed, facecolor='g', alpha=0.75)
	else:
		n, bins, patches = pyplot.hist(values, bins=bins, range=range_to_display, normed=normed, facecolor='g', alpha=0.75)
	pyplot.xlabel(value_name)
	pyplot.ylabel('Frequency')
	pyplot.title('Histogram of ' + value_name + 's')
	pyplot.axis('tight')
	pyplot.grid(True)
	pyplot.show()


def read_graph_from_yelp_JSON_file(file_name='yelp_academic_dataset_user.json'):
	"""
	Given a Yelp dataset user file (with users in JSON format), returns a NetworkX
	graph of the users and their friendships.
	"""
	users_file = open(file_name)
	users = [json.loads(line) for line in users_file.readlines()]

	graph = networkx.Graph()
	for user in users:
		user_ID = user['user_id']
		graph.add_node(user_ID)
		for friend_ID in user['friends']:
			graph.add_edge(user_ID, friend_ID)

	return graph


def read_user_reading_levels_from_yelp_JSON_file(file_name='yelp_academic_dataset_review.json'):
	"""
	Given a Yelp dataset reviews file (with reviews in JSON format), returns a
	dictionary mapping user ID to the user's reading level.
	"""
	# Hyperparameters
	LINES_TO_ANALYZE = 10000	# For reading level analysis only
	USE_REVIEW_LENGTH = True 	# Use review length (in words) rather than computationally expensive reading level

	review_reading_levels_for_user = defaultdict(list)

	with open(file_name) as reviews_file:
		if USE_REVIEW_LENGTH:
			for review in reviews_file:
				review = json.loads(review)
				review_reading_levels_for_user[review['user_id']] += [len(review['text'].split())]
		else:
			lines_used = 0
			for review in reviews_file:
				if lines_used > LINES_TO_ANALYZE:
					break
				else:
					lines_used += 1
				review = json.loads(review)
				try:
					readability_analyzer = Readability(review['text'])
					review_reading_levels_for_user[review['user_id']] += [readability_analyzer.SMOGIndex()]
				except UnicodeEncodeError as e:
					pass

	print 'CHECKPOINT 1'

	# Map each user to the average reading level of his/her reviews
	average_reading_level_for_user = {}
	for user_ID, reading_levels in review_reading_levels_for_user.iteritems():
		average_reading_level_for_user[user_ID] = float(sum(reading_levels)) / len(reading_levels)

	print 'CHECKPOINT 2'

	return average_reading_level_for_user


def read_users_from_yelp_JSON_file(file_name='yelp_academic_dataset_user.json', model_type='naive_bayes'):
	"""
	Given a Yelp dataset user file (with users in JSON format), returns a list of
	user dictionaries with numeric values for various attributes.
	"""
	current_year = date.today().year
	users_file = open(file_name)
	raw_users = [json.loads(line) for line in users_file.readlines()]

	users = []
	for raw_user in raw_users:
		user = {
			'ID': raw_user['user_id'],
			'review_count': raw_user['review_count'],
			'average_stars': raw_user['average_stars'],
			# 'friend_count': len(raw_user['friends']),
			'months_member': 12 * (current_year - int(raw_user['yelping_since'].split('-')[0]) - 1) + (12 - int(raw_user['yelping_since'].split('-')[1])) + 5,
			'years_elite': len(raw_user['elite']),
			# 'fan_count': raw_user['fans'],
		}

		if model_type == 'naive_bayes':
			pass
		elif model_type == 'linear_regression':
			user['funny_vote_count'] = raw_user['votes']['funny']
			user['useful_vote_count'] = raw_user['votes']['useful']
			user['cool_vote_count'] = raw_user['votes']['cool']
		
		users += [user]
	return users





