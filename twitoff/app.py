from re import DEBUG
from .models import DB, User, Tweet
from flask import Flask, render_template, request
from .twitter import add_or_update_user
from .predict import predict_user
import pickle


def create_app():
    app = Flask(__name__)

    # database configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # regiser our databases with the app
    DB.init_app(app)

    @app.route('/')
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

    @app.route('/reset')
    def reset():
        # Drop all database tables
        DB.drop_all()
        # Recreate all database tables according to the
        # indicated schema in models.py
        DB.create_all()
        return '''The database has been reset. 
        <a href='/'>Go to Home</a>
        <a href='/reset'>Go to reset</a>
        <a href='/populate'>Go to populate</a>'''

    # @app.route('/populate')
    # def populate():
    #     # create 2 fake users in the db
    #     add_or_update_user('Austen')
    #     add_or_update_user('elonmusk')
    #     add_or_update_user('NASA')

    #     return '''Created some users.
    #     <a href='/'>Go to Home</a>
    #     <a href='/reset'>Go to reset</a>
    #     <a href='/populate'>Go to populate</a>'''

    @app.route('/update')
    def update():
        # get list of usernames of all users
        users = User.query.all()
        usernames = [user.username for user in users]

        for username in usernames:
            add_or_update_user(username)

        return render_template('base.html', title="Users Updated")

    @app.route('/iris')
    def iris():
        from sklearn.datasets import load_iris
        from sklearn.linear_model import LogisticRegression
        X, y = load_iris(return_X_y=True)
        clf = LogisticRegression(random_state=42,
                                 solver='lbfgs',
                                 multi_class='multinomial').fit(X, y)

        return str(clf.predict(X[:2, :]))

    @app.route('/user', methods=['POST'])
    @app.route('/user/<username>', methods=['GET'])
    def user(username=None, message=''):
        username = username or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(username)
                message = f'User {username} has been successfully added!'

            tweets = User.query.filter(User.username == username).one().tweets
        except Exception as e:
            message = f'Error adding {username}: {e}'
            tweets = []

        return render_template('user.html',
                               title=username,
                               tweets=tweets,
                               message=message)

    @app.route('/compare', methods=['POST'])
    def compare():
        user0, user1 = sorted[request.values['user0'], request.values['user1']]
        hypo_tweet_text = request.values['tweet_text']

        if user0 == user1:
            message = 'Cannot compare a user to themselves!'
        else:
            prediction = predict_user(user0, user1, hypo_tweet_text)

            # get into the if statement if the prediction is user1
            if prediction:
                message = f'"{hypo_tweet_text}" is more likely to be said by {user1} than by {user0}'
            else:
                message = f'"{hypo_tweet_text}" is more likely to be said by {user0} than by {user1}'

        return render_template('prediction.html',
                               title='Prediction',
                               message=message)


    @app.route('/newiris')
    def new_iris():
        from .my_pickle import clf_saved, X_test_saved

        clf = pickle.loads(clf_saved)
        X = pickle.loads(X_test_saved)

        return str(clf.predict(X[:2, :]))

    @app.route('/score')
    def score():
        from sklearn.datasets import load_iris
        from sklearn.linear_model import LogisticRegression
        X, y = load_iris(return_X_y=True)
        clf = LogisticRegression(random_state=42, solver='lbfgs',
                                 multi_class='multinomial').fit(X, y)

        return str(clf.score(X, y))

    return app
