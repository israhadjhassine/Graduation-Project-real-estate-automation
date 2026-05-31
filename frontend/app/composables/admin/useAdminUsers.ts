import { ref, computed } from 'vue'
import { useAdminService } from '~/services/adminService'
import { useAlert } from '~/composables/useAlert'

export const useAdminUsers = () => {
  const adminService = useAdminService()
  const alert = useAlert()
  
  const users = ref<any[]>([])
  const loading = ref(false)
  const userSearchQuery = ref('')
  const userRoleFilter = ref('all')
  const userStatusFilter = ref('all')

  const filteredUsers = computed(() => {
    return users.value.filter(u => {
      const matchesSearch = !userSearchQuery.value || 
        u.full_name.toLowerCase().includes(userSearchQuery.value.toLowerCase())
      
      const matchesRole = userRoleFilter.value === 'all' || u.role === userRoleFilter.value
      
      const matchesStatus = userStatusFilter.value === 'all' || 
        (userStatusFilter.value === 'active' ? u.is_active : !u.is_active)
        
      const isStaff = u.role !== 'client'
        
      return matchesSearch && matchesRole && matchesStatus && isStaff
    })
  })

  const headAgents = computed(() => users.value.filter(u => u.role === 'head_agent'))

  const fetchUsers = async () => {
    loading.value = true
    try {
      const res = await adminService.getUsers()
      users.value = res.data || []
    } catch (e) {
      console.error("Failed to load users", e)
    } finally {
      loading.value = false
    }
  }

  const createUser = async (payload: any) => {
    loading.value = true
    try {
      await adminService.createUser(payload)
      await fetchUsers()
    } catch (e: any) {
      console.error("Failed to create user", e)
      throw new Error(e.response?.data?.detail || "Failed to create user")
    } finally {
      loading.value = false
    }
  }

  const toggleUserStatus = async (userId: number | string) => {
    try {
      await adminService.toggleUserStatus(userId)
      await fetchUsers()
    } catch (e: any) {
      console.error("Failed to toggle user status", e)
      alert.error("Status Update Failed", e.response?.data?.detail || "Failed to update account status")
    }
  }

  return {
    users,
    loading,
    userSearchQuery,
    userRoleFilter,
    userStatusFilter,
    filteredUsers,
    headAgents,
    fetchUsers,
    createUser,
    toggleUserStatus
  }
}
