import numpy as np
from sklearn import linear_model

def prep_data(data):
    """
    input: list of dictionaries

    output: (list of data, list of feature names)
    """
    samples = []
    feature_names = []
    for d in data:
        samples.append([x[1] for x in d.iteritems()])
        if len(feature_names) < 1:
            feature_names = [x[0] for x in d.iteritems()]
    return (samples, feature_names)
        

def get_weights(data):
    """
    input: tuple (list of data, list of feature names)
    output: dictionary of feature names to weight
    """
    lm = linear_model.LinearRegression()
    lm.fit(data[0], [_ for _ in range(len(data[1]))])
    features = data[1]
    weights = {}
    for n in range(len(features)):
        weights[features[n]] = lm.coef_[n]
    return weights

"""
tmp = [{'a':2, 'b':4, 'c':5}, {'b':1, 'c':7, 'a':2}, {'c':4, 'a':2, 'b':5}]
print prep_data(tmp)

print get_weights(prep_data(tmp))
"""
