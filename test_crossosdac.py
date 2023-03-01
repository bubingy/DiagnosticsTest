import sys

from tasks.CrossOSDACTest.analyze import analyze
from tasks.CrossOSDACTest.validate import validate


if __name__ == '__main__':
    if sys.argv[1] == 'analyze':
        analyze()
    if sys.argv[1] == 'validate':
        validate()
