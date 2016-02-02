"""
General utilities for working with Python data structures, NetworkX graphs, etc.
"""
import random
from collections import Counter, defaultdict

import networkx
from matplotlib import pyplot


def filter_dictionary_by_keys(dictionary, desired_keys):
	"""Returns a dictionary containing only entries whose keys are in desired_keys."""
	desired_key_set = set(desired_keys)
	return {key: value for key, value in dictionary.iteritems() if key in desired_keys}


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


def average(values):
	"""Returns the average (as a float) of a list of numerical values."""
	return sum(values) / float(len(values)) if len(values) > 0 else 0


def safe_divide(x, y, default_value=0):
	"""Returns x / y as a float, or default_value if y = 0."""
	return float(x) / y if y > 0 else default_value


def print_first_items(values, k=1):
	"""Prints the first k values on separate lines."""
	for i in xrange(0,k):
		print values[i]
	print ''


def format_as_percentage(value, decimal_places=2):
	return ('{:.' + str(decimal_places) + '%}').format(value)


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


