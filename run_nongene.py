import os
from src.non_gene_features.non_gene_features import get_non_gene_information

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    get_non_gene_information(THIS_FOLDER)
