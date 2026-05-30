<template>
  <div class="bg-primary-50/20 min-h-screen py-12">
    <div class="max-w-7xl mx-auto px-6">
      <!-- Head Agent Header -->
      <AgencyHeader @list-new="showModal = true" />



      <!-- Quick Stats -->
      <AgencyStats :properties-count="properties.length" :staff-count="staff.length" />

      <!-- Navigation Tabs -->
      <AgencyTabs 
        v-model:active-tab="activeTab" 
        :pending-sales-count="pendingSales.length" 
        :show-reports-tab="auth.isAdmin || auth.isHeadAgent" 
      />

      <!-- Tab Content: Properties -->
      <div v-show="activeTab === 'properties'">
        <PropertiesTab 
          :properties="activeProperties" 
          :staff="staff" 
          :current-user-id="auth.user?.id" 
          :is-admin="auth.isAdmin" 
          @view-property="viewProperty" 
          @edit-property="editProperty" 
          @delete-property="deleteProperty" 
          @assign-agent="assignAgent" 
        />
      </div>

      <!-- Tab Content: Staff Team -->
      <div v-show="activeTab === 'staff'">
        <StaffTab 
          :staff="staff" 
          :properties="properties" 
          @toggle-status="toggleAgentStatus" 
        />
      </div>

      <!-- Tab Content: Team Schedule -->
      <div v-show="activeTab === 'schedule'">
        <ScheduleTab 
          :visits="visits" 
          :staff="staff" 
          @view-visit="viewVisitDetails" 
        />
      </div>

      <!-- Tab Content: Sold Properties -->
      <div v-show="activeTab === 'sold'">
        <SoldTab 
          :properties="soldProperties" 
          :staff="staff" 
          :clients="clients" 
          @view-property="viewProperty" 
        />
      </div>

      <!-- Tab Content: Rented Properties -->
      <div v-show="activeTab === 'rented'">
        <RentedTab 
          :properties="rentedProperties" 
          :staff="staff" 
          :clients="clients" 
          @view-property="viewProperty" 
        />
      </div>

      <!-- Tab Content: Approvals -->
      <div v-show="activeTab === 'inquiries'">
        <InquiriesTab 
          :inquiries="inquiries" 
          @update-status="updateInquiryStatus" 
        />
      </div>

      <!-- Tab Content: Analytics -->
      <div v-show="activeTab === 'analytics'">
        <AnalyticsTab 
          :loading="loading"
          :property-status-chart-data="propertyStatusChartData"
          :agent-performance-chart-data="agentPerformanceChartData"
        />
      </div>

      <!-- Tab Content: Reports -->
      <div v-show="activeTab === 'reports' && (auth.isAdmin || auth.isHeadAgent)">
        <ReportsTab 
          :reports="reports" 
          @download-report="downloadReport" 
        />
      </div>
    </div>

    <PropertyUploadModal 
      :show="showModal" 
      :edit-data="selectedProperty"
      :read-only="isReadOnly"
      @close="handleClose" 
      @success="handleSuccess"
    />

    <VisitDetailsModal 
      v-if="selectedVisit"
      :isOpen="isVisitModalOpen"
      :visit="selectedVisit"
      @close="isVisitModalOpen = false"
    />

  </div>
</template>

<script setup>
import { 
  LucideBriefcase, LucideHome, LucideUsers, LucideEye,
  LucidePlus, LucideImage, LucideEdit, LucideTrash2,
  LucideUserPlus, LucideX, LucideCheckCircle2,
  LucideMessageSquare, LucideFileText, LucideDownload, LucidePieChart,
  LucideCalendar
} from 'lucide-vue-next'
import { useAuthStore } from '~/stores/auth'
import { useAssetUrl } from '~/composables/useAssetUrl'
import { useAgencyDashboard } from '~/composables/useAgencyDashboard'
import VisitDetailsModal from '~/components/agency/VisitDetailsModal.vue'
import AgencyHeader from '~/components/agency/dashboard/AgencyHeader.vue'
import AgencyStats from '~/components/agency/dashboard/AgencyStats.vue'
import AgencyTabs from '~/components/agency/dashboard/AgencyTabs.vue'
import PropertiesTab from '~/components/agency/dashboard/tabs/PropertiesTab.vue'
import StaffTab from '~/components/agency/dashboard/tabs/StaffTab.vue'
import ScheduleTab from '~/components/agency/dashboard/tabs/ScheduleTab.vue'
import SoldTab from '~/components/agency/dashboard/tabs/SoldTab.vue'
import RentedTab from '~/components/agency/dashboard/tabs/RentedTab.vue'
import InquiriesTab from '~/components/agency/dashboard/tabs/InquiriesTab.vue'
import AnalyticsTab from '~/components/agency/dashboard/tabs/AnalyticsTab.vue'
import ReportsTab from '~/components/agency/dashboard/tabs/ReportsTab.vue'

definePageMeta({ layout: 'dashboard' })

const auth = useAuthStore()
const { getPublicUrl } = useAssetUrl()
const activeTab = ref('properties')

const {
  properties, staff, inquiries, reports, clients, visits, loading, statistics,
  soldProperties, rentedProperties, activeProperties, pendingSales,
  propertyStatusChartData, agentPerformanceChartData,
  fetchData, deleteProperty, assignAgent, updateInquiryStatus,
  toggleAgentStatus, downloadReport
} = useAgencyDashboard()

const isVisitModalOpen = ref(false)
const selectedVisit = ref(null)

const showModal = ref(false)
const selectedProperty = ref(null)
const isReadOnly = ref(false)

const editProperty = (prop) => {
  isReadOnly.value = false
  selectedProperty.value = prop
  showModal.value = true
}

const viewProperty = (prop) => {
  isReadOnly.value = true
  selectedProperty.value = prop
  showModal.value = true
}

const viewVisitDetails = (visit) => {
  selectedVisit.value = visit
  isVisitModalOpen.value = true
}

const handleSuccess = () => {
  showModal.value = false
  selectedProperty.value = null
  fetchData()
}

const handleClose = () => {
  showModal.value = false
  selectedProperty.value = null
  isReadOnly.value = false
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('fr-TN').format(price)
}

onMounted(() => {
  watchEffect(() => {
    if (auth.isInitialized) {
      if (!auth.isHeadAgent && !auth.isAdmin) {
        navigateTo('/')
      } else {
        fetchData()
      }
    }
  })
})

useHead({
  title: 'Agency Dashboard | Elite Real Estate'
})
</script>
