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
from sklearn.cross_validation import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import confusion_matrix, classification_report
import pydot

from utilities import *
from data.data_interface import *

from analysis_utilities import *


# Cache expensive file reads and computations
CACHE = {
	'training_set': None,
	'test_set': None,
}

def load_training_set():
	"""Loads training set from the cache if possible, or from the training set file."""
	if not CACHE['training_set']:
		CACHE['training_set'] = read_training_set()
	return CACHE['training_set']

def load_test_set():
	"""Loads test set from the cache if possible, or from the test set file."""
	if not CACHE['test_set']:
		CACHE['test_set'] = read_test_set()
	return CACHE['test_set']



def train_and_validate_elite_status_classifier(ModelClass, attributes, model_arguments={}):
	"""
	Given a constructor for a classifier object and a list of user attributes to use,
		- Trains a classifier (using part of the training dataset)
		- Validates the classifier (using another part of the training dataset)
	"""
	print '---------------------------------------------------------------------------------------'
	print 'STARTING LEARNING PIPELINE'
	print 'Model type: ' + ModelClass.__name__ + ' with arguments ' + str(model_arguments)
	print 'Features: ' + ', '.join(attributes)
	print ''

	print 'LOADING TRAINING SET'
	users = load_training_set()

	print 'PREPARING DATA'
	users = balanced_sample(users)
	X, y = vectorize_users(users, attributes)

	print 'BUILDING CLASSIFIER MODEL'
	model = ModelClass(**model_arguments)

	# k-fold cross-validation: uses all data for training and validation
	# Stratification: prevents bias towards either class
	print 'PERFORMING STRATIFIED K-FOLD CROSS-VALIDATION'
	combined_confusion_matrix = numpy.zeros((2,2), dtype=numpy.int)
	combined_y_test = []
	combined_y_predict = []
	for train_indices, test_indices in StratifiedKFold(y, n_folds=5):
		X_train, X_test = X[train_indices], X[test_indices]
		y_train, y_test = y[train_indices], y[test_indices]
		model.fit(X_train, y_train)
		y_predict = model.predict(X_test)
		combined_confusion_matrix += confusion_matrix(y_test, y_predict, labels=[0,1])
		combined_y_test.extend(y_test)
		combined_y_predict.extend(y_predict)


	print 'COMPUTING ACCURACY MEASURES'
	print '\nConfusion Matrix (C_ij = # samples in class i but predicted j)'
	print combined_confusion_matrix
	print '\nClassification Report'
	print classification_report(combined_y_test, combined_y_predict, labels=[1,0], target_names=['Elite', 'Non-Elite'], digits=3)


def test_elite_status_classifier(ModelClass, attributes, model_arguments={}, balance_training_set=True, balance_test_set=True):
	"""
	Given a constructor for a classifier object and a list of user attributes to use,
		- Trains a classifier (using the full training dataset)
		- Tests the classifier (using test data)
	and returns the classifier for Elite status.
	"""
	print '---------------------------------------------------------------------------------------'
	print 'STARTING LEARNING PIPELINE'
	print 'Model type: ' + ModelClass.__name__ + ' with arguments ' + str(model_arguments)
	print 'Features: ' + ', '.join(attributes)
	print ''

	print 'LOADING TRAINING SET (WITH ' + ('UN' if not balance_training_set else '') + 'BALANCED CLASSES)'
	training_users = load_training_set()
	if balance_training_set:
		training_users = balanced_sample(training_users)
	X_train, y_train = vectorize_users(training_users, attributes)

	print 'TRAINING CLASSIFIER MODEL'
	model = ModelClass(**model_arguments)
	model.fit(X_train, y_train)

	print 'LOADING TEST SET (WITH ' + ('UN' if not balance_test_set else '') + 'BALANCED CLASSES)'
	test_users = load_test_set()
	if balance_test_set:
		test_users = balanced_sample(test_users)
	X_test, y_test = vectorize_users(test_users, attributes)

	print 'TESTING ON TEST SET'
	y_predict = model.predict(X_test)
	print '\nConfusion matrix (C_ij = # samples in class i but predicted j):'
	print confusion_matrix(y_test, y_predict, labels=[0,1])
	print '\nClassification report:'
	print classification_report(y_test, y_predict, labels=[1,0], target_names=['Elite', 'Non-Elite'], digits=3)

	return model



# Current best: attributes=[review_count, average_stars, months_member, pagerank]
# Accuracy on test data: ~91%
# Accuracy on training data: ~91%
# Recall on positive samples: ~88%
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
	"""Trains and validates a naive Bayes model for predicting users' Elite status."""
	model = train_and_validate_elite_status_classifier(GaussianNB, NAIVE_BAYES_USER_ATTRIBUTES)



# Current best: attributes=[review_count]
# Accuracy on test data: ~93%
# Accuracy on training data: ~93%
# Recall on positive samples: ~91.5%
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
	"""Trains and validates a logistic regression model for predicting users' Elite status."""
	model = train_and_validate_elite_status_classifier(LogisticRegression, LOGISTIC_REGRESSION_USER_ATTRIBUTES)



# Current best: attributes=[review_count], kernel='rbf' (default)
# Accuracy on test data: ~94.5%
# Accuracy on training data: ~94.5%
# Recall on positive samples: ~97.5%
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
	"""Trains and validates a support vector machine model for predicting users' Elite status."""
	model = train_and_validate_elite_status_classifier(SVC, SVM_USER_ATTRIBUTES)



# Current best: attributes=[review_count]
# Accuracy on test data: ~94.5%
# Accuracy on training data: 94.5%
# Recall on positive samples: ~97%
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
	"""Trains and validates a decision tree model for predicting users' Elite status."""
	model = train_and_validate_elite_status_classifier(DecisionTreeClassifier, DECISION_TREE_USER_ATTRIBUTES)

	# Output tree representation showing decision rules
	dot_data = StringIO()
	tree.export_graphviz(model, out_file=dot_data, class_names=True, filled=True)
	graph = pydot.graph_from_dot_data(dot_data.getvalue())
	graph.write_pdf('analysis/analysis_results/decision_tree.pdf')



# Current best: attributes=[(all attributes)], n_estimators=100, max_depth=12
# Accuracy on test data: ~96%
# Accuracy on training data: ~98%
# Recall on positive samples: ~98%
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
	"""Trains and validates a random forest model for predicting users' Elite status."""
	model = train_and_validate_elite_status_classifier(RandomForestClassifier, RANDOM_FOREST_USER_ATTRIBUTES, model_arguments=RANDOM_FOREST_ARGUMENTS)
	show_feature_importances(model, RANDOM_FOREST_USER_ATTRIBUTES)



# Current best: attributes=[(all attributes)], n_estimators=100, learning_rate=1.0
# Accuracy on test data: ~96%
# Accuracy on training data: ~96%
# Recall on positive samples: ~97.5%
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
	"""Trains and validates an AdaBoost (boosted decision trees) model for predicting users' Elite status."""
	model = train_and_validate_elite_status_classifier(AdaBoostClassifier, ADABOOST_USER_ATTRIBUTES, model_arguments=ADABOOST_ARGUMENTS)



def classify_by_review_count(minimum_reviews_for_elite=48):
	""" Classifies solely by the number of reviews. """
	users = load_training_set()

	predicted_positives = [user for user in users if user['review_count'] >= minimum_reviews_for_elite]
	predicted_negatives = [user for user in users if user['review_count'] < minimum_reviews_for_elite]

	correct_predictions = len([user for user in predicted_positives if user['label'] == 1] + [user for user in predicted_negatives if user['label'] == 0])
	print 'Accuracy: ', format_as_percentage( float(correct_predictions) / len(users) )

	recalled_positives = [user for user in predicted_positives if user['label'] == 1]
	all_positives = [user for user in users if user['label'] == 1]
	print 'Recall: ', format_as_percentage( float(len(recalled_positives)) / len(all_positives) )



if __name__ == "__main__":
	train_decision_tree_elite_status_classifier()


