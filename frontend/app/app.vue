<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup>
import { useAuthStore } from '~/stores/auth'
const auth = useAuthStore()

// Run auth init on client only, after DOM mount
// This ensures auth.isInitialized is set before the navbar renders user info
onMounted(async () => {
  await auth.init()
})
</script>
