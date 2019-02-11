import os
from src.expression.expression import get_expression_data

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    get_expression_data(THIS_FOLDER)
