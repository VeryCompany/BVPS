# -*- coding: utf-8 -*-

training_config = {
    "cap_nums":30
}
svm_param_grid = [
    {'C': [1, 10, 100, 1000],
     'kernel': ['linear']},
    {'C': [1, 10, 100, 1000],
     'gamma': [0.001, 0.0001],
     'kernel': ['rbf']}
]
