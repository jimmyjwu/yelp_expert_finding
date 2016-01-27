"""
Utilities for the following:

    +-----------+        +--------------------+
    | raw_data/ | -----> | cleaning           |        +-----------------+
    +-----------+        | reorganizing       | -----> | processed_data/ |
                    +--> | feature extraction |        +-----------------+
                    |    +--------------------+                 |
                    |                                           |
                    +-------------------------------------------+
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
	Given a Yelp dataset reviews file (with reviews in JSON format), builds a file:
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


def extract_user_reading_levels(input_file_name='yelp_academic_dataset_review.json', output_file_name='user_reading_levels.txt', reviews_to_analyze_per_user=float('inf')):
	"""
	Given a Yelp dataset reviews file (with reviews in JSON format), builds a file:
		user_1_ID user_1_reading_level
			.
			.
			.
		user_N_ID user_N_reading_level

	WARNING: This function is computationally expensive. The amount of computation can be limited
	by setting reviews_to_analyze_per_user, the maximum number of reviews to analyze per user.
	On a 2011 MacBook Air, 1000 reviews take 2-3 seconds to analyze.
	"""
	# Maps each user ID --> [running sum of review reading levels, running number of reviews]
	total_reading_level_and_review_count_for_user = defaultdict(lambda: [0,0])

	# Compute the above mapping
	with open(_raw_data_absolute_path(input_file_name)) as reviews_file: # Read mode (default)
		
		for review_JSON in reviews_file:
			review = json.loads(review_JSON)

			# Skip reviews from users who we have analyzed to the maximum desired
			if total_reading_level_and_review_count_for_user[review['user_id']][1] >= reviews_to_analyze_per_user:
				continue

			try:
				total_reading_level_and_review_count_for_user[review['user_id']][0] += Readability(review['text']).SMOGIndex() # Can be replaced with other text metrics
				total_reading_level_and_review_count_for_user[review['user_id']][1] += 1
			except UnicodeEncodeError as error:
				pass


	# Write each user's average review reading level to file
	with open(_processed_data_absolute_path(output_file_name), 'w') as user_reading_levels_file: # Write mode; overwrite old file if it exists
		
		for user_ID, [total_reading_level, review_count] in total_reading_level_and_review_count_for_user.iteritems():
			user_reading_levels_file.write(user_ID + ' ' + str( float(total_reading_level) / review_count ) + '\n')



