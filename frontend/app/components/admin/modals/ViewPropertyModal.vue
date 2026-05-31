<template>
  <PropertyUploadModal 
    v-if="show"
    :show="show" 
    :edit-data="property"
    :read-only="true"
    @close="$emit('close')" 
  />
</template>

<script setup lang="ts">
defineProps<{
  show: boolean
  property: any
}>()

defineEmits<{
  (e: 'close'): void
}>()
</script>
