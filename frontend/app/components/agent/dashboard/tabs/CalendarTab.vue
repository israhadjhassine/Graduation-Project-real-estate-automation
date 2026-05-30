<template>
  <div>
    <div class="mb-6">
      <h2 class="text-xl font-bold text-primary-950">My Calendar</h2>
      <p class="text-xs text-primary-500 mt-1">View and manage your scheduled property visits on the timeline.</p>
    </div>
    
    <AgencyTeamCalendar 
      :visits="visits" 
      :show-agent-filter="false" 
      title="My Calendar" 
      @view-visit="$emit('view-visit', $event)" 
    />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  visits: any[]
}>()

defineEmits(['view-visit'])
</script>
