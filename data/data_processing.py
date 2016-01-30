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
import json

from utilities import *
from readability.readability import Readability

from data_utilities import *
from data_interface import *


def extract_user_average_review_lengths(input_file_name=DEFAULT_RAW_REVIEWS_FILE_NAME, output_file_name=DEFAULT_REVIEW_LENGTHS_FILE_NAME):
	"""
	Given a Yelp dataset reviews file, builds a file:
		user_1_ID user_1_average_review_length
			.
			.
			.
		user_N_ID user_N_average_review_length
	"""
	# Maps each user ID --> [running sum of review lengths, running number of reviews]
	total_review_length_and_count_for_user = defaultdict(lambda: [0,0])

	# Compute the above mapping
	with open(_raw_data_absolute_path(input_file_name)) as reviews_file:
		
		for review_JSON in reviews_file:
			review = json.loads(review_JSON)
			total_review_length_and_count_for_user[review['user_id']][0] += len(review['text'].split())
			total_review_length_and_count_for_user[review['user_id']][1] += 1

	# Compute each user's average review length (truncated to an integer)
	average_review_length_for_user = { user_ID: (total_review_length / review_count if review_count > 0 else 0) for user_ID, [total_review_length, review_count] in total_review_length_and_count_for_user.iteritems() }

	_write_single_user_attribute(average_review_length_for_user, output_file_name)


def extract_user_reading_levels(input_file_name=DEFAULT_RAW_REVIEWS_FILE_NAME, output_file_name=DEFAULT_READING_LEVELS_FILE_NAME, reviews_to_analyze_per_user=float('inf')):
	"""
	Given a Yelp dataset reviews file, builds a file:
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
	with open(_raw_data_absolute_path(input_file_name)) as reviews_file:
		
		for review_JSON in reviews_file:
			review = json.loads(review_JSON)

			# Skip reviews from users who we have analyzed to the maximum desired
			if total_reading_level_and_review_count_for_user[review['user_id']][1] >= reviews_to_analyze_per_user:
				continue

			# TODO: Try other reading level metrics
			try:
				total_reading_level_and_review_count_for_user[review['user_id']][0] += Readability(review['text']).SMOGIndex()
				total_reading_level_and_review_count_for_user[review['user_id']][1] += 1
			except UnicodeEncodeError as error:
				pass

	# Compute each user's average reading level
	average_reading_level_for_user = { user_ID: float(total_reading_level) / review_count for user_ID, [total_reading_level, review_count] in total_reading_level_and_review_count_for_user.iteritems() }

	_write_single_user_attribute(average_reading_level_for_user, output_file_name)


def extract_user_tip_counts(input_file_name=DEFAULT_RAW_TIPS_FILE_NAME, output_file_name=DEFAULT_TIP_COUNTS_FILE_NAME):
	"""
	Given a Yelp dataset tips file, builds a file:
		user_1_ID user_1_tip_count
			.
			.
			.
		user_N_ID user_N_tip_count
	"""
	# Maps each user ID --> number of tips written by that user
	tip_count_for_user = Counter()

	with open(_raw_data_absolute_path(input_file_name)) as tips_file:

		for tip_JSON in tips_file:
			tip = json.loads(tip_JSON)
			tip_count_for_user[tip['user_id']] += 1

	_write_single_user_attribute(tip_count_for_user, output_file_name)


def extract_user_pageranks(input_file_name=DEFAULT_RAW_USERS_FILE_NAME, output_file_name=DEFAULT_PAGERANKS_FILE_NAME):
	"""
	Given a Yelp dataset users file, builds a file:
		user_1_ID user_1_pagerank
			.
			.
			.
		user_N_ID user_N_pagerank
	"""
	graph = read_user_graph(input_file_name)
	pagerank_for_user = networkx.pagerank(graph)
	
	_write_single_user_attribute(pagerank_for_user, output_file_name)


def extract_user_basic_attributes(input_file_name=DEFAULT_RAW_USERS_FILE_NAME, output_file_name=DEFAULT_BASIC_ATTRIBUTES_FILE_NAME):
	"""
	Given a Yelp dataset users file, builds a file:
		user_1_ID user_1_review_count ... user_1_fan_count
			.
			.
			.
		user_N_ID user_N_review_count ... user_N_fan_count
	"""
	users = []

	with open(_raw_data_absolute_path(input_file_name)) as raw_users_file:

		for user_line in raw_users_file:
			raw_user = json.loads(user_line)
			user = { attribute_name: extract_attribute_value(raw_user) for attribute_name, extract_attribute_value in BASIC_USER_ATTRIBUTES_AND_EXTRACTORS }
			users += [user]

	_write_multiple_user_attributes(users, BASIC_USER_ATTRIBUTES, output_file_name)


def combine_all_user_data(
	input_basic_attributes_file_name=DEFAULT_BASIC_ATTRIBUTES_FILE_NAME,
	input_review_lengths_file_name=DEFAULT_REVIEW_LENGTHS_FILE_NAME,
	input_reading_levels_file_name=DEFAULT_READING_LEVELS_FILE_NAME,
	input_tip_counts_file_name=DEFAULT_TIP_COUNTS_FILE_NAME,
	input_pageranks_file_name=DEFAULT_PAGERANKS_FILE_NAME,
	output_users_file_name=DEFAULT_COMBINED_USERS_FILE_NAME,
):
	"""
	Given all processed data on users, combines them into a single file formatted as follows:
		ID review_count ... pagerank
		user_1_ID user_1_review_count ... user_1_pagerank
			.
			.
			.
		user_N_ID user_N_review_count ... user_N_pagerank
	"""
	# Read in basic user attributes
	user_for_ID = { user['ID']: user for user in read_user_basic_attributes(input_file_name=input_basic_attributes_file_name) }

	# Read in average review lengths
	for user_ID, average_review_length in read_user_average_review_lengths(input_file_name=input_review_lengths_file_name).iteritems():
		user_for_ID[user_ID]['average_review_length'] = average_review_length

	# Read in average reading levels
	for user_ID, average_reading_level in read_user_average_reading_levels(input_file_name=input_reading_levels_file_name).iteritems():
		user_for_ID[user_ID]['average_reading_level'] = average_reading_level

	# Read in tip counts
	for user_ID, tip_count in read_user_tip_counts(input_file_name=input_tip_counts_file_name).iteritems():
		user_for_ID[user_ID]['tip_count'] = tip_count

	# Read in PageRanks
	for user_ID, pagerank in read_user_pageranks(input_file_name=input_pageranks_file_name).iteritems():
		user_for_ID[user_ID]['pagerank'] = pagerank

	_write_multiple_user_attributes(user_for_ID.itervalues(), ALL_USER_ATTRIBUTES, output_users_file_name)





