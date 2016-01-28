"""
Utilities specifically for the data processing scripts and data interfaces.
"""
import os

THIS_FILE_PATH = os.path.dirname(__file__)

DEFAULT_RAW_REVIEWS_FILE_NAME = 'yelp_academic_dataset_review.json'
DEFAULT_RAW_USERS_FILE_NAME = 'yelp_academic_dataset_user.json'

DEFAULT_REVIEW_LENGTHS_FILE_NAME = 'user_average_review_lengths.txt'
DEFAULT_READING_LEVELS_FILE_NAME = 'user_reading_levels.txt'
DEFAULT_PAGERANKS_FILE_NAME = 'user_pageranks.txt'
DEFAULT_COMBINED_USERS_FILE_NAME = 'combined_users.json'

DEFAULT_D3_GRAPH_FILE_NAME = 'users_graph.json'


def _raw_data_absolute_path(relative_path):
	"""Given the name of a raw data file, returns its absolute path."""
	return os.path.join(THIS_FILE_PATH, 'raw_data/' + relative_path)

def _processed_data_absolute_path(relative_path):
	"""Given the name of a processed data file, returns its absolute path."""
	return os.path.join(THIS_FILE_PATH, 'processed_data/' + relative_path)