"""
Utilities for the following:

    +-----------+        +---- THIS FILE -----+
    | raw_data/ | -----> | cleaning           |        +-----------------+
    +-----------+        | reorganizing       | -----> | processed_data/ |
                    +--> | feature extraction |        +-----------------+
                    |    +--------------------+                 |
                    |                                           |
                    +-------------------------------------------+
"""
from utilities import *
from data_utilities import *
from data_interface import *


def extract_user_average_review_lengths(input_file_name=DEFAULT_RAW_REVIEWS_FILE_NAME, output_file_name=DEFAULT_REVIEW_LENGTHS_FILE_NAME):
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

	# Compute each user's average review length
	average_review_length_for_user = { user_ID: float(total_review_length) / review_count for user_ID, [total_review_length, review_count] in total_review_length_and_count_for_user.iteritems() }

	_write_single_user_attribute(average_review_length_for_user, output_file_name)


def extract_user_reading_levels(input_file_name=DEFAULT_RAW_REVIEWS_FILE_NAME, output_file_name=DEFAULT_READING_LEVELS_FILE_NAME, reviews_to_analyze_per_user=float('inf')):
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

	# Compute each user's average reading level
	average_reading_level_for_user = { user_ID: float(total_reading_level) / review_count for user_ID, [total_reading_level, review_count] in total_reading_level_and_review_count_for_user.iteritems() }

	_write_single_user_attribute(average_reading_level_for_user, output_file_name)


def extract_user_pageranks(input_file_name=DEFAULT_RAW_USERS_FILE_NAME, output_file_name=DEFAULT_PAGERANKS_FILE_NAME):
	"""
	Given a Yelp dataset users file (with users in JSON format), builds a file:
		user_1_ID user_1_pagerank
			.
			.
			.
		user_N_ID user_N_pagerank
	"""
	graph = read_user_graph(input_file_name)
	pagerank_for_user = networkx.pagerank(graph)
	
	_write_single_user_attribute(pagerank_for_user, output_file_name)


def combine_all_user_data(
	input_users_file_name=DEFAULT_RAW_USERS_FILE_NAME,
	input_review_lengths_file_name=DEFAULT_REVIEW_LENGTHS_FILE_NAME,
	input_reading_levels_file_name=DEFAULT_READING_LEVELS_FILE_NAME,
	input_pageranks_file_name=DEFAULT_PAGERANKS_FILE_NAME,
	output_users_file_name=DEFAULT_COMBINED_USERS_FILE_NAME,
):
	"""
	Given all data on users (both raw and processed), combines them into a single file formatted as follows:
		ID review_count ... pagerank
		user_1_ID user_1_review_count ... user_1_pagerank
			.
			.
			.
		user_N_ID user_N_review_count ... user_N_pagerank
	"""
	# TODO: Check if there are more features provided by the Yelp dataset that are not being added

	user_for_ID = {}

	# Read in basic user attributes
	with open(_raw_data_absolute_path(input_users_file_name)) as users_file:

		for user_line in users_file:
			raw_user = json.loads(user_line)
			user = {
				'ID': raw_user['user_id'],
				'review_count': raw_user['review_count'],
				'average_stars': raw_user['average_stars'],
				'friend_count': len(raw_user['friends']),
				'months_member': 12 * (CURRENT_YEAR - int(raw_user['yelping_since'].split('-')[0]) - 1) + (12 - int(raw_user['yelping_since'].split('-')[1])) + 5,
				'years_elite': len(raw_user['elite']),
				'fan_count': raw_user['fans'],
				'funny_vote_count': raw_user['votes']['funny']
				'useful_vote_count': raw_user['votes']['useful']
				'cool_vote_count': raw_user['votes']['cool']
			}
			user_for_ID[user['ID']] = user

	# Read in average review lengths
	for user_ID, average_review_length in read_user_average_review_lengths(input_file_name=input_review_lengths_file_name).iteritems():
		user_for_ID[user_ID]['average_review_length'] = average_review_length

	# Read in average reading levels
	for user_ID, average_reading_level in read_user_average_reading_levels(input_file_name=input_reading_levels_file_name).iteritems():
		user_for_ID[user_ID]['average_reading_level'] = average_reading_level

	# Read in PageRanks
	for user_ID, pagerank in read_user_pageranks(input_file_name=input_pageranks_file_name).iteritems():
		user_for_ID[user_ID]['pagerank'] = pagerank

	# Write combined user data to file
	with open(_processed_data_absolute_path(output_users_file_name), 'w') as combined_users_file: # Write mode; overwrite old file if it exists

		# Row 1: attribute names
		combined_users_file.write( ' '.join(ALL_USER_ATTRIBUTES) + '\n')

		# Rows 2,...,N: users' attribute values written in the same order
		for user in user_for_ID.itervalues():
			combined_users_file.write( ' '.join([str(user[attribute]) for attribute in ALL_USER_ATTRIBUTES]) + '\n')





