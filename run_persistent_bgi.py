import os
from src.basic_gene_information.bgiPersistent import get_basic_gene_information

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    get_basic_gene_information(THIS_FOLDER)
