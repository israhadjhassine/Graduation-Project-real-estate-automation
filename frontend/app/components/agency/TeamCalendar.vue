<template>
  <div class="calendar-container bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden flex flex-col h-[800px]">
    <!-- Header -->
    <div class="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200">
      <div class="flex items-center gap-6">
        <h2 class="text-xl font-bold text-gray-800 shrink-0">{{ title }}</h2>
        
        <!-- Navigation Controls -->
        <div class="flex items-center bg-gray-100 rounded-lg p-1 gap-1">
          <button @click="goToToday" class="px-3 py-1.5 text-sm font-semibold text-gray-600 hover:bg-white hover:shadow-sm rounded-md transition-all">
            Today
          </button>
          
          <div class="w-px h-4 bg-gray-300 mx-1"></div>
          
          <div class="flex items-center gap-0.5">
            <button @click="prevDay" class="p-1.5 hover:bg-white hover:shadow-sm rounded-md transition-all text-gray-600">
              <LucideChevronLeft :size="18" />
            </button>
            
            <!-- Day Selector -->
            <select 
              v-model="selectedDay" 
              class="bg-transparent border-none text-sm font-bold text-gray-700 focus:ring-0 cursor-pointer hover:text-blue-600 px-1"
            >
              <option v-for="d in daysInSelectedMonth" :key="d" :value="d">
                {{ d }}
              </option>
            </select>

            <button @click="nextDay" class="p-1.5 hover:bg-white hover:shadow-sm rounded-md transition-all text-gray-600">
              <LucideChevronRight :size="18" />
            </button>
          </div>
        </div>

        <!-- Date Label Display -->
        <div class="flex items-center gap-2">
          <select v-model="selectedMonth" class="bg-transparent border-none text-sm font-bold text-gray-700 focus:ring-0 cursor-pointer hover:text-blue-600">
            <option v-for="(m, i) in monthNames" :key="i" :value="i">{{ m }}</option>
          </select>
          <select v-model="selectedYear" class="bg-transparent border-none text-sm font-bold text-gray-700 focus:ring-0 cursor-pointer hover:text-blue-600">
            <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
      </div>

      <!-- Agent Filter Dropdown -->
      <div v-if="showAgentFilter" class="relative agent-filter-dropdown">
        <button 
          @click="isAgentFilterOpen = !isAgentFilterOpen"
          class="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg hover:border-blue-400 transition-all text-sm font-semibold text-gray-700 shadow-sm"
        >
          <div class="flex -space-x-2 overflow-hidden">
            <div 
              v-for="agentId in selectedAgents.slice(0, 3)" 
              :key="agentId"
              class="inline-block h-5 w-5 rounded-full ring-2 ring-white bg-blue-100 flex items-center justify-center text-[8px] font-bold text-blue-600"
            >
              {{ uniqueAgents.find(a => String(a.id) === String(agentId))?.name.charAt(0) }}
            </div>
            <div v-if="selectedAgents.length > 3" class="inline-block h-5 w-5 rounded-full ring-2 ring-white bg-gray-100 flex items-center justify-center text-[8px] font-bold text-gray-500">
              +{{ selectedAgents.length - 3 }}
            </div>
          </div>
          <span>Team Filter</span>
          <LucideChevronDown :size="16" :class="{'rotate-180': isAgentFilterOpen}" class="transition-transform text-gray-400" />
        </button>

        <!-- Dropdown Menu -->
        <div 
          v-if="isAgentFilterOpen"
          class="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-2xl border border-gray-100 z-50 p-2 animate-in fade-in zoom-in duration-200"
        >
          <div class="p-2 border-b border-gray-50 flex items-center justify-between">
            <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Select Agents</span>
            <button @click="toggleAllAgents" class="text-[10px] font-bold text-blue-600 hover:underline">
              {{ selectedAgents.length === uniqueAgents.length ? 'Clear All' : 'Select All' }}
            </button>
          </div>
          <div class="max-h-60 overflow-y-auto py-1 custom-scrollbar">
            <div 
              v-for="agent in uniqueAgents" 
              :key="agent.id"
              @click="toggleAgent(agent.id)"
              class="flex items-center gap-3 px-3 py-2.5 hover:bg-blue-50 rounded-lg cursor-pointer transition-colors group"
            >
              <div 
                class="w-5 h-5 rounded border-2 flex items-center justify-center transition-all"
                :class="selectedAgents.includes(String(agent.id)) ? 'bg-blue-600 border-blue-600' : 'bg-white border-gray-200 group-hover:border-blue-400'"
              >
                <LucideCheck v-if="selectedAgents.includes(String(agent.id))" :size="12" class="text-white" stroke-width="4" />
              </div>
              <div class="flex flex-col">
                <span class="text-sm font-bold text-gray-700">{{ agent.name }}</span>
                <span class="text-[10px] text-gray-400 leading-tight">Sub-agent</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Timeline View -->
    <div class="flex-1 overflow-y-auto relative custom-scrollbar bg-white" ref="timelineRef">
      <!-- Current Time Indicator -->
      <div 
        v-if="isTodaySelected"
        class="absolute left-0 right-0 z-20 pointer-events-none flex items-center"
        :style="{ top: currentTimePosition + 'px' }"
      >
        <div class="w-3 h-3 rounded-full bg-red-500 -ml-1.5"></div>
        <div class="h-px bg-red-500 flex-1"></div>
      </div>

      <div class="relative min-h-full">
        <!-- Hour Rows -->
        <div v-for="hour in hoursOfDay" :key="hour" class="flex h-[80px] border-b border-gray-100 relative group">
          <!-- Hour Label -->
          <div class="w-20 pr-4 text-right -mt-2.5">
            <span class="text-xs font-semibold text-gray-500 uppercase">{{ formatHour(hour) }}</span>
          </div>
          <!-- Slot Area -->
          <div class="flex-1 border-l border-gray-100 relative">
            <!-- Half-hour line -->
            <div class="absolute top-1/2 left-0 right-0 h-px border-t border-gray-50 border-dashed"></div>
          </div>
        </div>

        <!-- Positioned Visits -->
        <div class="absolute top-0 left-20 right-4 bottom-0 pointer-events-none">
          <div 
            v-for="event in positionedVisits" 
            :key="`${event.visit.id}-${event.visit.agent?.id}-${event.style.left}`"
            @click="openVisitDetails(event.visit)"
            class="absolute p-2 rounded-xl border-l-4 shadow-sm cursor-pointer pointer-events-auto transition-all hover:shadow-md hover:z-30 overflow-hidden flex flex-col"
            :style="event.style"
            :class="getVisitColorClass(event.visit.status)"
          >
            <div class="flex flex-col h-full overflow-hidden">
              <div class="flex items-center justify-between gap-1 overflow-hidden mb-0.5">
                <span class="text-[11px] font-bold truncate leading-tight">{{ event.visit.property?.title || 'Untitled' }}</span>
                <span class="text-[9px] font-black whitespace-nowrap opacity-80 bg-black/5 px-1.5 py-0.5 rounded uppercase tracking-tighter">{{ event.visit.status }}</span>
              </div>
              <div class="flex items-center gap-1.5 mt-0.5 min-w-0">
                <div class="w-4 h-4 rounded-full bg-white/60 flex items-center justify-center text-[9px] font-bold border border-black/10 shrink-0 shadow-sm text-gray-700">
                  {{ event.visit.agent?.full_name?.charAt(0) || 'A' }}
                </div>
                <span class="text-[10px] truncate opacity-90 font-semibold tracking-tight">
                  {{ event.visit.agent?.full_name?.split(' ')[0] }} • {{ event.visit.client?.full_name || 'No Client' }}
                </span>
              </div>
              <div class="mt-auto pt-1 flex items-center justify-between">
                <span class="text-[9px] font-bold opacity-60 flex items-center gap-1">
                  <LucideClock :size="8" />
                  {{ formatTime(event.visit.visit_date) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { LucideChevronLeft, LucideChevronRight, LucideChevronDown, LucideCheck, LucideClock } from 'lucide-vue-next'

const props = defineProps({
  visits: {
    type: Array,
    default: () => []
  },
  agents: {
    type: Array,
    default: () => []
  },
  showAgentFilter: {
    type: Boolean,
    default: true
  },
  title: {
    type: String,
    default: 'Team Schedule'
  }
})

const emit = defineEmits(['view-visit'])

const openVisitDetails = (visit) => {
  emit('view-visit', visit)
}

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

const now = ref(new Date())
const selectedDay = ref(now.value.getDate())
const selectedMonth = ref(now.value.getMonth())
const selectedYear = ref(now.value.getFullYear())

// Agent Filtering
const isAgentFilterOpen = ref(false)
const selectedAgents = ref([])

const uniqueAgents = computed(() => {
  // If agents prop is provided, use it (this shows all sub-agents even without visits)
  if (props.agents && props.agents.length > 0) {
    return props.agents.map(a => ({
      id: a.id,
      name: a.full_name || 'Unknown Agent'
    }))
  }

  // Fallback: discover agents from visits (legacy behavior)
  const agentsMap = new Map()
  props.visits.forEach(v => {
    if (v.agent && !agentsMap.has(v.agent.id)) {
      agentsMap.set(v.agent.id, {
        id: v.agent.id,
        name: v.agent.full_name || 'Unknown Agent'
      })
    }
  })
  return Array.from(agentsMap.values())
})

// Watch uniqueAgents to initialize selectedAgents once
watch(uniqueAgents, (newAgents) => {
  if (selectedAgents.value.length === 0 && newAgents.length > 0) {
    selectedAgents.value = newAgents.map(a => String(a.id))
  }
}, { immediate: true })

const toggleAgent = (id) => {
  const sId = String(id)
  const index = selectedAgents.value.indexOf(sId)
  if (index > -1) {
    selectedAgents.value.splice(index, 1)
  } else {
    selectedAgents.value.push(sId)
  }
}

const toggleAllAgents = () => {
  if (selectedAgents.value.length === uniqueAgents.value.length) {
    selectedAgents.value = []
  } else {
    selectedAgents.value = uniqueAgents.value.map(a => String(a.id))
  }
}

let timer = null
onMounted(() => {
  timer = setInterval(() => {
    now.value = new Date()
  }, 60000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

const yearOptions = computed(() => {
  const current = new Date().getFullYear()
  const years = []
  for (let i = current - 2; i <= current + 5; i++) years.push(i)
  return years
})

const daysInSelectedMonth = computed(() => {
  return new Date(selectedYear.value, selectedMonth.value + 1, 0).getDate()
})

// Time Range: 7 AM to 6 PM (18:00)
const START_HOUR = 7
const END_HOUR = 18
const hoursOfDay = Array.from({ length: END_HOUR - START_HOUR + 1 }, (_, i) => i + START_HOUR) 
const hourHeight = 80

const currentTimePosition = computed(() => {
  const h = now.value.getHours()
  const m = now.value.getMinutes()
  
  if (h < START_HOUR || h > END_HOUR) return -100 // Hide if outside range
  
  return ((h - START_HOUR) * hourHeight) + (m / 60) * hourHeight
})

const isTodaySelected = computed(() => {
  const today = new Date()
  return selectedDay.value === today.getDate() && 
         selectedMonth.value === today.getMonth() && 
         selectedYear.value === today.getFullYear()
})

const dailyVisits = computed(() => {
  return props.visits.filter(v => {
    const vDate = new Date(v.visit_date)
    const isSameDay = vDate.getFullYear() === selectedYear.value &&
                      vDate.getMonth() === selectedMonth.value &&
                      vDate.getDate() === selectedDay.value
    
    const isAgentSelected = !props.showAgentFilter || (v.agent && selectedAgents.value.includes(String(v.agent.id)))

    return isSameDay && isAgentSelected
  }).sort((a, b) => new Date(a.visit_date).getTime() - new Date(b.visit_date).getTime())
})

const positionedVisits = computed(() => {
  const events = dailyVisits.value
  const positioned = []
  
  // Group overlapping events
  const groups = []
  events.forEach(visit => {
    const vDate = new Date(visit.visit_date)
    const vStart = vDate.getHours() * 60 + vDate.getMinutes()
    const vEnd = vStart + 60 // Assume 1 hour duration
    
    // Skip if outside visible hours
    if (vDate.getHours() < START_HOUR || vDate.getHours() > END_HOUR) return

    // A visit overlaps with a group if it overlaps with ANY visit in that group
    let placed = false
    for (const group of groups) {
      const overlaps = group.some(e => {
        // Precise overlap: (StartA < EndB) and (EndA > StartB)
        // We use a small epsilon or inclusive check if they are exactly the same
        return (vStart < e.end && vEnd > e.start)
      })

      if (overlaps) {
        group.push({ visit, start: vStart, end: vEnd })
        placed = true
        break
      }
    }
    
    if (!placed) {
      groups.push([{ visit, start: vStart, end: vEnd }])
    }
  })
  
  // Calculate positions for each group
  groups.forEach(group => {
    group.forEach((item, index) => {
      const width = 100 / group.length
      const left = index * width
      const top = ((item.start / 60) - START_HOUR) * hourHeight
      const height = ((item.end - item.start) / 60) * hourHeight - 2 // small gap
      
      positioned.push({
        visit: item.visit,
        style: {
          top: `${top}px`,
          height: `${height}px`,
          left: `${left}%`,
          width: `${width}%`,
          zIndex: 10 + index
        }
      })
    })
  })
  
  return positioned
})

const goToToday = () => {
  const d = new Date()
  selectedDay.value = d.getDate()
  selectedMonth.value = d.getMonth()
  selectedYear.value = d.getFullYear()
}

const prevDay = () => {
  const d = new Date(selectedYear.value, selectedMonth.value, selectedDay.value - 1)
  selectedDay.value = d.getDate()
  selectedMonth.value = d.getMonth()
  selectedYear.value = d.getFullYear()
}

const nextDay = () => {
  const d = new Date(selectedYear.value, selectedMonth.value, selectedDay.value + 1)
  selectedDay.value = d.getDate()
  selectedMonth.value = d.getMonth()
  selectedYear.value = d.getFullYear()
}

const formatHour = (hour) => {
  if (hour === 0) return '12 AM'
  if (hour === 12) return '12 PM'
  return hour > 12 ? `${hour - 12} PM` : `${hour} AM`
}

const formatTime = (dateString) => {
  return new Date(dateString).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  })
}

const getVisitColorClass = (status) => {
  switch (status?.toLowerCase()) {
    case 'finished':
    case 'completed':
      return 'bg-emerald-50 text-emerald-700 border-emerald-500 shadow-emerald-100'
    case 'cancelled':
    case 'rejected':
      return 'bg-rose-50 text-rose-700 border-rose-500 shadow-rose-100'
    case 'scheduled':
    case 'pending':
    default:
      // "Still not" / Pending visits get a vibrant blue/amber theme
      return 'bg-blue-50 text-blue-700 border-blue-500 shadow-blue-100 animate-pulse-subtle'
  }
}
</script>

<style scoped>
.calendar-container {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e5e7eb;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #d1d5db;
}

@keyframes pulse-subtle {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.85; }
}

.animate-pulse-subtle {
  animation: pulse-subtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>

<style scoped>
.calendar-container {
  box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.05), 0 8px 10px -6px rgb(0 0 0 / 0.05);
}
</style>
