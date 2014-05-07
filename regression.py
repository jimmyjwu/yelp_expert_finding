import numpy as np
from sklearn import linear_model

def prep_data(data):
    """
    input: list of dictionaries mapping attribute to value
    output: [list of feature_values, list of label_values, list of feature names]
    """
    samples = []
    labels = []
    feature_names = []
    for d in data:
        tmp = []
        for key, value in d.iteritems():
            if key == 'label':
                labels.append(value)
            else:
                tmp.append(value)
        samples.append(tmp)
        if len(feature_names) < 1:
            feature_names = [x[0] for x in d.iteritems()]
    feature_names.remove('label')
    return [samples, labels, feature_names]
        

def get_weights(data):
    """
    input: list of dictionaries mapping attribute to value
    output: dictionary of feature names to weight
    """
    lm = get_model(data)
    features = prep_data(data)[2]
    weights = {}
    coef =  list(lm.coef_)
    for n in range(len(features)):
        weights[features[n]] = coef[n]
    return weights

def get_model(data):
    """
    input: list of dictionaries mapping attribute to value
    output: sklearn.linear_model.base.LinearRegression
    """
    data = prep_data(data)
    lm = linear_model.LinearRegression()
    lm.fit(data[0], data[1])
    return lm

def predict(data, model):
    """
    input: dictionary of attribute values, linearRegression model
    output: predicted value
    """
    data = [v for _, v in data.iteritems()]
    return model.predict(data)

"""

tmp = [{'b':1, 'label':3, 'c':1}, {'b':2, 'c':2, 'label':6 }, {'c':1, 'label':5, 'b':3}]
print prep_data(tmp)

print get_weights(tmp)

print predict({'b':5, 'c':2}, get_model(tmp))

print predict({'c':2, 'b':5}, get_model(tmp))
"""
