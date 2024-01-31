<template>
  <div id="app">
    <div>
      <form @submit.prevent="submitFileForm">
        <input
          type="file"
          name="habitica-tasks-history"
          ref="fileInput"
          @change="onFileChange"
        />
        <input
          type="date"
          name="start-date"
          v-model="startDate"
          @change="resetResult"
          required
        />
        <input
          type="date"
          name="end-date"
          v-model="endDate"
          @change="resetResult"
          required
        />
        <button :disabled="!selectedFile">Examine the file</button>
        <button :disabled="!selectedFile" @click="resetAll">Reset all</button>
      </form>
      <div style="color: red" v-for="error in errors" :key="error">{{ error }}</div>
      <form v-if="tasks.length" @submit.prevent="submitTasksForm">
        <label for="select-all-tasks">
          <input
            type="checkbox"
            id="select-all-tasks"
            v-model="allTasksSelected"
            @change="selectAlltasks"
          />
          Select all
        </label>
        <p v-for="task in tasks" :key="task.id">
          <label :for="task.id">
            <input
              type="checkbox"
              :id="task.id"
              :value="task.id"
              v-model="selectedTasksIDs"
            />
            {{ task.name }}
          </label>
        </p>
        <button>Give me my statistics</button>
        <button @click="resetChosenStatistics">Reset statistics</button>
      </form>
      <table v-if="chosenStatisticsList.length" class="calendar-table">
        <tr>
          <th>Name</th>
          <th v-for="(day, key) in daysBetweenStartAndEnd" :key="day" v-html="getDateForCalendar(day, key)">
          </th>
        </tr>
        <tr v-for="task in chosenStatisticsList" :key="task.id">
          <td>{{ task.name }}</td>
          <td v-for="(day, key) in daysBetweenStartAndEnd" :key="day">
            {{
              getDayResult(
                task,
                day,
                daysBetweenStartAndEnd[key - 1],
                daysBetweenStartAndEnd[key + 1]
              )
            }}
          </td>
        </tr>
      </table>
      <table class="statistics-table" v-if="chosenStatisticsList.length">
        <tr>
          <th>Name</th>
          <th>Days done</th>
          <th>Percentage</th>
          <th>Longest streak</th>
        </tr>
        <tr v-for="task in chosenStatisticsList" :key="task.id">
          <td>{{ task.name }}</td>
          <td>{{ task.days.length }}</td>
          <td>{{ task.percentage }}%</td>
          <td>{{ task.longest_streak }}</td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script>
import { dateAdapter, parseDateStringToDate } from './utils/date-adapter';
import { getMonthsList } from './utils/get-months-list';

export default {
  name: 'App',
  data() {
    return {
      tasks: [],
      selectedFile: null,
      startDate: '2023-12-31',
      endDate: '2024-02-02',
      calendar: {},
      selectedTasksIDs: [],
      statisticsList: [],
      chosenStatisticsList: [],
      errors: [],
      allTasksSelected: false,
      parseDateStringToDate,
    };
  },
  computed: {
    months() {
      return getMonthsList();
    },
    daysBetweenStartAndEnd() {
      const firstDate = new Date(this.startDate);
      const lastDate = new Date(this.endDate);
      const dateArray = [];

      for (
        let currentDate = firstDate;
        currentDate <= lastDate;
        currentDate.setDate(currentDate.getDate() + 1)
      ) {
        dateArray.push(
          new Date(currentDate).toLocaleString('de-DE', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
          })
        );
      }

      return dateArray;
    },
    lastYear() {
      const years = Object.keys(this.calendar);
      return years[years.length - 1];
    },
    lastMonth() {
      const months = Object.keys(this.calendar[this.lastYear]);
      return months[months.length - 1];
    },
  },
  methods: {
    onFileChange(event) {
      const file = event.target.files[0];
      this.selectedFile = file;
      this.errors = [];
    },
    async submitFileForm() {
      if (!this.selectedFile) {
        this.errors.push('No file selected');
        return;
      }
      if (!this.startDate) {
        this.errors.push('No start date selected');
        return;
      }
      if (!this.endDate) {
        this.errors.push('No end date selected');
        return;
      }
      if (this.startDate > this.endDate) {
        this.errors.push('Start date cannot be after end date');
        return;
      }
      this.resetResult();

      const formData = new FormData();
      formData.append('habitica-tasks-history', this.selectedFile);
      formData.append(
        'start-date',
        this.startDate === '' ? '' : dateAdapter.convertToBEFormat(this.startDate)
      );
      formData.append(
        'end-date',
        this.endDate === '' ? '' : dateAdapter.convertToBEFormat(this.endDate)
      );

      try {
        const fetchedTasksList = await fetch('http://127.0.0.1:5000/get-statistics', {
          method: 'POST',
          body: formData,
        });

        if (!fetchedTasksList.ok) {
          const errorResponse = await fetchedTasksList.json();
          if (errorResponse && errorResponse.error) {
            this.errors.push(errorResponse.error);
          } else {
            this.errors.push('Unknown error occurred');
          }
        } else {
          const fetchedTasksListJson = await fetchedTasksList.json();
          this.tasks = fetchedTasksListJson.tasks_list;
          this.statisticsList = fetchedTasksListJson.statistics;
        }
      } catch (e) {
        this.errors.push('Network error occurred');
      }
    },
    selectAlltasks() {
      if (this.selectedTasksIDs.length === this.tasks.length) {
        this.selectedTasksIDs = [];
      } else {
        this.selectedTasksIDs = this.tasks.map(task => task.id);
      }
    },
    submitTasksForm() {
      this.chosenStatisticsList = this.statisticsList.filter(task =>
        this.selectedTasksIDs.includes(task.id)
      );
    },
    getDateForCalendar(day, key) {
      const options = {
        day: 'numeric',
      };
      const dateObj = parseDateStringToDate(day);

      if (key === 0 || dateObj.getDate() === 1) {
        options.month = 'short';
        options.year = 'numeric';
      }

      return dateObj.toLocaleDateString('en-US', options).replace(/, /g, '<br>')
    },
    getDayResult(task, day, previousDay, nextDay) {
      // Not done
      if (!task.days.includes(day)) {
        return '❌';
      }

      // Streak
      if (
        (previousDay && task.days.includes(previousDay)) ||
        (nextDay && task.days.includes(nextDay))
      ) {
        return '🎉';
      }

      // Single done
      return '✔';
    },
    resetChosenStatistics() {
      this.selectedTasksIDs = [];
      this.chosenStatisticsList = [];
      this.allTasksSelected = false;
    },
    resetResult() {
      this.tasks = [];
      this.statisticsList = [];
      this.resetChosenStatistics();
      this.errors = [];
    },
    resetAll() {
      this.selectedFile = null;
      this.$refs.fileInput.value = '';
      this.startDate = '';
      this.endDate = '';
      this.calendar = [];
      this.tasks = [];
      this.selectedTasksIDs = [];
      this.statisticsList = [];
      this.chosenStatisticsList = [];
      this.errors = [];
      this.allTasksSelected = false;
    },
  },
};
</script>

<style>
#app {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 60px;
  box-sizing: border-box;
}
* {
  box-sizing: border-box;
}
.calendar-table {
  max-width: 80vw;
  overflow: auto;
  margin-top: 20px;
}
.calendar-table {
  border-collapse: collapse;
  border: 1px solid black;
}
.border {
  border: 1px solid black;
}
.calendar-tr {
  display: flex;
  margin: 0;
  padding: 0;
  border: 1px solid black;
}
.calendar-table-name {
  border: 1px solid black;
}
.calendar-table-head {
  text-align: start;
  padding: 0;
}
.calendar-table-days {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}

.statistics-table {
  margin-top: 20px;
}
</style>
<!-- <style>
.calendar-table-wrapper {
	overflow: auto;
	margin-top: 20px;
	width: 80%;
}
.calendar-table {
  display: grid;
  grid-template-rows: 60px repeat(auto-fit, minmax(30px, 1fr));
  grid-template-columns: auto 1fr;
  border-top: 1px solid black;
  border-right: 1px solid black;
}
.calendar-table-years {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  grid-template-rows: auto;
}
.calendar-table-year {
  display: grid;
  grid-template-rows: 20px 40px;
}
.calendar-table-months {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
	grid-template-rows: 40px;
	width: 100%;
}
.calendar-table-month {
	display: grid;
	width: 100%;
	grid-template-rows: 20px 20px;
}
.calendar-table-days {
	display: grid;
	width: 100%;
	grid-template-columns: repeat(auto-fit, 20px);
	grid-template-rows: 20px;
}
</style> -->
<style>
.calendar-table-wrapper {
  overflow-x: auto;
  margin-top: 20px;
  width: 90vw;
}
.calendar-table {
  display: flex;
  flex-direction: column;
  overflow-x: auto;
  border-top: 1px solid black;
  border-right: 1px solid black;
}
.calendar-head {
  display: flex;
}
.calendar-table-first-column {
  flex-shrink: 0;
  width: 200px;
  border-right: 1px solid black;
  text-align: center;
  vertical-align: middle;
}
.calendar-table-years {
  display: flex;
  height: 60px;
}
.calendar-table-year {
  display: flex;
  height: 60px;
  flex-direction: column;
}
.calendar-table-months {
  display: flex;
  height: 40px;
}
.calendar-table-month {
  display: flex;
  height: 40px;
  flex-direction: column;
}
.calendar-table-days {
  display: flex;
  max-height: 20px;
  justify-content: flex-end;
}
.calendar-table-days_last-month {
  justify-content: flex-start;
}
.calendar-table-day-name {
  width: 30px;
}
.calendar-days-cells {
  display: flex;
  justify-content: flex-end;
}
.calendar-days-cell {
  display: flex;
  justify-content: flex-end;
  width: 30px;
}
</style>
