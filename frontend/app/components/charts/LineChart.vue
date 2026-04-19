<template>
  <Line :data="chartData" :options="mergedOptions" />
</template>

<script setup>
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler } from 'chart.js'
import { Line } from 'vue-chartjs'
import { computed } from 'vue'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

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
  elements: {
    line: {
      tension: 0.4 // Smooth curves
    },
    point: {
      radius: 4,
      hoverRadius: 6
    }
  },
  ...props.chartOptions
}))
</script>
