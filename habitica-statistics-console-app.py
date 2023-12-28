import csv, click
from datetime import datetime, timedelta

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

    streaks = {task_id: [[]] for task_id in task_ids}

    for task_id in task_ids:
        task_rows = list(filter(lambda row: row['Task ID'] == task_id, reader))

        if (not task_rows):
            print(f'Task ID {task_id} not found')
            continue

        sorted_rows = sorted(task_rows, key=lambda row: datetime.strptime(
            row['Date'], '%Y-%m-%d %H:%M:%S'))

        task_days = []
        streak_number = 0
        task_name = None

        for table_row in sorted_rows:
            table_task_name = table_row['Task Name']
            table_task_id = table_row['Task ID']

            table_row_date = datetime.strptime(
                table_row['Date'], '%Y-%m-%d %H:%M:%S')

            table_row_date_formatted = table_row_date.strftime('%d.%m.%Y')

            if task_name is None:
                task_name = table_task_name

            if (start_date <= table_row_date <= end_date + timedelta(days=1) and
                table_task_id == task_id and
                    table_row_date_formatted not in task_days):

                task_days.append(table_row_date_formatted)

                if not streaks[task_id][streak_number]:
                    streaks[task_id][streak_number].append(table_row_date)

                else:
                    last_saved_date = streaks[task_id][streak_number][-1]
                    date_after_last_saved = last_saved_date + timedelta(days=1)

                    if table_row_date.day == date_after_last_saved.day:
                        streaks[task_id][streak_number].append(table_row_date)

                    else:
                        streak_number += 1
                        streaks[task_id].append([table_row_date])

        task_days_length = len(task_days)
        percentage = round(calculate_percentage(
            task_days_length, number_of_days))

        longest_streak = max(streaks[task_id], key=lambda streak: len(streak))
        longest_streak_len = len(longest_streak)

        is_streak_exist = longest_streak_len > 0
        is_streak_one_day = longest_streak_len == 1

        longest_streak_first_date = longest_streak[0].strftime('%d.%m.%Y') if is_streak_exist else ''
        longest_streak_last_date = longest_streak[-1].strftime('%d.%m.%Y') if is_streak_exist else ''

        longest_streak_result = f"{longest_streak_len} days, {longest_streak_first_date} - {longest_streak_last_date}" \
            if is_streak_exist and not is_streak_one_day \
                else 'no multi-day streaks'
        
        print(f"{task_name}:\n \
            {len(task_days)} times \n \
            {percentage}% \n \
            Longest streak: {longest_streak_result} \n\n \
        ")
