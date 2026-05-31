<template>
  <AdminDashboard />
</template>

<script setup>
import AdminDashboard from '~/components/admin/dashboard/AdminDashboard.vue'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: 'dashboard' })

const auth = useAuthStore()

onMounted(() => {
  // Wait for the auth store to finish loading the token from local storage
  watchEffect(() => {
    if (auth.isInitialized) {
      if (!auth.isAdmin) {
        navigateTo('/')
      }
    }
  })
})

useHead({
  title: 'Admin Dashboard | Elite Real Estate'
})
</script>
