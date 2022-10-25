import os
from src.alleles.allelesPersistent import get_allele_information

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    get_allele_information(THIS_FOLDER)