import csv
import click
from datetime import datetime
import habitica_statistics

csv_file_path = 'habitica-tasks-history.csv'

while True:
    start_date_inp = input('Start date\n(Enter date as dd.mm.yyyy): ')

    try:
        start_date = datetime.strptime(start_date_inp, '%d.%m.%Y')
        break
    except ValueError:
        print('Incorrect format, should be dd.mm.yyyy')

while True:
    end_date_inp = input('End date\n(Enter date as dd.mm.yyyy): ')

    try:
        end_date = datetime.strptime(end_date_inp, '%d.%m.%Y')
        break
    except ValueError:
        print('Incorrect format, should be dd.mm.yyyy')

number_of_days = (end_date - start_date).days

def calculate_percentage(part, whole):
    return (part / whole) * 100

task_ids = [
    # 'exampled-test-test-test-yourtaskidaa',
]

with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
    reader = list(csv.DictReader(file))
    task_ids = []

    if (not task_ids or len(task_ids) == 0):
        if click.confirm('Do you want to enter task ID?', default=True):
            task_id_inp = input('Enter task ID: ')
            task_ids.append(task_id_inp)

            while True:
                print('Your task IDs:')
                for task_id in task_ids:
                    print(f"{task_id}")
                if click.confirm('Do you want to enter another one task ID?', default=True):
                    task_id_inp = input('Enter task ID: ')
                    task_ids.append(task_id_inp)
                else:
                    break

        else:
            task_ids = list(set(map(lambda row: row['Task ID'], reader)))

    statistics_result = habitica_statistics.calculate_statistics(
        reader, start_date, end_date, task_ids)

    for task_result in statistics_result:
        print(f"{task_result['name']}:\n \
            {task_result['days']} times \n \
            {task_result['percentage']}% \n \
            Longest streak: {task_result['longest_streak']} \n\n \
        ")
