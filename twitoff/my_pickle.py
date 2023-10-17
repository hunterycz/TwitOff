# imports
import pickle

# use the sklearn library to load in iris dataset
# also LogisticRegression class
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
X, y = load_iris(return_X_y=True)
clf = LogisticRegression(random_state=42,
                         solver='lbfgs',
                         multi_class='multinomial').fit(X, y)

# use pickle .dumps function to save clf
clf_saved = pickle.dumps(clf)
# use pickle to save the test data for the prediction
X_test = X[:2, :]
X_test_saved = pickle.dumps(X_test)

if __name__ == "__main__":
    print(clf_saved)
