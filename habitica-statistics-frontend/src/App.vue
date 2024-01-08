<template>
  <div id="app">
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
    <div style="max-width: 80vw" v-if="chosenStatisticsList.length">
      <table class="calendar-table">
        <thead>
          <tr class="calendar-tr">
            <th class="calendar-table-name">Name</th>
            <th
              class="calendar-table-head"
              v-for="(yearData, year) in calendar"
              :key="year"
            >
              <div class="calendar-table-year">{{ year }}</div>
              <tr>
                <th
                  class="calendar-table-head"
                  v-for="(monthData, month) in yearData"
                  :key="month"
                >
                  <div class="calendar-table-month">{{ months[month] }}</div>
                  <tr>
                    <th
                      class="calendar-table-head border"
                      v-for="day in monthData"
                      :key="day"
                    >
                      {{ day }}
                    </th>
                  </tr>
                </th>
              </tr>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr class="calendar-tr" v-for="task in chosenStatisticsList" :key="task.id">
            <td class="calendar-table-name">{{ task.name }}</td>
            <td class="border" v-for="(day, key) in daysBetweenStartAndEnd" :key="day">
              {{
                getDayCell(
                  task,
                  day,
                  daysBetweenStartAndEnd[key - 1],
                  daysBetweenStartAndEnd[key + 1]
                )
              }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <table v-if="chosenStatisticsList.length">
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
</template>

<script>
import { dateAdapter } from './utils/date-adapter';
import { getMonthsList } from './utils/get-months-list';

export default {
  name: 'App',
  data() {
    return {
      tasks: [],
      selectedFile: null,
      startDate: '',
      endDate: '',
      calendar: {},
      selectedTasksIDs: [],
      statisticsList: [],
      chosenStatisticsList: [],
      errors: [],
      allTasksSelected: false,
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
  },
  mounted() {
    this.generateCalendar();
  },
  methods: {
    onFileChange(event) {
      const file = event.target.files[0];
      this.selectedFile = file;
      this.errors = [];
    },
    async submitFileForm() {
      if (!this.selectedFile) return;
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
      this.generateCalendar();
    },
    generateCalendar() {
      const calendar = {};
      let currentDate = new Date(this.startDate);
      const lastDate = new Date(this.endDate);

      while (currentDate <= lastDate) {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();

        if (!calendar[year]) {
          calendar[year] = {};
        }

        calendar[year][month] = {};

        const daysInMonth =
          currentDate.getMonth() === lastDate.getMonth()
            ? lastDate.getDate()
            : new Date(year, month + 1, 0).getDate();

        for (let day = 1; day <= daysInMonth; day++) {
          calendar[year][month] = day;
        }

        currentDate.setMonth(month + 1);
      }

      this.calendar = calendar;
    },
    getDayCell(task, day, previousDay, nextDay) {
      // Not done
      if (!task.days.includes(day)) {
        return '';
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
  overflow: auto;
  border-collapse: collapse;
  border: 1px solid black;
}
.border {
  border: 1px solid black;
  max-width: 30px;
  width: 30px;
  padding: 0;
  margin: 0;
}
.calendar-tr {
  display: flex;
  margin: 0;
  padding: 0;
  border: 1px solid black;
}
.calendar-table-name {
  width: 100px;
  min-width: 100px;
  max-width: 100px;
  border: 1px solid black;
}
.calendar-table-head {
  text-align: start;
  padding: 0;
}
.calendar-table-year,
.calendar-table-month {
  padding-left: 5px;
}
</style>
