<script setup>
import { useRouter } from 'vue-router'
import { useAlertsStore } from '../stores/alerts'
import { useAuthStore } from '../stores/auth'
import { computed, ref, onMounted, onUnmounted } from 'vue'

const router = useRouter()
const store = useAlertsStore()
const authStore = useAuthStore()

// View mode toggle
const viewMode = ref('normal')

// Computed alert counts
const criticalCount = computed(() => store.alerts.filter(a => a.type === 'critical').length)
const warningCount = computed(() => store.alerts.filter(a => a.type === 'warning').length)
const normalCount = computed(() => store.alerts.filter(a => a.type === 'normal').length)

// Current time - updates every second
const currentTime = computed(() => {
  const now = new Date()
  return now.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit',
    hour12: true 
  })
})

// Force reactivity update for time
let timeInterval = null
onMounted(() => {
  timeInterval = setInterval(() => {
    // Time updates automatically via computed
  }, 1000)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
})

// Operator status
const operatorStatus = ref('ACTIVE')

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="dashboard-container">
    <!-- Top Header Bar -->
    <header class="dashboard-header">
      <div class="header-content">
        <div class="header-top">
          <!-- Logo Section -->
          <div class="logo-section">
            <!-- RF Wave/Drone Icon -->
            <div class="logo-icon">
              <svg style="width: 28px; height: 28px; color: white;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
              </svg>
            </div>
            <!-- AirFence Text Logo -->
            <div>
              <h1 class="logo-text">AirFence</h1>
              <p class="logo-subtitle">Drone Detection System</p>
            </div>
          </div>

          <!-- Top Right Info Bar -->
          <div class="header-info">
            <!-- Current Time -->
            <div class="time-box">
              <div class="time-label">Current Time</div>
              <div class="time-value">{{ currentTime }}</div>
            </div>

            <!-- View Mode Toggle -->
            <div class="view-mode-box">
              <div class="view-mode-label">View Mode</div>
              <div class="view-mode-buttons">
                <button
                  @click="viewMode = 'normal'"
                  :class="['view-mode-btn', viewMode === 'normal' ? 'active' : '']"
                  aria-label="Normal View Mode"
                >
                  NORMAL
                </button>
                <button
                  @click="viewMode = 'simple'"
                  :class="['view-mode-btn', viewMode === 'simple' ? 'active' : '']"
                  aria-label="Simple View Mode"
                >
                  SIMPLE
                </button>
              </div>
            </div>

            <!-- Operator Status -->
            <div class="status-box">
              <div class="status-label">Operator Status</div>
              <div class="status-value">
                <span class="status-dot"></span>
                {{ operatorStatus }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Alert Status Cards -->
      <div class="cards-grid">
        <!-- Critical Alerts Card -->
        <button
          @click="router.push('/alerts')"
          class="alert-card critical-card"
          :aria-label="`Critical Alerts: ${criticalCount} alerts. Click to view details.`"
        >
          <div class="card-content">
            <div class="card-icon critical-icon">
              <svg style="width: 40px; height: 40px; color: #EF4444;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h2 class="card-title critical-title">Critical Alerts</h2>
            <div class="card-number critical-number">{{ criticalCount }}</div>
          </div>
          <div class="card-footer critical-footer">
            <p>Click to view details →</p>
          </div>
        </button>

        <!-- Warning Alerts Card -->
        <button
          @click="router.push('/alerts')"
          class="alert-card warning-card"
          :aria-label="`Warning Alerts: ${warningCount} alerts. Click to view details.`"
        >
          <div class="card-content">
            <div class="card-icon warning-icon">
              <svg style="width: 40px; height: 40px; color: #F59E0B;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 class="card-title warning-title">Warning Alerts</h2>
            <div class="card-number warning-number">{{ warningCount }}</div>
          </div>
          <div class="card-footer warning-footer">
            <p>Click to view details →</p>
          </div>
        </button>

        <!-- Normal Status Card -->
        <div class="alert-card normal-card" :aria-label="`Normal Status: ${normalCount} systems operating normally`">
          <div class="card-content">
            <div class="card-icon normal-icon">
              <svg style="width: 40px; height: 40px; color: #10B981;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 class="card-title normal-title">Normal Status</h2>
            <div class="card-number normal-number">{{ normalCount }}</div>
          </div>
          <div class="card-footer normal-footer">
            <p>All systems operational</p>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="actions-grid">
        <!-- View Alert History Button -->
        <button
          @click="router.push('/alerts')"
          class="action-btn primary-btn"
          aria-label="View Alert History"
        >
          <div class="btn-content">
            <div class="btn-icon">
              <svg style="width: 28px; height: 28px; color: white;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <div class="btn-text">
              <div class="btn-title">View Alert History</div>
              <div class="btn-subtitle">Review complete alert history and manage incidents</div>
            </div>
          </div>
          <svg style="width: 32px; height: 32px; color: white;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
          </svg>
        </button>

        <!-- End Shift / Handover Button -->
        <button
          @click="router.push('/shift-summary')"
          class="action-btn secondary-btn"
          aria-label="End Shift and Handover"
        >
          <div class="btn-content">
            <div class="btn-icon">
              <svg style="width: 28px; height: 28px; color: white;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div class="btn-text">
              <div class="btn-title">End Shift / Handover</div>
              <div class="btn-subtitle">Complete shift summary and handover to next operator</div>
            </div>
          </div>
          <svg style="width: 32px; height: 32px; color: white;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </main>
  </div>
</template>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 50%, #f3e8ff 100%);
  color: #111827;
  font-family: system-ui, -apple-system, sans-serif;
}

/* Header Styles */
.dashboard-header {
  background: white;
  border-bottom: 2px solid #bfdbfe;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 1rem;
}

.header-top {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.25rem 0;
}

@media (min-width: 768px) {
  .header-top {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.logo-text {
  font-size: 1.875rem;
  font-weight: 700;
  background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.025em;
}

.logo-subtitle {
  font-size: 0.75rem;
  color: #4b5563;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.header-info {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
}

@media (min-width: 768px) {
  .header-info {
    gap: 1.5rem;
  }
}

.time-box {
  background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%);
  padding: 0.75rem 1.25rem;
  border-radius: 12px;
  border: 2px solid #93c5fd;
  min-width: 180px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.time-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #1e40af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.time-value {
  font-size: 1.5rem;
  font-family: 'Courier New', monospace;
  font-weight: 700;
  color: #2563eb;
  font-variant-numeric: tabular-nums;
}

.view-mode-box {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  padding: 0.75rem 1rem;
  border-radius: 12px;
  border: 2px solid #d1d5db;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.view-mode-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
  text-align: center;
}

.view-mode-buttons {
  display: flex;
  background: white;
  border-radius: 8px;
  padding: 0.25rem;
  gap: 0.25rem;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.view-mode-btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.875rem;
  min-height: 44px;
  flex: 1;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  color: #374151;
  background: transparent;
}

.view-mode-btn:hover {
  background: #f3f4f6;
}

.view-mode-btn.active {
  background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
}

.status-box {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  padding: 0.75rem 1.25rem;
  border-radius: 12px;
  border: 2px solid #34d399;
  min-width: 160px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.status-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #065f46;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.status-value {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: #059669;
}

.status-dot {
  width: 12px;
  height: 12px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Main Content */
.main-content {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.cards-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

@media (min-width: 768px) {
  .cards-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.alert-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  min-height: 320px;
  display: flex;
  flex-direction: column;
  text-align: left;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  overflow: hidden;
}

.alert-card:hover {
  transform: scale(1.05);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.alert-card:focus {
  outline: 4px solid;
  outline-offset: 2px;
}

.critical-card {
  border: 4px solid #EF4444;
}

.critical-card:hover {
  border-color: #dc2626;
}

.warning-card {
  border: 2px solid #F59E0B;
}

.warning-card:hover {
  border-color: #d97706;
}

.normal-card {
  border: 1px solid #10B981;
  cursor: default;
}

.normal-card:hover {
  transform: none;
}

.card-content {
  padding: 2rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.card-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.critical-icon {
  background: #fee2e2;
}

.warning-icon {
  background: #fef3c7;
}

.normal-icon {
  background: #d1fae5;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.critical-title {
  color: #EF4444;
  font-size: 1.5rem;
}

.warning-title {
  color: #F59E0B;
}

.normal-title {
  color: #10B981;
}

.card-number {
  font-size: 4.5rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

.critical-number {
  color: #EF4444;
  font-size: 5rem;
}

.warning-number {
  color: #F59E0B;
  font-size: 4rem;
}

.normal-number {
  color: #10B981;
  font-size: 4rem;
}

.card-footer {
  padding: 1rem 1.5rem;
  border-top: 2px solid;
  font-size: 0.875rem;
  font-weight: 600;
  text-align: center;
}

.critical-footer {
  background: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
}

.warning-footer {
  background: #fffbeb;
  border-color: #fde68a;
  color: #92400e;
}

.normal-footer {
  background: #f0fdf4;
  border-color: #bbf7d0;
  color: #065f46;
}

/* Action Buttons */
.actions-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.action-btn {
  background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
  color: white;
  font-weight: 700;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
  min-height: 90px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 2rem;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
  background: linear-gradient(135deg, #1d4ed8 0%, #4338ca 100%);
}

.action-btn:focus {
  outline: 4px solid #93c5fd;
  outline-offset: 2px;
}

.secondary-btn {
  background: linear-gradient(135deg, #9333ea 0%, #ec4899 100%);
  box-shadow: 0 4px 12px rgba(147, 51, 234, 0.3);
}

.secondary-btn:hover {
  background: linear-gradient(135deg, #7e22ce 0%, #db2777 100%);
  box-shadow: 0 8px 20px rgba(147, 51, 234, 0.4);
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-icon {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.btn-text {
  text-align: left;
}

.btn-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.btn-subtitle {
  font-size: 0.875rem;
  opacity: 0.9;
  font-weight: 400;
}

.secondary-btn .btn-subtitle {
  color: #fce7f3;
}
</style>
