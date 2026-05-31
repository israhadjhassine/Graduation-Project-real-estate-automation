import { ref } from 'vue'
import { useAdminService } from '~/services/adminService'
import { useAlert } from '~/composables/useAlert'

export const useAdminReports = () => {
  const adminService = useAdminService()
  const alert = useAlert()

  const reports = ref<any[]>([])
  const loading = ref(false)

  const fetchReports = async () => {
    loading.value = true
    try {
      const res = await adminService.getReports()
      reports.value = res.data || []
    } catch (e) {
      console.error("Failed to load reports", e)
    } finally {
      loading.value = false
    }
  }

  const downloadReport = async (report: any) => {
    try {
      if (!report.id) {
        console.error("Report ID is missing", report)
        throw new Error("Invalid report ID")
      }
      const res = await adminService.downloadReport(report.id)
      const url = window.URL.createObjectURL(res.data)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `Report_${report.property_title || 'Transaction'}.pdf`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (e) {
      console.error("Failed to download report", e)
      alert.error("Download Failed", "Could not download report.")
    }
  }

  return {
    reports,
    loading,
    fetchReports,
    downloadReport
  }
}
