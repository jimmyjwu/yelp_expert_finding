"""
Primary file for analysis of the Yelp dataset.
"""
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.externals.six import StringIO
from sklearn.cross_validation import train_test_split, cross_val_score
import pydot

from utilities import *
from data.data_interface import *

from analysis_utilities import *


# Cache expensive file reads and computations
CACHE = {
	'users': None,
}



def train_elite_status_classifier(ModelClass, attributes, fraction_for_training, model_arguments={}):
	"""
	Given a constructor for a classifier object and a list of user attributes to use, trains,
	tests, and returns a classifier for Elite status.
	"""
	print '---------------------------------------------------------------------------------------'
	print 'STARTING LEARNING PIPELINE'
	print 'Model type: ' + ModelClass.__name__ + ' with arguments ' + str(model_arguments)
	print 'Features: ' + ', '.join(attributes)
	print 'Fraction of dataset for training: ' + format_as_percentage(fraction_for_training)
	print ''

	if CACHE['users']:
		print 'USERS LOADED FROM MEMORY'
		users = CACHE['users']
	else:
		print 'READING USERS FROM FILE'
		users = read_users()
		binarize_attribute(users, 'years_elite')
		designate_attribute_as_label(users, 'years_elite')
		CACHE['users'] = users

	# Ensure 50-50 split of positive and negative data, preventing a natural bias towards the 94% negative labels
	print 'TAKING STRATIFIED SAMPLE OF DATA'
	sampled_users = stratified_boolean_sample(users)
	random.shuffle(sampled_users)
	X, y = vectorize_users(sampled_users, attributes)

	print 'PARTITIONING DATA INTO TRAINING AND TEST'
	X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=fraction_for_training)
	# X_train, y_train, X_test, y_test, X_positive, y_positive = partition_data_vectors(X, y, fraction_for_training)

	print 'TRAINING CLASSIFIER'
	model = ModelClass(**model_arguments)
	model.fit(X_train, y_train)

	print ''
	print 'COMPUTING ACCURACY MEASURES'
	print 'Accuracy on test data: ', format_as_percentage( model.score(X_test, y_test) )
	print 'Accuracy on training data: ', format_as_percentage( model.score(X_train, y_train) )
	# print 'Recall of positive samples: ', format_as_percentage( model.score(X_positive, y_positive) )
	print ''

	return model



# Current best: training fraction=0.5, attributes=[review_count, average_stars, months_member, pagerank]
# Accuracy on test data: ~91%
# Accuracy on training data: ~91%
# Recall on positive samples: ~88%
FRACTION_FOR_TRAINING = 0.5
NAIVE_BAYES_USER_ATTRIBUTES = [
	'review_count',
	'average_stars',
	#'funny_vote_count',
	#'useful_vote_count',
	#'cool_vote_count',
	#'friend_count',
	'months_member',
	#'compliment_count',
	#'fan_count',
	#'average_review_length',
	#'average_reading_level',
	#'tip_count',
	'pagerank',
]
def train_naive_bayes_elite_status_classifier():
	"""Trains and tests a naive Bayes model for predicting users' Elite status."""
	model = train_elite_status_classifier(GaussianNB, NAIVE_BAYES_USER_ATTRIBUTES, FRACTION_FOR_TRAINING)



# Current best: training fraction=0.5, attributes=[review_count]
# Accuracy on test data: ~93%
# Accuracy on training data: ~93%
# Recall on positive samples: ~91.5%
LOGISTIC_REGRESSION_FRACTION_FOR_TRAINING = 0.5
LOGISTIC_REGRESSION_USER_ATTRIBUTES = [
	'review_count',
	#'average_stars',
	#'funny_vote_count',
	#'useful_vote_count',
	#'cool_vote_count',
	#'friend_count',
	#'months_member',
	#'compliment_count',
	#'fan_count',
	#'average_review_length',
	#'average_reading_level',
	#'tip_count',
	#'pagerank',
]
def train_logistic_regression_elite_status_classifier():
	"""Trains and tests a logistic regression model for predicting users' Elite status."""
	model = train_elite_status_classifier(LogisticRegression, LOGISTIC_REGRESSION_USER_ATTRIBUTES, LOGISTIC_REGRESSION_FRACTION_FOR_TRAINING)



# Current best: training fraction=0.8, attributes=[review_count], kernel='rbf' (default)
# Accuracy on test data: ~94.5%
# Accuracy on training data: ~94.5%
# Recall on positive samples: ~97.5%
SVM_FRACTION_FOR_TRAINING = 0.8
SVM_USER_ATTRIBUTES = [
	'review_count',
	#'average_stars',
	#'funny_vote_count',
	#'useful_vote_count',
	#'cool_vote_count',
	#'friend_count',
	#'months_member',
	#'compliment_count',
	#'fan_count',
	#'average_review_length',
	#'average_reading_level',
	#'tip_count',
	#'pagerank',
]
def train_SVM_elite_status_classifier():
	"""Trains and tests a support vector machine model for predicting users' Elite status."""
	model = train_elite_status_classifier(SVC, SVM_USER_ATTRIBUTES, SVM_FRACTION_FOR_TRAINING)



# Current best: training fraction=0.3, attributes=[review_count]
# Accuracy on test data: ~94.5%
# Accuracy on training data: 94.5%
# Recall on positive samples: ~97%
DECISION_TREE_FRACTION_FOR_TRAINING = 0.3
DECISION_TREE_USER_ATTRIBUTES = [
	'review_count',
	#'average_stars',
	#'funny_vote_count',
	#'useful_vote_count',
	#'cool_vote_count',
	#'friend_count',
	#'months_member',
	#'compliment_count',
	#'fan_count',
	#'average_review_length',
	#'average_reading_level',
	#'tip_count',
	#'pagerank',
]
def train_decision_tree_elite_status_classifier():
	"""Trains and tests a decision tree model for predicting users' Elite status."""
	model = train_elite_status_classifier(DecisionTreeClassifier, DECISION_TREE_USER_ATTRIBUTES, DECISION_TREE_FRACTION_FOR_TRAINING)

	# Output tree representation showing decision rules
	dot_data = StringIO()
	tree.export_graphviz(model, out_file=dot_data, class_names=True, filled=True)
	graph = pydot.graph_from_dot_data(dot_data.getvalue())
	graph.write_pdf('analysis/analysis_results/decision_tree.pdf')



# Current best: training fraction=0.8, attributes=[(all attributes)], n_estimators=100, max_depth=12
# Accuracy on test data: ~96%
# Accuracy on training data: ~98%
# Recall on positive samples: ~98%
RANDOM_FOREST_FRACTION_FOR_TRAINING = 0.8
RANDOM_FOREST_USER_ATTRIBUTES = [
	'review_count',
	'average_stars',
	'funny_vote_count',
	'useful_vote_count',
	'cool_vote_count',
	'friend_count',
	'months_member',
	'compliment_count',
	'fan_count',
	'average_review_length',
	'average_reading_level',
	'tip_count',
	'pagerank',
]
RANDOM_FOREST_ARGUMENTS = {
	'n_estimators': 100,
	'max_depth': 12,
}
def train_random_forest_elite_status_classifier():
	"""Trains and tests a random forest model for predicting users' Elite status."""
	model = train_elite_status_classifier(RandomForestClassifier, RANDOM_FOREST_USER_ATTRIBUTES, RANDOM_FOREST_FRACTION_FOR_TRAINING, model_arguments=RANDOM_FOREST_ARGUMENTS)

	# Print features and importances side-by-side
	for importance, attribute in sorted(zip(model.feature_importances_, RANDOM_FOREST_USER_ATTRIBUTES)):
		print attribute, '\t', format_as_percentage(importance)



# Current best: training fraction=0.8, attributes=[(all attributes)], n_estimators=100, learning_rate=1.0
# Accuracy on test data: ~96%
# Accuracy on training data: ~96%
# Recall on positive samples: ~97.5%
ADABOOST_FRACTION_FOR_TRAINING = 0.8
ADABOOST_USER_ATTRIBUTES = [
	'review_count',
	'average_stars',
	'funny_vote_count',
	'useful_vote_count',
	'cool_vote_count',
	'friend_count',
	'months_member',
	'compliment_count',
	'fan_count',
	'average_review_length',
	'average_reading_level',
	'tip_count',
	'pagerank',
]
ADABOOST_ARGUMENTS = {
	'n_estimators': 100
}
def train_adaboost_elite_status_classifier():
	"""Trains and tests an AdaBoost (boosted decision trees) model for predicting users' Elite status."""
	model = train_elite_status_classifier(AdaBoostClassifier, ADABOOST_USER_ATTRIBUTES, ADABOOST_FRACTION_FOR_TRAINING, model_arguments=ADABOOST_ARGUMENTS)



def classify_by_review_count(minimum_reviews_for_elite=48):
	""" Classifies solely by the number of reviews. """
	if CACHE['users']:
		print 'USERS LOADED FROM MEMORY'
		users = CACHE['users']
	else:
		print 'READING USERS FROM FILE'
		users = read_users()
		booleanize_attribute(users, 'years_elite')
		designate_attribute_as_label(users, 'years_elite')
		CACHE['users'] = users

	predicted_positives = [user for user in users if user['review_count'] >= minimum_reviews_for_elite]
	predicted_negatives = [user for user in users if user['review_count'] < minimum_reviews_for_elite]

	correct_predictions = len([user for user in predicted_positives if user['label'] == 1] + [user for user in predicted_negatives if user['label'] == 0])
	print 'Accuracy: ', format_as_percentage( float(correct_predictions) / len(users) )

	recalled_positives = [user for user in predicted_positives if user['label'] == 1]
	all_positives = [user for user in users if user['label'] == 1]
	print 'Recall: ', format_as_percentage( float(len(recalled_positives)) / len(all_positives) )



if __name__ == "__main__":
	train_decision_tree_elite_status_classifier()


