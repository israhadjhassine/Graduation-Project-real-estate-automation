<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup>
import { useAuthStore } from '~/stores/auth'
const auth = useAuthStore()

// Initialize auth on client side
if (process.client) {
  auth.init()
}
</script>
