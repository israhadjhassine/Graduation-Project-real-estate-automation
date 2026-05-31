import { ref } from 'vue'
import { useAgencyService } from '~/services/agencyService'
import { useAlert } from '~/composables/useAlert'

export const useAgencyStaff = (onSuccess?: () => void) => {
  const agencyService = useAgencyService()
  const alert = useAlert()

  // State
  const staff = ref<any[]>([])
  const loading = ref(false)

  // Methods
  const fetchStaff = async () => {
    loading.value = true
    try {
      const res = await agencyService.getStaff()
      staff.value = res.data || []
    } catch (e) {
      console.error("Failed to fetch agency staff:", e)
    } finally {
      loading.value = false
    }
  }

  const toggleAgentStatus = async (agentId: number | string) => {
    try {
      await agencyService.toggleAgentStatus(agentId)
      if (onSuccess) {
        onSuccess()
      } else {
        await fetchStaff()
      }
    } catch (e: any) {
      console.error("Failed to toggle agent status:", e)
      alert.error('Status Update Failed', e.response?.data?.detail || 'Failed to update status')
    }
  }

  return {
    staff,
    loading,
    fetchStaff,
    toggleAgentStatus
  }
}
