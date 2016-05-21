"""
Utilities specifically for the data processing scripts and data interfaces.
"""
import os
import json
from datetime import date

from utilities import *

THIS_FILE_PATH = os.path.dirname(__file__)
CURRENT_YEAR = date.today().year
CURRENT_MONTH = date.today().month

DEFAULT_RAW_USERS_FILE_NAME = 'yelp_academic_dataset_user.json'
DEFAULT_RAW_REVIEWS_FILE_NAME = 'yelp_academic_dataset_review.json'
DEFAULT_RAW_TIPS_FILE_NAME = 'yelp_academic_dataset_tip.json'

DEFAULT_BASIC_ATTRIBUTES_FILE_NAME = 'user_basic_attributes.txt'
DEFAULT_REVIEW_LENGTHS_FILE_NAME = 'user_average_review_lengths.txt'
DEFAULT_READING_LEVELS_FILE_NAME = 'user_average_reading_levels.txt'
DEFAULT_TIP_COUNTS_FILE_NAME = 'user_tip_counts.txt'
DEFAULT_PAGERANKS_FILE_NAME = 'user_pageranks.txt'
DEFAULT_COMBINED_USERS_FILE_NAME = 'combined_users.txt'

DEFAULT_TRAINING_SET_FILE_NAME = 'training_set.txt'
DEFAULT_TEST_SET_FILE_NAME = 'test_set.txt'

DEFAULT_D3_GRAPH_FILE_NAME = 'users_D3_graph.json'

# List of (attribute name, function that returns attribute value, given a raw user dictionary)
BASIC_USER_ATTRIBUTES_AND_EXTRACTORS = [
	( 'ID', lambda raw_user: raw_user['user_id'] ),
	( 'review_count', lambda raw_user: raw_user['review_count'] ),
	( 'average_stars', lambda raw_user: raw_user['average_stars'] ),
	( 'funny_vote_count', lambda raw_user: raw_user['votes']['funny'] ),
	( 'useful_vote_count', lambda raw_user: raw_user['votes']['useful'] ),
	( 'cool_vote_count', lambda raw_user: raw_user['votes']['cool'] ),
	( 'friend_count', lambda raw_user: len(raw_user['friends']) ),
	( 'years_elite', lambda raw_user: len(raw_user['elite']) ),
	( 'months_member', lambda raw_user: _months_since_year_and_month(raw_user['yelping_since']) ),
	( 'compliment_count', lambda raw_user: sum(raw_user['compliments'].itervalues()) ),
	( 'fan_count', lambda raw_user: raw_user['fans'] ),
]

# Attributes that can be extracted solely from the raw Yelp user file
BASIC_USER_ATTRIBUTES = list(zip(*BASIC_USER_ATTRIBUTES_AND_EXTRACTORS)[0])

# All user attributes available
ALL_USER_ATTRIBUTES = list(BASIC_USER_ATTRIBUTES) + [
	'average_review_length',
	'average_reading_level',
	'tip_count',
	'pagerank',
]

# All attributes used in the training and test sets
TRAINING_AND_TEST_SET_ATTRIBUTES = ['label' if attribute=='years_elite' else attribute for attribute in ALL_USER_ATTRIBUTES]

# Used for re-casting attribute values when reading from processed data files
CASTER_FOR_ATTRIBUTE_NAME = {
	'ID': unicode,
	'review_count': int,
	'average_stars': float,
	'funny_vote_count': int,
	'useful_vote_count': int,
	'cool_vote_count': int,
	'friend_count': int,
	'years_elite': int,
	'months_member': int,
	'compliment_count': int,
	'fan_count': int,
	'average_review_length': int,
	'average_reading_level': float,
	'tip_count': int,
	'pagerank': float,
	'label': int,
}


def _months_since_year_and_month(year_month_string):
	"""Returns the number of months' difference between now and a month formatted as YYYY-MM."""
	year, month = map(int, year_month_string.split('-'))
	return 12 * (CURRENT_YEAR - year) - month + CURRENT_MONTH


def raw_data_absolute_path(relative_path):
	"""Given the name of a raw data file, returns its absolute path."""
	return os.path.join(THIS_FILE_PATH, 'raw_data/' + relative_path)


def processed_data_absolute_path(relative_path):
	"""Given the name of a processed data file, returns its absolute path."""
	return os.path.join(THIS_FILE_PATH, 'processed_data/' + relative_path)


def read_single_user_attribute(input_file_name, attribute_name):
	"""
	Given a processed user attribute file of the form
		user_1_ID user_1_attribute_value
			.
			.
			.
		user_N_ID user_N_attribute_value

	and the name of the attribute, returns a dictionary:
		{ user_1_ID: user_1_attribute_value, ..., user_N_ID: user_N_attribute_value }
	"""
	attribute_for_user = {}
	attribute_caster = CASTER_FOR_ATTRIBUTE_NAME[attribute_name] # Type-casting function for this attribute
	ID_caster = CASTER_FOR_ATTRIBUTE_NAME['ID']

	with open(processed_data_absolute_path(input_file_name)) as attribute_file:

		for user_line in attribute_file:
			user_ID, attribute_value = user_line.split()
			attribute_for_user[ID_caster(user_ID)] = attribute_caster(attribute_value)

	return attribute_for_user


def write_single_user_attribute(attribute_for_user, output_file_name):
	"""
	Given a dictionary
		{ user_1_ID: user_1_attribute_value, ..., user_N_ID: user_N_attribute_value }

	writes a file of the form
		user_1_ID user_1_attribute_value
			.
			.
			.
		user_N_ID user_N_attribute_value
	"""
	with open(processed_data_absolute_path(output_file_name), 'w') as attribute_file: # Write mode; overwrite old file if it exists
		
		for user_ID, attribute in attribute_for_user.iteritems():
			attribute_file.write(user_ID + ' ' + str(attribute) + '\n')


def read_multiple_user_attributes(input_file_name, attributes, order_attributes=False):
	"""
	Given a processed user attributes file of the form
		attribute_1_name ... attribute_K_name
		user_1_attribute_1_value ... user_1_attribute_K_value
			.
			.
			.
		user_N_attribute_1_value ... user_N_attribute_K_value

	and a list of desired attributes, returns a list of user dictionaries:
		[
			{attribute_1_name: user_1_attribute_1_value, ..., attribute_k_name: user_1_attribute_k_value},
				.
				.
				.
			{attribute_1_name: user_N_attribute_1_value, ..., attribute_k_name: user_N_attribute_k_value}
		]
	where the user dictionaries include only the k <= K desired attributes, in the order given.
	"""
	users = []
	DictionaryClass = OrderedDict if order_attributes else dict

	with open(processed_data_absolute_path(input_file_name)) as attributes_file:

		# Row 1: attribute names
		attributes_in_file = attributes_file.readline().split()

		# List of (desired attribute name, index in attributes_in_file where desired attribute occurs, caster for desired attribute)
		attribute_names_indices_and_casters = [ (attribute, attributes_in_file.index(attribute), CASTER_FOR_ATTRIBUTE_NAME[attribute]) for attribute in attributes ]

		# Rows 2,...,N: users' attribute values written in the same order
		for user_line in attributes_file:
			user_attribute_values = user_line.split()
			users += [ DictionaryClass([ ( attribute, caster(user_attribute_values[index]) ) for attribute, index, caster in attribute_names_indices_and_casters ]) ]

	return users


def write_multiple_user_attributes(users, attributes, output_file_name):
	"""
	Given a list of (or iterator over) user dictionaries and a list of user attributes, writes a
	file of the form
		attribute_1_name ... attribute_K_name
		user_1_attribute_1_value ... user_1_attribute_K_value
			.
			.
			.
		user_N_attribute_1_value ... user_N_attribute_K_value
	"""
	with open(processed_data_absolute_path(output_file_name), 'w') as user_attributes_file: # Write mode; overwrite old file if it exists

		# Row 1: attribute names
		user_attributes_file.write( ' '.join(attributes) + '\n' )

		# Rows 2,...,N: users' attribute values written in the same order
		for user in users:
			user_attributes_file.write( ' '.join([str(user[attribute]) for attribute in attributes]) + '\n' )



def binarize_attribute(users, attribute):
	"""
	Given a list of user dictionaries and an attribute name, maps the designated attribute values
	of all users as follows:
		value = 0	-->		new value = 0
		value != 0	-->		new value = 1
	"""
	[ user.update( { attribute: int(bool(user[attribute])) } ) for user in users ]


def designate_attribute_as_label(users, attribute):
	"""
	Given a list of user dictionaries and an attribute name, replaces the designated attribute
	with a 'label' attribute which takes on the removed attribute's value.
	"""
	for user in users:
		user['label'] = user.pop(attribute)



