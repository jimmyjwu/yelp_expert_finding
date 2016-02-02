"""
Primary file for analysis of the Yelp dataset.
"""
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

from utilities import *
from data.data_interface import *

from analysis_utilities import *


# TODO: Try decision trees/random forests
# TODO: Refactor functions for training/classifying using different ML models


def predict_elite_status_with_naive_bayes():
	"""Trains and tests a naive Bayes model for predicting users' Elite status."""
	# Hyperparameters
	FRACTION_FOR_TRAINING = 0.7
	NAIVE_BAYES_USER_ATTRIBUTES = [
		#'ID',
		'review_count',
		'average_stars',
		#'funny_vote_count',
		#'useful_vote_count',
		#'cool_vote_count',
		#'friend_count',
		'years_elite',
		'months_member',
		#'compliment_count',
		#'fan_count',
		#'average_review_length',
		#'average_reading_level',
		#'tip_count',
		'pagerank',
	]

	print 'READING USERS FROM FILE'
	users = read_users(attributes=NAIVE_BAYES_USER_ATTRIBUTES)
	users = remove_attribute(users, 'ID')
	users = make_attribute_boolean(users, 'years_elite')
	users = designate_attribute_as_label(users, 'years_elite')

	# Ensure 50-50 split of positive and negative data, preventing a natural bias towards the 94% negative labels
	print 'TAKING STRATIFIED SAMPLE OF DATA'
	users = stratified_boolean_sample(users)
	random.shuffle(users)
	user_vectors, labels = vectorize_users(users)

	print 'PARTITIONING DATA INTO TRAINING AND TEST'
	training_set, training_set_labels, test_set, test_set_labels, positive_test_set, positive_test_set_labels = partition_data_vectors(user_vectors, labels, FRACTION_FOR_TRAINING)

	# Train naive Bayes model
	naive_bayes_model = GaussianNB()
	naive_bayes_model.fit(training_set, training_set_labels)

	# Compute accuracy measures
	print 'Accuracy on test data: ', format_as_percentage( naive_bayes_model.score(test_set, test_set_labels) )
	print 'Accuracy on training data: ', format_as_percentage( naive_bayes_model.score(training_set, training_set_labels) )
	print 'Recall of positive samples: ', format_as_percentage( naive_bayes_model.score(positive_test_set, positive_test_set_labels) )
	print 'Class prior distribution (should be roughly even): ', naive_bayes_model.class_prior_


def predict_elite_status_with_logistic_regression():
	"""Trains and tests a logistic regression model for predicting users' Elite status."""
	# Hyperparameters
	FRACTION_FOR_TRAINING = 0.7
	LOGISTIC_REGRESSION_USER_ATTRIBUTES = [
		#'ID',
		'review_count',
		#'average_stars',
		#'funny_vote_count',
		#'useful_vote_count',
		#'cool_vote_count',
		#'friend_count',
		'years_elite',
		#'months_member',
		#'compliment_count',
		#'fan_count',
		#'average_review_length',
		#'average_reading_level',
		#'tip_count',
		#'pagerank',
	]

	print 'READING USERS FROM FILE'
	users = read_users(attributes=LOGISTIC_REGRESSION_USER_ATTRIBUTES)
	users = remove_attribute(users, 'ID')
	users = make_attribute_boolean(users, 'years_elite')
	users = designate_attribute_as_label(users, 'years_elite')

	# Ensure 50-50 split of positive and negative data, preventing a natural bias towards the 94% negative labels
	print 'TAKING STRATIFIED SAMPLE OF DATA'
	users = stratified_boolean_sample(users)
	random.shuffle(users)
	user_vectors, labels = vectorize_users(users)

	print 'PARTITIONING DATA INTO TRAINING AND TEST'
	training_set, training_set_labels, test_set, test_set_labels, positive_test_set, positive_test_set_labels = partition_data_vectors(user_vectors, labels, FRACTION_FOR_TRAINING)

	# Train logistic regression model
	logistic_regression_model = LogisticRegression()
	logistic_regression_model.fit(training_set, training_set_labels)

	# Compute accuracy measures
	print 'Accuracy on test data: ', format_as_percentage( logistic_regression_model.score(test_set, test_set_labels) )
	print 'Accuracy on training data: ', format_as_percentage( logistic_regression_model.score(training_set, training_set_labels) )
	print 'Recall of positive samples: ', format_as_percentage( logistic_regression_model.score(positive_test_set, positive_test_set_labels) )


def predict_elite_status_with_decision_tree():
	"""Trains and tests a decision tree model for predicting users' Elite status."""
	# Hyperparameters
	FRACTION_FOR_TRAINING = 0.7
	DECISION_TREE_USER_ATTRIBUTES = [
		#'ID',
		'review_count',
		#'average_stars',
		#'funny_vote_count',
		#'useful_vote_count',
		#'cool_vote_count',
		#'friend_count',
		'years_elite',
		#'months_member',
		#'compliment_count',
		#'fan_count',
		#'average_review_length',
		#'average_reading_level',
		#'tip_count',
		#'pagerank',
	]

	print 'READING USERS FROM FILE'
	users = read_users(attributes=DECISION_TREE_USER_ATTRIBUTES)
	users = remove_attribute(users, 'ID')
	users = make_attribute_boolean(users, 'years_elite')
	users = designate_attribute_as_label(users, 'years_elite')

	# Ensure 50-50 split of positive and negative data, preventing a natural bias towards the 94% negative labels
	print 'TAKING STRATIFIED SAMPLE OF DATA'
	users = stratified_boolean_sample(users)
	random.shuffle(users)
	user_vectors, labels = vectorize_users(users)

	print 'PARTITIONING DATA INTO TRAINING AND TEST'
	training_set, training_set_labels, test_set, test_set_labels, positive_test_set, positive_test_set_labels = partition_data_vectors(user_vectors, labels, FRACTION_FOR_TRAINING)

	# Train decision tree model
	decision_tree_model = DecisionTreeClassifier()
	decision_tree_model.fit(training_set, training_set_labels)

	# Compute accuracy measures
	print 'Accuracy on test data: ', format_as_percentage( decision_tree_model.score(test_set, test_set_labels) )
	print 'Accuracy on training data: ', format_as_percentage( decision_tree_model.score(training_set, training_set_labels) )
	print 'Recall of positive samples: ', format_as_percentage( decision_tree_model.score(positive_test_set, positive_test_set_labels) )






if __name__ == "__main__":
	predict_elite_status_with_decision_tree()


