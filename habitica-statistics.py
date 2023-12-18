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

    for task_id in task_ids:
        task_days = []
        task_name = None

        for table_row in reader:
            table_task_name = table_row['Task Name']
            table_task_id = table_row['Task ID']
            date_time_str = table_row['Date']

            table_row_date = datetime.strptime(
                table_row['Date'], '%Y-%m-%d %H:%M:%S')

            if (start_date <= table_row_date <= end_date + timedelta(days=1) and
                table_task_id == task_id and
                table_row_date not in task_days):
                task_days.append(table_row_date)

                if task_name is None:
                    task_name = table_task_name

        task_days_length = len(task_days)
        percentage = round(calculate_percentage(task_days_length, number_of_days))

        print(f"{task_name}: {len(task_days)} times, {percentage}%")
