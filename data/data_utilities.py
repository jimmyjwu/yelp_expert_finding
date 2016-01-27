"""
Utilities specifically for the data processing scripts and data interfaces.
"""
import os

THIS_FILE_PATH = os.path.dirname(__file__)

DEFAULT_RAW_REVIEWS_FILE = 'yelp_academic_dataset_review.json'
DEFAULT_RAW_USERS_FILE = 'yelp_academic_dataset_user.json'

DEFAULT_REVIEW_LENGTHS_FILE = 'user_average_review_lengths.txt'
DEFAULT_READING_LEVELS_FILE = 'user_reading_levels.txt'
DEFAULT_COMBINED_USERS_FILE = 'combined_users.txt'


def _raw_data_absolute_path(relative_path):
	"""Given the name of a raw data file, returns its absolute path."""
	return os.path.join(THIS_FILE_PATH, 'raw_data/' + relative_path)

def _processed_data_absolute_path(relative_path):
	"""Given the name of a processed data file, returns its absolute path."""
	return os.path.join(THIS_FILE_PATH, 'processed_data/' + relative_path)