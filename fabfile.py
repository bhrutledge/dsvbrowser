import fabric.api as f


def test():
    f.local('python -m unittest discover')


def lint():
    f.local('flake8 .')
    f.local('pylint --rcfile=.pylintrc dsvbrowser tests fabfile run')
