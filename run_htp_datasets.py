import os
from src.htp_metadata.htp_datasets import get_htp_datasets
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    get_htp_datasets(THIS_FOLDER)
