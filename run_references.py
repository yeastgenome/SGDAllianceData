import os
from src.literature.refs import get_refs_information
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    get_refs_information(THIS_FOLDER)