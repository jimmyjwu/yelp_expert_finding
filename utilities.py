"""
Utilities for file manipulation, graph processing, etc.
"""

import json
import itertools
from collections import Counter

import networkx
import numpy
import matplotlib
from matplotlib import pyplot


def make_attribute_boolean(users, attribute):
	"""
	Given a list of users and an attribute name, transforms attribute values:
		value = 0	-->		new value = 0
		value > 0	-->		new value = 1
	and returns a new list of users.
	"""
	transformed_users = []
	for user in users:
		user_copy = {key: value for key, value in user.items() if key != attribute}
		user_copy[attribute] = 1 if user[attribute] > 0 else 0
		transformed_users += [user_copy]
	return transformed_users


def designate_attribute_as_label(users, attribute):
	"""
	Given an attribute name, changes that attribute to 'label' in all user
	dictionaries. Use for regression fitting.
	"""
	labeled_users = []
	for user in users:
		user_copy = {key: value for key, value in user.items() if key != attribute}
		user_copy['label'] = user[attribute]
		labeled_users += [user_copy]
	return labeled_users


def remove_labels(users, label_name='label'):
	"""
	Given a list of user dictionaries, returns a list of user dictionaries with
	a label attribute from each user removed.
	"""
	unlabeled_users = []
	for user in users:
		unlabeled_users += [{key: value for key, value in user.items() if key != label_name}]
	return unlabeled_users


def normalize_users(users, excluded_attributes=[]):
	"""
	Given a list of user dictionaries with numeric values, returns a list of
	user dictionaries in which all attributes, EXCEPT those whose names are in
	excluded_attributes, arenormalized to [0, 1].
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


def print_first_elements(values, k=1):
	"""
	Prints the first k values.
	"""
	for value in values[0:k]:
		print value
	print ''


def unique(values):
	"""
	Given a list of values, returns a list of unique values.
	"""
	return list(set(values))


def most_frequent_values_and_frequencies(values, k):
	"""
	Given a list of values, returns a list of tuples of the k most frequent values
	and their respective frequencies.
	"""
	return sorted(frequencies(values).items(), key=lambda value: value[1])[-k:]


def smallest_unique_values(values, k):
	"""
	Given a list of values, returns a list of the k smallest values.
	"""
	return sorted(unique(values))[0:k]


def largest_unique_values(values, k):
	"""
	Given a list of values, returns a list of the k largest values.
	"""
	return sorted(unique(values))[-k:]


def frequencies(values):
	"""
	Given a list of values, returns a dictionary mapping each unique value
	to the frequency with which it occurs.
	"""
	return Counter(values)


def remove_low_degree_nodes(graph, minimum_degree=1):
	"""
	Removes all nodes with degree less than minimum_degree.
	"""
	for node in graph.nodes():
		if graph.degree(node) < minimum_degree:
			graph.remove_node(node)


def highest_degree_node_in_graph(graph):
	"""
	Given a NetworkX graph, returns the node with highest degree.
	"""
	max_degree = 0
	max_degree_node = None
	for node, degree in graph.degree_iter():
		if degree > max_degree:
			max_degree = degree
			max_degree_node = node

	return max_degree_node


def show_histogram(values, value_name='Value', bins=100, range_to_display=(0,0)):
	if range_to_display == (0,0):
		n, bins, patches = pyplot.hist(values, bins=bins, normed=1, facecolor='g', alpha=0.75)
	else:
		n, bins, patches = pyplot.hist(values, bins=bins, range=range_to_display, normed=1, facecolor='g', alpha=0.75)
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


def read_users_from_yelp_JSON_file(file_name='yelp_academic_dataset_user.json'):
	"""
	Given a Yelp dataset user file (with users in JSON format), returns a list of
	user dictionaries with numeric values for various attributes.
	"""
	users_file = open(file_name)
	raw_users = [json.loads(line) for line in users_file.readlines()]

	users = []
	for user in raw_users:
		users += [
			{
				'ID': user['user_id'],
				'review_count': user['review_count'],
				'average_stars': user['average_stars'],
				'friend_count': len(user['friends']),
				'years_member': 2014 - int(user['yelping_since'].split('-')[0]),
				'years_elite': len(user['elite']),
			}
		]
	return users


def output_graph_to_D3_JSON_file(file_name='users_graph.json'):
	"""
	Given a NetworkX graph, writes the graph to a JSON file in a format suitable
	for displaying a D3 force-directed graph.
	"""
	JSON = {'nodes': [], 'links': []}
	for user_ID in graph.nodes_iter():
		JSON['nodes'] += [{'name': user_ID}]
	for friend_1_ID, friend_2_ID in graph.edges_iter():
		JSON['links'] += [{'source': friend_1_ID, 'target': friend_2_ID, 'value': 1}]

	with open(file_name, 'w') as output_file:
		json.dump(JSON, output_file)




