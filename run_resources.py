import os
from src.literature.resources import get_resources_information
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    get_resources_information(THIS_FOLDER)