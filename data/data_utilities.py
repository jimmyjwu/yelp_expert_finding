"""
Utilities specifically for the data processing scripts and data interfaces.
"""
import os
from datetime import date

THIS_FILE_PATH = os.path.dirname(__file__)
CURRENT_YEAR = date.today().year

DEFAULT_RAW_REVIEWS_FILE_NAME = 'yelp_academic_dataset_review.json'
DEFAULT_RAW_USERS_FILE_NAME = 'yelp_academic_dataset_user.json'

DEFAULT_REVIEW_LENGTHS_FILE_NAME = 'user_average_review_lengths.txt'
DEFAULT_READING_LEVELS_FILE_NAME = 'user_reading_levels.txt'
DEFAULT_PAGERANKS_FILE_NAME = 'user_pageranks.txt'
DEFAULT_COMBINED_USERS_FILE_NAME = 'combined_users.txt'

DEFAULT_D3_GRAPH_FILE_NAME = 'users_graph.json'

DEFAULT_USER_ATTRIBUTES = [
	'ID',
	'review_count',
	'average_stars',
	# 'friend_count',
	'months_member',
	'years_elite',
	# 'fan_count',
	# 'funny_vote_count',
	# 'useful_vote_count',
	# 'cool_vote_count',
	'average_review_length',
	'average_reading_level',
	'pagerank',
]

ALL_USER_ATTRIBUTES = [
	'ID',
	'review_count',
	'average_stars',
	'friend_count',
	'months_member',
	'years_elite',
	'fan_count',
	'funny_vote_count',
	'useful_vote_count',
	'cool_vote_count',
	'average_review_length',
	'average_reading_level',
	'pagerank',
]


def _raw_data_absolute_path(relative_path):
	"""Given the name of a raw data file, returns its absolute path."""
	return os.path.join(THIS_FILE_PATH, 'raw_data/' + relative_path)


def _processed_data_absolute_path(relative_path):
	"""Given the name of a processed data file, returns its absolute path."""
	return os.path.join(THIS_FILE_PATH, 'processed_data/' + relative_path)


def _read_single_user_attribute(input_file_name):
	"""
	Given a processed user attribute file of the form
		user_1_ID user_1_attribute_value
			.
			.
			.
		user_N_ID user_N_attribute_value
	returns a dictionary:
		{ user_1_ID: user_1_attribute_value, ..., user_N_ID: user_N_attribute_value }
	"""
	attribute_for_user = {}

	with open(_processed_data_absolute_path(input_file_name)) as attribute_file:

		for user_line in attribute_file:
			user_ID, attribute_value = user_line.split()
			attribute_for_user[user_ID] = attribute_value

	return attribute_for_user



