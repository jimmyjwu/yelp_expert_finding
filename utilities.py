"""
Utilities for file manipulation, graph processing, etc.
"""

import json
import itertools
from collections import Counter, defaultdict

import networkx
import numpy
import matplotlib
import math
from matplotlib import pyplot
from readability.readability import Readability


def join_dictionaries(dictionaries_1, dictionaries_2, join_key):
	"""
	Given two lists of dictionaries, returns a list of new dictionaries that are the original
	dictionaries joined by join_key.
	
		Example: dictionaries_1 and dictionaries_2 are lists of user dictionaries, but have
		different attributes, and we want a single list of users that have their combined
		attributes. The 'join key' is the user ID.

	NOTE: dictionaries_2 must be a superset of dictionaries_1.
	"""
	pairs_to_join = {dictionary[join_key]: [dictionary, None] for dictionary in dictionaries_1}
	for dictionary in dictionaries_2:
		if dictionary[join_key] in pairs_to_join:
			pairs_to_join[dictionary[join_key]][1] = dictionary

	joined_dictionaries = []
	for dictionary_1, dictionary_2 in pairs_to_join.itervalues():
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
		user_copy = {key: value for key, value in user.iteritems() if key != attribute}
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
		user_copy = {key: value for key, value in user.iteritems() if key != attribute}
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
		for attribute, value in user.iteritems():
			if attribute not in excluded_attributes:
				max_user[attribute] = max(max_user[attribute], value)
				min_user[attribute] = min(min_user[attribute], value)

	# Normalize users
	for user in users:
		for attribute, value in user.iteritems():
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


