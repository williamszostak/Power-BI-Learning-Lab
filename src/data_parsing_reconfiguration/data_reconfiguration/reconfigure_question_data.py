from sql_generator import question as game_question
from sql_generator import category as game_question_category
import pandas as pd


def generate_sql_statements(questions_df,
                            trend_df,
                            input_config,
                            output_config):
    # get location of output files
    question_sql_location = output_config.get('files', 'questions')
    category_sql_location = output_config.get('files', 'category')

    # reset the sql files
    open(question_sql_location, 'w').close()
    open(category_sql_location, 'w').close()

    # get entity definition
    question_entity_definition = input_config.get('entities', 'question')
    category_entity_definition = input_config.get('entities', 'category')

    # get data from multiple CSVs
    questions_trend_df = pd.merge(questions_df, trend_df,
                                  how='outer',
                                  on=['game_id', 'row', 'column', 'round'])

    # generate SQL files
    no_of_questions, no_of_question_categories = generate_questions(questions_trend_df,
                                                                    question_sql_location,
                                                                    question_entity_definition,
                                                                    category_sql_location,
                                                                    category_entity_definition)
    print(questions_trend_df.columns)
    print(" No. of question categories to be inserted : ", no_of_question_categories)
    print(" No. of questions to be inserted : ", no_of_questions)


def generate_questions(questions_trend_df,
                       question_sql_location,
                       question_entity_definition,
                       category_sql_location,
                       category_entity_definition):
    question_counter = 0
    category_counter = 0
    questions_param = {}
    # Generate group of customers with the same occupation.
    question_groups = questions_trend_df.groupby(questions_trend_df['category'])
    for category, question_rows in question_groups:
        # Generate SQL for category
        category_counter = category_counter + 1

        if category:
            category = (category.strip()).replace("'", "\\'")
            question_category = game_question_category.Category(category_counter,
                                                                category,
                                                                file_location=category_sql_location)
            question_category.generate_sql(entity_definition=category_entity_definition)

        # Generate SQL for question
        no_of_questions = len(question_rows)
        for index in range(no_of_questions):
            question_row = question_rows.iloc[index]
            question_counter += 1
            questions_param['question_id'] = question_counter
            questions_param['question_text'] = (question_row['question_text'].strip()).replace("'", "\\'")
            questions_param['answer'] = (question_row['answer'].strip()).replace("'", "\\'")
            questions_param['dollar_value'] = question_row['value_x']
            questions_param['file_location'] = question_sql_location
            questions_param['game_id'] = question_row['game_id']
            questions_param['round_name'] = (question_row['round'].strip()).replace("'", "\\'")
            questions_param['category_id'] = category_counter
            if pd.notnull(question_row['season_y']):
                if pd.notnull(question_row['wager']):
                    questions_param['is_daily_double'] = 1
                else:
                    questions_param['is_daily_double'] = 0
                questions_param['question_index'] = question_row['question_index']

            question = game_question.Question(**questions_param)
            question.generate_sql(question_entity_definition)

    return question_counter, category_counter