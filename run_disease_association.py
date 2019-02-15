import os
from src.disease.disease import get_disease_association_data
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    get_disease_association_data(THIS_FOLDER)
