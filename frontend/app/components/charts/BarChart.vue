<template>
  <Bar :data="chartData" :options="mergedOptions" />
</template>

<script setup>
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
import { Bar } from 'vue-chartjs'
import { computed } from 'vue'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const props = defineProps({
  chartData: {
    type: Object,
    required: true
  },
  chartOptions: {
    type: Object,
    default: () => ({})
  }
})

const mergedOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: '#f1f5f9', // primary-50
        drawBorder: false
      },
      ticks: {
        font: {
          family: "'Inter', sans-serif",
          weight: 'bold'
        },
        color: '#94a3b8' // primary-400
      }
    },
    x: {
      grid: {
        display: false,
        drawBorder: false
      },
      ticks: {
        font: {
          family: "'Inter', sans-serif",
          weight: 'bold'
        },
        color: '#64748b' // primary-500
      }
    }
  },
  borderRadius: 8,
  ...props.chartOptions
}))
</script>
