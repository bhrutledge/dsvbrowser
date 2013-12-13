import fabric.api as f


def test():
    f.local('python -m unittest discover')


def lint():
    f.local('flake8 .')
    f.local('pylint --rcfile=.pylintrc dsvbrowser tests fabfile run')

def docs():
    f.local('rm -f docs/dsvbrowser.rst')
    f.local('rm -f docs/modules.rst')
    f.local('sphinx-apidoc -o docs/ dsvbrowser')
    f.local('make -C docs clean')
    f.local('make -C docs html')
    f.local('open docs/_build/html/index.html')

