from sql_generator import Contestant
from sql_generator import Occupation
from data_reconfiguration import constants
from copy import deepcopy
import pandas as pd


def find_contestant_id_from_dup_records(contestant_id):
    """
    Since there exists duplicate records in the csv for contestants.
    Given a contestant_id, find the unique_id used for insertion in the database.
    @param contestant_id: Player id retrieved from the csv
    @return: contestant_id used for database insertion.
    """
    if any(df_non_duplicate_contestants[constants.PLAYER_ID] == contestant_id):
        # if the contestant_id is present in the non duplicate ones
        return contestant_id
    else:
        if any(df_duplicate_contestants[constants.PLAYER_ID] == contestant_id):
            # check if duplicate records has the player id
            temp_contestant_df = df_duplicate_contestants.loc[df_duplicate_contestants[constants.PLAYER_ID]
                                                              == contestant_id]            
            first_row = temp_contestant_df.head(1)

            # find the appropriate contestant id based on the other parameters
            non_dup_contestants = df_non_duplicate_contestants
            non_duplicated_player_df_with_criteria = pd.merge(non_dup_contestants,
                                                              first_row,
                                                              how='inner',
                                                              on=constants.NON_DUPLICATED_PLAYER_CRITERIA_COLUMNS)
            if len(non_duplicated_player_df_with_criteria) == 1:
                return non_duplicated_player_df_with_criteria[constants.PLAYER_ID_X].item()
        return ''


def generate_contestant_and_occupation(df_contestant, input_config, output_config):
    """
    Collect contestant and occupation information from contestants.csv
    @param df_contestant: Contestant data-frame used for reconfiguration
    @param input_config: Input configuration
    @param output_config: Output configuration
    """

    # get location of output files
    contestants_sql_location = output_config.get('files', constants.CONTESTANTS)
    occupation_sql_location = output_config.get('files', constants.OCCUPATIONS)

    # reset the sql files
    open(contestants_sql_location, 'w').close()
    open(occupation_sql_location, 'w').close()

    # get entity definition
    contestant_entity_definition = input_config.get('entities', constants.CONTESTANT)
    occupation_entity_definition = input_config.get('entities', constants.OCCUPATION)

    # remove duplicate player_id rows and clean data
    global df_duplicate_contestants
    df_contestant = df_contestant.fillna('')
    df_duplicate_contestants = deepcopy(df_contestant)
    df_contestant = df_contestant.drop_duplicates(subset=[constants.PLAYER_ID],
                                                  keep='first')
    df_contestant = df_contestant.drop_duplicates(df_contestant.columns.difference([constants.PLAYER_ID]),
                                                  keep='first')
    global df_non_duplicate_contestants
    df_non_duplicate_contestants = df_contestant

    # Generate group of customers with the same occupation.
    contestants_groups = df_contestant.groupby(df_contestant[constants.OCCUPATION])
    occupation_id = 0
    contestant_count = 0
    for occupation_name, group in contestants_groups:
        # Generate SQL for Occupation
        occupation_id = occupation_id + 1

        if occupation_name:
            occupation_name = (occupation_name.strip()).replace("'", "\\'")
            contestant_occupation = Occupation(occupation_id,
                                               occupation_name,
                                               file_location=occupation_sql_location)
            contestant_occupation.generate_sql(entity_definition=occupation_entity_definition)

        # Generate SQL for contestant
        no_of_contestants = len(group)
        for index in range(no_of_contestants):
            csv_player = group.iloc[index]
            contestant_id = csv_player[constants.PLAYER_ID]

            first_name = (csv_player[constants.PLAYER_FIRST_NAME].strip()).replace("'", "\\'")
            last_name = (csv_player[constants.PLAYER_LAST_NAME].strip()).replace("'", "\\'")
            home_city = (csv_player[constants.HOMETOWN_CITY].strip()).replace("'", "\\'")
            country_or_state = (csv_player[constants.HOMETOWN_STATE].strip()).replace("'", "\\'")

            if occupation_name:
                player = Contestant(contestant_id=contestant_id,
                                    first_name=first_name,
                                    last_name=last_name,
                                    home_city=home_city,
                                    country_or_state=country_or_state,
                                    occupation_id=occupation_id,
                                    file_location=contestants_sql_location)
                player.generate_sql(entity_definition=contestant_entity_definition)
                contestant_count += 1
            else:
                player = Contestant(contestant_id=contestant_id,
                                    first_name=first_name,
                                    last_name=last_name,
                                    home_city=home_city,
                                    country_or_state=country_or_state,
                                    occupation_id=None,
                                    file_location=contestants_sql_location)
                player.generate_sql(entity_definition=contestant_entity_definition)
                contestant_count += 1

    print(" No. of occupations to be inserted : ", occupation_id-1)
    print(" No. of contestants to be inserted : ", contestant_count)