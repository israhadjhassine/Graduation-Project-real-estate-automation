<template>
  <div>
    <div class="mb-6">
      <h2 class="text-xl font-bold text-primary-950">Team Visit Schedule</h2>
      <p class="text-xs text-primary-500 mt-1">Consolidated view of all upcoming visits across your sub-agent team.</p>
    </div>
    
    <AgencyTeamCalendar :visits="visits" :agents="staff" @view-visit="$emit('view-visit', $event)" />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  visits: any[]
  staff: any[]
}>()

defineEmits(['view-visit'])
</script>
