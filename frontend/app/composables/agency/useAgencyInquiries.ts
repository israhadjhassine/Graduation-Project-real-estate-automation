import { ref } from 'vue'
import { useAgentService } from '~/services/agentService'
import { useAlert } from '~/composables/useAlert'

export const useAgencyInquiries = (onSuccess?: () => void) => {
  const agentService = useAgentService()
  const alert = useAlert()

  // State
  const inquiries = ref<any[]>([])
  const loading = ref(false)

  // Methods
  const fetchInquiries = async () => {
    loading.value = true
    try {
      const res = await agentService.getInquiries()
      inquiries.value = res.data || []
    } catch (e) {
      console.error("Failed to fetch agency inquiries:", e)
    } finally {
      loading.value = false
    }
  }

  const updateInquiryStatus = async (inquiryId: number | string, status: string) => {
    try {
      await agentService.updateInquiryStatus(inquiryId, status)
      alert.success('Updated', 'Inquiry status has been updated.')
      if (onSuccess) {
        onSuccess()
      } else {
        await fetchInquiries()
      }
    } catch (e) {
      console.error("Failed to update inquiry status:", e)
      alert.error('Update Failed', "Could not update status.")
    }
  }

  return {
    inquiries,
    loading,
    fetchInquiries,
    updateInquiryStatus
  }
}
