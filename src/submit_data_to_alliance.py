import os

# https://github.com/alliance-genome/agr_java_software/blob/develop/agr_api/Submission_README.md
# curl command:
#
# SUBMISSION_VERSION
# curl -H "api_access_token: ALLIANCE_API_TOKEN" -X POST "submit ALLIANCE_SUBMIT_URL" -F "FILE_NAME = @directory/file_name"

submit_list = [
    "BGI", "GFF", "DAF", "PHENOTYPE", "EXPRESSION", "ALLELE"
]

