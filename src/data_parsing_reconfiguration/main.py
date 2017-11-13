# The entire process starts from here
# The config.ini is required to execute this program

import sys
import os

sys.path.insert(0, os.path.realpath('./csv_reader'))
sys.path.insert(0, os.path.realpath('./data_reconfiguration'))
sys.path.insert(0, os.path.realpath('./sql_generator'))

from csv_reader import argument_parser as ap
from csv_reader import CSVReader as csvr


if __name__ == '__main__':
    # Parse command line arguments
    config = ap.argument_parser()

    # Retrieve questions.csv location from the config
    questions_csv_location = config.get('files', 'questions')
    print(os.path.realpath(questions_csv_location))

    # Request dataframe of questions.csv
    questions_df = csvr.get_dataframe(questions_csv_location)
    print(questions_df.describe())