import csv
from datetime import datetime, timedelta

csv_file_path = 'habitica-tasks-history.csv'
filtered_rows = []

start_date = datetime.strptime('01.01.2023', '%d.%m.%Y')
end_date = datetime.strptime('31.12.2023', '%d.%m.%Y')
number_of_days = (end_date - start_date).days

def calculate_percentage(part, whole):
    return (part / whole) * 100

task_ids = [
    'exampled-test-test-test-yourtaskidaa',
]

with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
    reader = list(csv.DictReader(file))

    streaks = {task_id: [[]] for task_id in task_ids}

    for task_id in task_ids:
        task_rows = filter(lambda row: row['Task ID'] == task_id, reader)
        sorted_rows = sorted(task_rows, key=lambda row: datetime.strptime(
            row['Date'], '%Y-%m-%d %H:%M:%S'))

        task_days = []
        streak_number = 0
        task_name = None

        for table_row in sorted_rows:
            table_task_name = table_row['Task Name']
            table_task_id = table_row['Task ID']
            date_time_str = table_row['Date']

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
        longest_streak_first_date = longest_streak[0].strftime('%d.%m.%Y')
        longest_streak_last_date = longest_streak[-1].strftime('%d.%m.%Y')
        
        print(f"{task_name}:\n \
            {len(task_days)} times \n \
            {percentage}% \n \
            Longest streak: {longest_streak_len} days, {longest_streak_first_date} - {longest_streak_last_date} \n\n \
        ")