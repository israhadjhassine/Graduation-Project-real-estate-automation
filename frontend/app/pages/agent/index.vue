<template>
  <div class="bg-primary-50/20 min-h-screen py-12">
    <div class="max-w-7xl mx-auto px-6">
      <!-- Sub-Agent Header -->
      <AgentHeader />

      <!-- Quick Stats -->
      <AgentStats 
        :my-properties="myProperties" 
        :upcoming-visits="upcomingVisits" 
        :finished-visits="finishedVisits" 
      />

      <!-- Navigation Tabs -->
      <AgentTabs 
        :active-tab="activeTab" 
        @update:active-tab="activeTab = $event" 
      />


      <!-- Tab Content: Analytics -->
      <div v-show="activeTab === 'analytics'">
        <AgentAnalyticsTab 
          :stats-loading="statsLoading"
          :visit-chart-data="visitChartData"
          :monthly-visits-chart-data="monthlyVisitsChartData"
          :property-status-chart-data="propertyStatusChartData"
        />
      </div>

      <!-- Tab Content: Properties -->
      <div v-show="activeTab === 'properties'">
        <PortfolioTab 
          :my-properties="myProperties" 
          @view-property="viewProperty" 
          @open-sale-modal="openSaleModal" 
          @open-rent-modal="openRentModal" 
        />
      </div>
      <div v-show="activeTab === 'visits'">
        <VisitsTab 
          v-model:searchQuery="searchQuery"
          v-model:locationQuery="locationQuery"
          v-model:statusFilter="statusFilter"
          v-model:dateFilter="dateFilter"
          :filtered-visits="filteredVisits"
          :visits="visits"
          @view-details="viewVisitDetails"
          @update-status="updateVisitStatus"
        />
      </div>

    </div>

    <!-- Details Modal -->
    <VisitDetailsModal 
      v-if="selectedVisit"
      :isOpen="isVisitModalOpen"
      :visit="selectedVisit"
      @close="isVisitModalOpen = false"
    />

    <!-- Sale Request Modal -->
    <SaleRequestModal 
      :show="showSaleModal"
      v-model:selectedClientId="selectedClientId"
      :clients="clients"
      @close="showSaleModal = false"
      @submit="submitSaleRequest"
    />

    <!-- Rent Request Modal -->
    <RentRequestModal 
      :show="showRentModal"
      v-model:selectedClientId="selectedClientId"
      v-model:rentStartDate="rentStartDate"
      v-model:rentEndDate="rentEndDate"
      :clients="clients"
      @close="showRentModal = false"
      @submit="submitRentRequest"
    />
    
    <PropertyUploadModal 
      :show="showDetailsModal" 
      :edit-data="selectedProperty"
      :read-only="isReadOnly"
      @close="handleClose" 
    />
  </div>
</template>

<script setup>
import { 
  LucideHeadset, LucideHome, LucideCalendar, 
  LucideCheckCircle2, LucideXCircle, LucideX,
  LucideCheck, LucidePieChart, LucideCalendarOff,
  LucideSearch, LucideMapPin, LucideFilter, LucideEye
} from 'lucide-vue-next'
import VisitDetailsModal from '~/components/agency/VisitDetailsModal.vue'

import SaleRequestModal from '~/components/agent/dashboard/modals/SaleRequestModal.vue'
import RentRequestModal from '~/components/agent/dashboard/modals/RentRequestModal.vue'
import { useAuthStore } from '~/stores/auth'
import { useAlert } from '~/composables/useAlert'
import { useAgentDashboard } from '~/composables/useAgentDashboard'

import AgentHeader from '~/components/agent/dashboard/AgentHeader.vue'
import AgentStats from '~/components/agent/dashboard/AgentStats.vue'
import AgentTabs from '~/components/agent/dashboard/AgentTabs.vue'
import VisitsTab from '~/components/agent/dashboard/tabs/VisitsTab.vue'
import PortfolioTab from '~/components/agent/dashboard/tabs/PortfolioTab.vue'
import AgentAnalyticsTab from '~/components/agent/dashboard/tabs/AgentAnalyticsTab.vue'

definePageMeta({ layout: 'dashboard' })

const auth = useAuthStore()
const alert = useAlert()
const activeTab = ref('visits')

const {
  visits, myProperties, clients, statistics, searchQuery, locationQuery,
  statusFilter, dateFilter, loading, statsLoading,
  upcomingVisits, finishedVisits, filteredVisits, visitChartData,
  propertyStatusChartData, monthlyVisitsChartData,
  fetchData, submitSaleRequest: doSubmitSaleRequest, submitRentRequest: doSubmitRentRequest, updateVisitStatus
} = useAgentDashboard()

const showDetailsModal = ref(false)
const selectedProperty = ref(null)
const isReadOnly = ref(false)

const viewProperty = (prop) => {
  isReadOnly.value = true
  selectedProperty.value = prop
  showDetailsModal.value = true
}

const handleClose = () => {
  showDetailsModal.value = false
  selectedProperty.value = null
  isReadOnly.value = false
}


const showSaleModal = ref(false)
const selectedSalePropertyId = ref(null)
const selectedClientId = ref('')

const isVisitModalOpen = ref(false)
const selectedVisit = ref(null)

const viewVisitDetails = (visit) => {
  selectedVisit.value = visit
  isVisitModalOpen.value = true
}

const openSaleModal = (id) => {
  selectedSalePropertyId.value = id
  selectedClientId.value = ''
  showSaleModal.value = true
}

const submitSaleRequest = async () => {
  if (!selectedClientId.value) {
    alert.error("Selection Required", "Please select a registered client.")
    return
  }
  try {
    await doSubmitSaleRequest(selectedSalePropertyId.value, selectedClientId.value)
    fetchData()
    showSaleModal.value = false
    alert.success("Sale Request Sent", "Your head agent will review and approve.")
  } catch (e) {
    console.error("Failed to request sale", e)
    alert.error("Submission Failed", e.response?.data?.detail || "Failed to submit sale request.")
  }
}

const showRentModal = ref(false)
const selectedRentPropertyId = ref(null)
const rentStartDate = ref('')
const rentEndDate = ref('')

const openRentModal = (id) => {
  selectedRentPropertyId.value = id
  rentStartDate.value = ''
  rentEndDate.value = ''
  selectedClientId.value = ''
  showRentModal.value = true
}

const submitRentRequest = async () => {
  if (!selectedClientId.value) {
    alert.error("Selection Required", "Please select a registered client.")
    return
  }
  if (!rentStartDate.value || !rentEndDate.value) {
    alert.error("Date Required", "Please select both start and end dates.")
    return
  }
  
  try {
    await doSubmitRentRequest(selectedRentPropertyId.value, selectedClientId.value, rentStartDate.value, rentEndDate.value)
    showRentModal.value = false
    fetchData()
    alert.success("Rent Request Sent", "Your head agent will review and approve.")
  } catch (e) {
    console.error("Failed to request rent", e)
    alert.error("Submission Failed", e.response?.data?.detail || "Failed to submit rent request.")
  }
}

onMounted(() => {
  // Allow Head Agents and Admins to view this dashboard too for demonstration/testing
  watchEffect(() => {
    if (auth.isInitialized) {
      if (!auth.isAgent && !auth.isHeadAgent && !auth.isAdmin) {
        navigateTo('/')
      } else {
        fetchData()
      }
    }
  })
})

useHead({
  title: 'Agent Workspace | Elite Real Estate'
})
</script>
