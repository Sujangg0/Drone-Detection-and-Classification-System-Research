<script setup>
import { useRouter } from 'vue-router'
import { useAlertsStore } from '../stores/alerts'
import { ref, computed } from 'vue'

const router = useRouter()
const store = useAlertsStore()
const searchQuery = ref('')
const filter = ref('All')
const selectedAlert = ref(null)
const showModal = ref(false)

const filteredAlerts = computed(() => {
  let alerts = store.alerts

  // Apply search filter
  if (searchQuery.value) {
    alerts = alerts.filter(alert => 
      alert.description.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      alert.time.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  // Apply type filter
  if (filter.value !== 'All') {
    alerts = alerts.filter(alert => alert.type === filter.value.toLowerCase())
  }

  return alerts
})

const openModal = (alert) => {
  selectedAlert.value = alert
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedAlert.value = null
}

const acknowledgeAlert = () => {
  if (selectedAlert.value) {
    store.acknowledge(selectedAlert.value.id)
    closeModal()
  }
}

const escalateAlert = () => {
  if (selectedAlert.value) {
    store.escalate(selectedAlert.value.id)
    closeModal()
  }
}
</script>

<template>
  <div class="alerts-container">
    <!-- Header -->
    <header class="alerts-header">
      <div class="header-content">
        <button 
          @click="router.push('/dashboard')"
          class="back-button"
        >
          <svg style="width: 20px; height: 20px; color: white;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span>Back to Dashboard</span>
        </button>
        <h1 class="page-title">Alert Management</h1>
        <div class="spacer"></div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="alerts-main">
      <!-- Search and Filters -->
      <div class="filters-section">
        <!-- Search Bar -->
        <div class="search-wrapper">
          <svg class="search-icon" style="width: 20px; height: 20px; color: #6b7280;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search alerts by location, type, or time..."
            class="search-input"
          />
        </div>

        <!-- Quick Filters -->
        <div class="filter-buttons">
          <button
            @click="filter = 'All'"
            :class="['filter-btn', filter === 'All' ? 'active' : '']"
          >
            All Alerts
          </button>
          <button
            @click="filter = 'Critical'"
            :class="['filter-btn', filter === 'Critical' ? 'active critical' : '']"
          >
            Critical Only
          </button>
          <button
            @click="filter = 'Warning'"
            :class="['filter-btn', filter === 'Warning' ? 'active warning' : '']"
          >
            Warnings
          </button>
          <button
            @click="filter = 'Normal'"
            :class="['filter-btn', filter === 'Normal' ? 'active normal' : '']"
          >
            Normal
          </button>
        </div>
      </div>

      <!-- Alerts List -->
      <div class="alerts-list">
        <div v-if="filteredAlerts.length === 0" class="empty-state">
          <svg style="width: 64px; height: 64px; color: #9ca3af;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p>No alerts found</p>
        </div>

        <button
          v-for="alert in filteredAlerts"
          :key="alert.id"
          @click="openModal(alert)"
          :class="['alert-item', `alert-${alert.type}`]"
        >
          <div class="alert-icon-wrapper" :class="`icon-${alert.type}`">
            <svg v-if="alert.type === 'critical'" style="width: 24px; height: 24px; color: #EF4444;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <svg v-else-if="alert.type === 'warning'" style="width: 24px; height: 24px; color: #F59E0B;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else style="width: 24px; height: 24px; color: #10B981;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>

          <div class="alert-content">
            <div class="alert-header">
              <div>
                <div class="alert-badges">
                  <span class="alert-badge" :class="`badge-${alert.type}`">{{ alert.type }}</span>
                  <span class="status-badge" :class="alert.status === 'pending' ? 'pending' : 'acknowledged'">
                    {{ alert.status }}
                  </span>
                </div>
                <h3 class="alert-title">{{ alert.description }}</h3>
              </div>
              <div class="alert-time">{{ alert.time }}</div>
            </div>
            <p class="alert-subtitle">Click to view details and take action</p>
          </div>

          <svg class="arrow-icon" style="width: 20px; height: 20px; color: #9ca3af;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </main>

    <!-- Alert Detail Modal -->
    <div 
      v-if="showModal && selectedAlert" 
      class="modal-overlay"
      @click.self="closeModal"
    >
      <div class="modal-content" :class="`modal-${selectedAlert.type}`">
        <!-- Modal Header -->
        <div class="modal-header" :class="`header-${selectedAlert.type}`">
          <div class="modal-header-content">
            <div class="modal-icon-wrapper" :class="`icon-${selectedAlert.type}`">
              <svg v-if="selectedAlert.type === 'critical'" style="width: 24px; height: 24px; color: #EF4444;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <svg v-else-if="selectedAlert.type === 'warning'" style="width: 24px; height: 24px; color: #F59E0B;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <svg v-else style="width: 24px; height: 24px; color: #10B981;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h2 class="modal-title" :class="`title-${selectedAlert.type}`">{{ selectedAlert.type }} Alert</h2>
              <p class="modal-subtitle">Alert Details</p>
            </div>
          </div>
          <button @click="closeModal" class="close-button">
            <svg style="width: 24px; height: 24px; color: #6b7280;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Modal Body -->
        <div class="modal-body">
          <div class="modal-info-box">
            <div class="info-item">
              <label>Description</label>
              <p>{{ selectedAlert.description }}</p>
            </div>
            <div class="info-grid">
              <div class="info-item">
                <label>Time</label>
                <p class="info-time">{{ selectedAlert.time }}</p>
              </div>
              <div class="info-item">
                <label>Status</label>
                <p class="info-status" :class="selectedAlert.status === 'pending' ? 'pending' : 'acknowledged'">
                  {{ selectedAlert.status }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Actions -->
        <div class="modal-actions">
          <button @click="acknowledgeAlert" class="action-btn acknowledge-btn">
            ✓ Acknowledge Alert
          </button>
          <button @click="escalateAlert" class="action-btn escalate-btn">
            ↑ Escalate Alert
          </button>
          <button @click="closeModal" class="action-btn close-btn">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.alerts-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 50%, #f3e8ff 100%);
  color: #111827;
  font-family: system-ui, -apple-system, sans-serif;
}

/* Header */
.alerts-header {
  background: white;
  border-bottom: 2px solid #bfdbfe;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
  color: white;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.back-button:hover {
  transform: translateX(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e40af;
}

.spacer {
  width: 96px;
}

/* Main Content */
.alerts-main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.filters-section {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.search-wrapper {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  background: white;
  border: 2px solid #bfdbfe;
  border-radius: 12px;
  font-size: 1rem;
  color: #111827;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.filter-btn {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  border: 2px solid #d1d5db;
  background: white;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.filter-btn.active {
  background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
  color: white;
  border-color: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.filter-btn.active.critical {
  background: linear-gradient(135deg, #EF4444 0%, #dc2626 100%);
  border-color: #EF4444;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.filter-btn.active.warning {
  background: linear-gradient(135deg, #F59E0B 0%, #d97706 100%);
  border-color: #F59E0B;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.filter-btn.active.normal {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  border-color: #10B981;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

/* Alerts List */
.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}

.alert-item {
  width: 100%;
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  border: 2px solid;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
}

.alert-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.alert-critical {
  border-color: #EF4444;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
}

.alert-warning {
  border-color: #F59E0B;
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
}

.alert-normal {
  border-color: #10B981;
  background: linear-gradient(135deg, #f0fdf4 0%, #d1fae5 100%);
}

.alert-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-critical {
  background: #fee2e2;
}

.icon-warning {
  background: #fef3c7;
}

.icon-normal {
  background: #d1fae5;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.alert-badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.alert-badge {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  text-transform: uppercase;
}

.badge-critical {
  background: #fee2e2;
  color: #991b1b;
}

.badge-warning {
  background: #fef3c7;
  color: #92400e;
}

.badge-normal {
  background: #d1fae5;
  color: #065f46;
}

.status-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.status-badge.pending {
  background: #fed7aa;
  color: #9a3412;
}

.status-badge.acknowledged {
  background: #dbeafe;
  color: #1e40af;
}

.alert-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.25rem;
}

.alert-time {
  font-size: 0.875rem;
  font-family: 'Courier New', monospace;
  font-weight: 600;
  color: #4b5563;
  white-space: nowrap;
}

.alert-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
}

.arrow-icon {
  flex-shrink: 0;
  margin-top: 0.25rem;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  z-index: 50;
}

.modal-content {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  max-width: 28rem;
  width: 100%;
  overflow: hidden;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 2px solid;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-critical {
  border-color: #fecaca;
  background: #fef2f2;
}

.header-warning {
  border-color: #fde68a;
  background: #fffbeb;
}

.header-normal {
  border-color: #bbf7d0;
  background: #f0fdf4;
}

.modal-header-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.modal-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  text-transform: uppercase;
}

.title-critical {
  color: #EF4444;
}

.title-warning {
  color: #F59E0B;
}

.title-normal {
  color: #10B981;
}

.modal-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
}

.close-button {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  transition: all 0.2s;
}

.close-button:hover {
  transform: scale(1.1);
}

.modal-body {
  padding: 1.5rem;
}

.modal-info-box {
  background: #f9fafb;
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #e5e7eb;
}

.info-item {
  margin-bottom: 0.75rem;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item label {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: block;
  margin-bottom: 0.25rem;
}

.info-item p {
  font-weight: 500;
  color: #111827;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 0.75rem;
}

.info-time {
  font-family: 'Courier New', monospace;
  font-weight: 600;
}

.info-status {
  font-weight: 600;
  text-transform: uppercase;
}

.info-status.pending {
  color: #ea580c;
}

.info-status.acknowledged {
  color: #2563eb;
}

.modal-actions {
  padding: 1rem 1.5rem;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.action-btn {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.acknowledge-btn {
  background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.acknowledge-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
}

.escalate-btn {
  background: linear-gradient(135deg, #EF4444 0%, #dc2626 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.escalate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(239, 68, 68, 0.4);
}

.close-btn {
  background: #e5e7eb;
  color: #374151;
}

.close-btn:hover {
  background: #d1d5db;
}
</style>
