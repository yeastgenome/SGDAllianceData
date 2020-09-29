import os
from src.affectedGeneModel.affectedGeneModel import get_agm_information
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    get_agm_information(THIS_FOLDER)