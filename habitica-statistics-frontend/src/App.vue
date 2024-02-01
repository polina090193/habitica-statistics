<template>
  <div id="app">
    <div class="wrapper">
      <form @submit.prevent="submitFileForm">
        <input
          type="file"
          name="habitica-tasks-history"
          ref="fileInput"
          @change="onFileChange"
          class="mr"
        />
        <input
          type="date"
          name="start-date"
          v-model="startDate"
          @change="resetResult"
          required
          class="mr"
        />
        <input
          type="date"
          name="end-date"
          v-model="endDate"
          @change="resetResult"
          required
          class="mr"
        />
        <button :disabled="!selectedFile" class="mr">Examine the file</button>
        <button :disabled="!selectedFile" @click="resetAll">Reset all</button>
      </form>
      <div class="file-form-error" style="color: red" v-for="error in errors" :key="error">{{ error }}</div>
      <form class="tasks-selector" v-if="tasks.length" @submit.prevent="submitTasksForm">
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
        <button class="mr">Give me my statistics</button>
        <button @click="resetChosenStatistics">Reset statistics</button>
      </form>
      <table v-if="chosenStatisticsList.length" class="calendar-table">
        <tr>
          <th class="name-col">Name</th>
          <th class="days-col" v-for="(day, key) in daysBetweenStartAndEnd" :key="day" v-html="getDateForCalendar(day, key)">
          </th>
        </tr>
        <tr v-for="task in chosenStatisticsList" :key="task.id">
          <td  class="name-col">{{ task.name }}</td>
          <td class="days-col" v-for="(day, key) in daysBetweenStartAndEnd" :key="day">
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
      <div class="total-days">Total days: {{ daysBetweenStartAndEnd.length }}</div>
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
      startDate: '',
      endDate: '',
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
          this.statisticsList = fetchedTasksListJson.statistics;
          this.tasks = this.statisticsList.map(task => ({id: task.id, name: task.name}))
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
        return '×';
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
.wrapper {
  display: flex;
  flex-direction: column;
  width: 100%;
  align-items: center;
}
.mr {
  margin-right: 10px;
}
.tasks-selector {
  margin-top: 20px;
}
.file-form-error {
  margin-top: 5px;
}
.calendar-table {
  position: relative;
  display: flex;
  flex-direction: column;
  max-width: 80vw;
  overflow-x: auto;
  margin-top: 30px;
  padding-bottom: 10px;
  border-collapse: collapse;
  border: 1px solid gray;
}
.name-col {
  position: sticky;
  top: 0;
  left: 0;
  min-width: 140px;
  padding: 5px;
  border-right: 1px solid gray;
  border-bottom: 1px solid lightgray;
  background-color: white;
}
.days-cols {
  display: flex;
  justify-content: flex-end;
}
.days-col {
  min-width: 58px;
  padding: 5px;
  border: 1px solid lightgray;
  text-align: center;
  vertical-align: middle;
}
.total-days {
  margin-top: 30px;
}
.statistics-table {
  border-collapse: collapse;
  margin: 30px 0;
}
.statistics-table th,
.statistics-table td {
  padding: 10px;
  border: 1px solid gray;
}
</style>
