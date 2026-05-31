<template>
  <div class="bg-primary-50/20 min-h-screen py-12">
    <div class="max-w-7xl mx-auto px-6">
      <!-- Admin Header -->
      <AdminHeader />

      <!-- Quick Stats -->
      <AdminStats
        :users-length="users.length"
        :head-agents-length="headAgents.length"
        :properties-length="properties.length"
        :visits-length="visits.length"
        :closed-deals-count="closedDealsCount"
      />

      <!-- Navigation Tabs -->
      <AdminTabs v-model:activeTab="activeTab" />

      <!-- Tab Content: Users -->
      <AdminUsersTab
        v-show="activeTab === 'users'"
        v-model:searchQuery="userSearchQuery"
        v-model:roleFilter="userRoleFilter"
        v-model:statusFilter="userStatusFilter"
        :filtered-users="filteredUsers"
        :auth="auth"
        @create-user="showUserModal = true"
        @toggle-status="toggleUserStatus"
      />

      <!-- Tab Content: Properties -->
      <AdminPropertiesTab
        v-show="activeTab === 'properties'"
        v-model:propSearchQuery="propSearchQuery"
        v-model:propLocationQuery="propLocationQuery"
        :filtered-properties="filteredProperties"
        :properties="properties"
        @view-property="viewProperty"
      />

      <!-- Tab Content: Analytics -->
      <AdminAnalyticsTab
        v-show="activeTab === 'analytics'"
        :stats-loading="statsLoading"
        :statistics="statistics"
        :user-roles-chart-data="userRolesChartData"
        :top-agents-chart-data="topAgentsChartData"
        :property-status-chart-data="propertyStatusChartData"
      />

      <!-- Tab Content: Reports -->
      <AdminReportsTab
        v-show="activeTab === 'reports'"
        :reports="reports"
        @download-report="downloadReport"
      />

    </div>

    <!-- User Creation Modal -->
    <CreateUserModal
      :show="showUserModal"
      :head-agents="headAgents"
      :loading="loading"
      :error="userError"
      @close="showUserModal = false"
      @submit="handleCreateUser"
    />

    <!-- View Property Modal -->
    <ViewPropertyModal
      :show="showPropertyModal"
      :property="selectedProperty"
      @close="closePropertyModal"
    />

  </div>
</template>

<script setup lang="ts">
import AdminHeader from './AdminHeader.vue'
import AdminStats from './AdminStats.vue'
import AdminTabs from './AdminTabs.vue'
import AdminUsersTab from './tabs/AdminUsersTab.vue'
import AdminPropertiesTab from './tabs/AdminPropertiesTab.vue'
import AdminAnalyticsTab from './tabs/AdminAnalyticsTab.vue'
import AdminReportsTab from './tabs/AdminReportsTab.vue'

import CreateUserModal from '../modals/CreateUserModal.vue'
import ViewPropertyModal from '../modals/ViewPropertyModal.vue'

import { useAuthStore } from '~/stores/auth'
import { useAdminDashboard } from '~/composables/useAdminDashboard'

const auth = useAuthStore()

// Domain Composable Orchestration
const {
  users, properties, reports, statistics, visits,
  loading, statsLoading,
  userSearchQuery, userRoleFilter, userStatusFilter,
  propSearchQuery, propLocationQuery,
  filteredUsers, filteredProperties,
  userRolesChartData, topAgentsChartData, propertyStatusChartData,
  headAgents, closedDealsCount,
  fetchData, createUser, toggleUserStatus, downloadReport
} = useAdminDashboard()

// UI State
const activeTab = ref('users')

const showUserModal = ref(false)
const userError = ref('')

const showPropertyModal = ref(false)
const selectedProperty = ref<any>(null)

// UI Handlers
const handleCreateUser = async (formPayload: any) => {
  userError.value = ''
  
  // Format payload
  const payload = { ...formPayload }
  if (!payload.manager_id || payload.role !== 'agent') {
    payload.manager_id = null
  } else {
    payload.manager_id = parseInt(payload.manager_id)
  }

  try {
    await createUser(payload)
    showUserModal.value = false
  } catch (e: any) {
    userError.value = e.message || "Failed to create user"
  }
}

const viewProperty = (property: any) => {
  selectedProperty.value = property
  showPropertyModal.value = true
}

const closePropertyModal = () => {
  showPropertyModal.value = false
  selectedProperty.value = null
}

onMounted(() => {
  // Wait for the auth store to finish loading the token from local storage
  watchEffect(() => {
    if (auth.isInitialized) {
      if (auth.isAdmin) {
        fetchData()
      }
    }
  })
})
</script>
