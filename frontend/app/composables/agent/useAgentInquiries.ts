import { ref } from 'vue'
import { useAgentService } from '~/services/agentService'

export const useAgentInquiries = () => {
  const agentService = useAgentService()

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
      console.error("Failed to fetch inquiries:", e)
    } finally {
      loading.value = false
    }
  }

  return {
    inquiries,
    loading,
    fetchInquiries
  }
}
