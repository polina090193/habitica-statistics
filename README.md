# Habitica Statistics
Python app for calculating your habits statistics based on data from [Habitica app](https://habitica.com/).

Work in progress, stay tuned.

## Getting the file
1. Login to your Habitica account.
2. Go to [https://habitica.com/export/history.csv](https://habitica.com/export/history.csv) to get your data about habits and dailies in CSV.

# 1. Web app

## Start:
1. In the root directory run `flask run --debug`
2. In the habitica-statistics-frontend directory run `npm run serve`
3. Open http://localhost:8080/

## Usage:
4. Upload your downloaded habitica-tasks-history.csv
5. Choose tasks.
6. Push "Give me my statistics".

# 2. Console app

## Usage:
1. Put your downloaded habitica-tasks-history.csv in the root folder.
2. You can add task IDs you want to examine (you can peek it in your .csv file): to the task_ids variable or during running the app.
3. Run the habitica-statistics-console-app.py.
4. Enter start date and end date.
5. Example output:
```
Eat a fruit 🍎:
             35 times
             76%
             Longest streak: 11 days, 07.11.2023 - 17.11.2023


Workout:
             26 times
             57%
             Longest streak: 6 days, 04.11.2023 - 09.11.2023


Reading:
             34 times
             74%
             Longest streak: 8 days, 08.12.2023 - 15.12.2023
```
