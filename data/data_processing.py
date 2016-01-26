"""
Utilities for the following:

	+-----------+        cleaning                 +-----------------+
	| raw_data/ | ------ reorganizing      -----> | processed_data/ |
	+-----------+        feature extraction       +-----------------+
"""
import os

from utilities import *

THIS_FILE_PATH = os.path.dirname(__file__)

def _raw_data_absolute_path(relative_path):
	"""Given the name of a raw data file, returns its absolute path."""
	return os.path.join(THIS_FILE_PATH, 'raw_data/' + relative_path)

def _processed_data_absolute_path(relative_path):
	"""Given the name of a processed data file, returns its absolute path."""
	return os.path.join(THIS_FILE_PATH, 'processed_data/' + relative_path)


def extract_user_average_review_lengths(input_file_name='yelp_academic_dataset_review.json', output_file_name='user_average_review_lengths.txt'):
	"""
	Given a Yelp dataset reviews file (with reviews in JSON format), builds
	a file:
		user_1_ID user_1_average_review_length
			.
			.
			.
		user_N_ID user_N_average_review_length
	"""
	# Maps each user ID --> [running sum of review lengths, running number of reviews]
	total_review_length_and_count_for_user = defaultdict(lambda: [0,0])

	# Compute the above mapping
	with open(_raw_data_absolute_path(input_file_name)) as reviews_file: # Read mode (default)
		
		for review_JSON in reviews_file:
			review = json.loads(review_JSON)
			total_review_length_and_count_for_user[review['user_id']][0] += len(review['text'].split())
			total_review_length_and_count_for_user[review['user_id']][1] += 1


	# Write each user's average review length to file
	with open(_processed_data_absolute_path(output_file_name), 'w') as user_review_lengths_file: # Write mode; overwrite old file if it exists
		
		for user_ID, [total_review_length, review_count] in total_review_length_and_count_for_user.iteritems():
			user_review_lengths_file.write(user_ID + ' ' + str( float(total_review_length) / review_count ) + '\n')


