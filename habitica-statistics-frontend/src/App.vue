<template>
  <div id="app">
    <form @submit.prevent="submitFileForm">
      <input type="file" name="habitica-tasks-history" ref="fileInput" @change="onFileChange" />
      <input type="date" name="start-date" v-model="startDate" />
      <input type="date" name="end-date" v-model="endDate" />
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
    <div v-for="task in chosenStatisticsList" :key="task.id">
      <p>{{ task.name }}</p>
      <p>Days: {{ task.days }}</p>
      <p>{{ task.percentage }}%</p>
      <p>Longest streak: {{ task.longest_streak }}</p>
    </div>
  </div>
</template>

<script>
import dateAdapter from './utils/date-adapter';

export default {
  name: 'App',
  data() {
    return {
      tasks: [],
      selectedFile: null,
      startDate: '',
      endDate: '',
      selectedTasksIDs: [],
      statisticsList: [],
      chosenStatisticsList: [],
      errors: [],
      allTasksSelected: false,
    };
  },
  methods: {
    onFileChange(event) {
      const file = event.target.files[0];
      this.selectedFile = file;
      this.errors = [];
    },
    async submitFileForm() {
      if (!this.selectedFile) return;

      const formData = new FormData();
      formData.append('habitica-tasks-history', this.selectedFile);
      formData.append('start-date', this.startDate === '' ? '' : dateAdapter(this.startDate));
      formData.append('end-date', this.endDate === '' ? '' : dateAdapter(this.endDate));

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
      this.chosenStatisticsList = this.statisticsList.filter(
        task => this.selectedTasksIDs.includes(task.id),
      )
    },
    resetChosenStatistics() {
      this.selectedTasksIDs = [];
      this.chosenStatisticsList = [];
      this.allTasksSelected = false;
    },
    resetAll() {
      this.selectedFile = null;
      this.$refs.fileInput.value = '';
      this.startDate = '';
      this.endDate = '';
      this.tasks = [];
      this.selectedTasksIDs = [];
      this.statisticsList = [];
      this.chosenStatisticsList = [];
      this.errors = [];
      this.allTasksSelected = false;
    }
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
}
</style>
