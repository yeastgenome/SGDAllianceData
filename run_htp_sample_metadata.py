import os
from src.htp_metadata.htp_datasamples import get_htp_sample_metadata
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    get_htp_sample_metadata(THIS_FOLDER)
