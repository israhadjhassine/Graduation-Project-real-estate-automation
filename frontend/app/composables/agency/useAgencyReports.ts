import { ref } from 'vue'
import { useAgencyService } from '~/services/agencyService'
import { useAlert } from '~/composables/useAlert'

export const useAgencyReports = () => {
  const agencyService = useAgencyService()
  const alert = useAlert()

  // State
  const reports = ref<any[]>([])
  const loading = ref(false)

  // Methods
  const fetchReports = async () => {
    loading.value = true
    try {
      const res = await agencyService.getReports()
      reports.value = res.data || []
    } catch (e) {
      console.error("Failed to fetch reports:", e)
    } finally {
      loading.value = false
    }
  }

  const downloadReport = async (report: any) => {
    try {
      const res = await agencyService.downloadReport(report.id)
      const url = window.URL.createObjectURL(res.data)
      const link = document.createElement('a')
      link.href = url
      const filename = `Report_${report.type}_${report.property_title.replace(/\s+/g, '_')}.pdf`
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
    } catch (e) {
      console.error("Failed to download report:", e)
      alert.error('Download Failed', "Could not download report.")
    }
  }

  return {
    reports,
    loading,
    fetchReports,
    downloadReport
  }
}
