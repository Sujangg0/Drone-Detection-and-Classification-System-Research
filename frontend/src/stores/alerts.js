import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAlertsStore = defineStore('alerts', () => {
  const alerts = ref([
    { id: 1, time: '02:43 AM', description: 'Door breach - Building A, Floor 3, Room 305', type: 'critical', status: 'pending' },
    { id: 2, time: '02:35 AM', description: 'Motion detected - Parking Lot', type: 'warning', status: 'acknowledged' },
    { id: 3, time: '02:12 AM', description: 'Fire alarm - Building B', type: 'critical', status: 'acknowledged' },
    { id: 4, time: '01:58 AM', description: 'Camera offline - Gate 2', type: 'warning', status: 'pending' },
    { id: 5, time: '01:30 AM', description: 'System check complete', type: 'normal', status: 'acknowledged' },
  ])

  const acknowledge = (id) => {
    const alert = alerts.value.find(a => a.id === id)
    if (alert) alert.status = 'acknowledged'
  }

  const escalate = (id) => {
    // Mock escalate logic
    console.log(`Escalated alert ${id}`)
  }

  return { alerts, acknowledge, escalate }
})
