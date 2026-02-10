<script setup>
import { useRouter } from 'vue-router'
import { useAlertsStore } from '../stores/alerts'
import { useAuthStore } from '../stores/auth'
import { ref, computed } from 'vue'

const router = useRouter()
const store = useAlertsStore()
const authStore = useAuthStore()
const notes = ref('Building A door may need maintenance. Camera at Gate 2 has been offline since 1:58 AM. Notified.')

const criticalCount = computed(() => store.alerts.filter(a => a.type === 'critical').length)
const warningCount = computed(() => store.alerts.filter(a => a.type === 'warning').length)
const totalCount = computed(() => store.alerts.length)
const unresolved = computed(() => store.alerts.filter(a => a.status === 'pending'))

const handleShiftEnd = () => {
  alert('Shift summary sent to next operator. Logging out...')
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="shift-container">
    <!-- Header -->
    <header class="shift-header">
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
        <h1 class="page-title">Shift Summary</h1>
        <div class="spacer"></div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="shift-main">
      <!-- Shift Information -->
      <div class="info-card">
        <h2 class="card-title">Shift Information</h2>
        <div class="info-grid">
          <div class="info-box">
            <label>Shift Time</label>
            <p>10:00 PM - 06:00 AM</p>
          </div>
          <div class="info-box">
            <label>Operator</label>
            <p>Admin</p>
          </div>
        </div>
      </div>

      <!-- Alert Statistics -->
      <div class="stats-grid">
        <!-- Critical Alerts -->
        <div class="stat-card critical-stat">
          <div class="stat-icon critical-icon">
            <svg style="width: 24px; height: 24px; color: #EF4444;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 class="stat-label critical-label">Critical Alerts</h3>
          <p class="stat-number critical-number">{{ criticalCount }}</p>
        </div>

        <!-- Warning Alerts -->
        <div class="stat-card warning-stat">
          <div class="stat-icon warning-icon">
            <svg style="width: 24px; height: 24px; color: #F59E0B;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="stat-label warning-label">Warning Alerts</h3>
          <p class="stat-number warning-number">{{ warningCount }}</p>
        </div>

        <!-- Total Handled -->
        <div class="stat-card normal-stat">
          <div class="stat-icon normal-icon">
            <svg style="width: 24px; height: 24px; color: #10B981;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="stat-label normal-label">Total Handled</h3>
          <p class="stat-number normal-number">{{ totalCount }}</p>
        </div>
      </div>

      <!-- Unresolved Alerts -->
      <div class="unresolved-card">
        <div class="unresolved-header">
          <div class="unresolved-icon">
            <svg style="width: 24px; height: 24px; color: #ea580c;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 class="unresolved-title">Unresolved / Pending Alerts</h2>
        </div>
        
        <div v-if="unresolved.length === 0" class="empty-unresolved">
          <svg style="width: 48px; height: 48px; color: #10B981;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p>All alerts have been resolved</p>
        </div>

        <div v-else class="unresolved-list">
          <div
            v-for="alert in unresolved"
            :key="alert.id"
            class="unresolved-item"
          >
            <div class="unresolved-content">
              <div class="unresolved-badges">
                <span class="unresolved-badge">{{ alert.type }}</span>
                <span class="unresolved-time">{{ alert.time }}</span>
              </div>
              <p class="unresolved-description">{{ alert.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Notes Section -->
      <div class="notes-card">
        <h2 class="card-title">Notes for Next Shift</h2>
        <textarea
          v-model="notes"
          class="notes-textarea"
          placeholder="Add important notes, observations, or instructions for the next operator..."
        ></textarea>
        <p class="notes-hint">Include any important information that the next shift operator should know</p>
      </div>

      <!-- Action Button -->
      <button @click="handleShiftEnd" class="submit-button">
        <svg style="width: 20px; height: 20px; color: white;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>Send to Next Shift & Log Out</span>
      </button>
    </main>
  </div>
</template>

<style scoped>
.shift-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 50%, #f3e8ff 100%);
  color: #111827;
  font-family: system-ui, -apple-system, sans-serif;
}

/* Header */
.shift-header {
  background: white;
  border-bottom: 2px solid #bfdbfe;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-content {
  max-width: 896px;
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
.shift-main {
  max-width: 896px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.info-card {
  background: white;
  border: 1px solid #bfdbfe;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.info-box {
  background: #f9fafb;
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #e5e7eb;
}

.info-box label {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: block;
  margin-bottom: 0.25rem;
}

.info-box p {
  font-weight: 600;
  color: #111827;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

@media (min-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.critical-stat {
  border: 2px solid #EF4444;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
}

.warning-stat {
  border: 2px solid #F59E0B;
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
}

.normal-stat {
  border: 2px solid #10B981;
  background: linear-gradient(135deg, #f0fdf4 0%, #d1fae5 100%);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
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

.stat-label {
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.critical-label {
  color: #EF4444;
}

.warning-label {
  color: #F59E0B;
}

.normal-label {
  color: #10B981;
}

.stat-number {
  font-size: 2.25rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.critical-number {
  color: #EF4444;
}

.warning-number {
  color: #F59E0B;
}

.normal-number {
  color: #10B981;
}

/* Unresolved Alerts */
.unresolved-card {
  background: white;
  border: 2px solid #ea580c;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.unresolved-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.unresolved-icon {
  width: 40px;
  height: 40px;
  background: #fed7aa;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.unresolved-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #ea580c;
}

.empty-unresolved {
  text-align: center;
  padding: 1.5rem;
  color: #6b7280;
}

.empty-unresolved p {
  margin-top: 0.5rem;
  color: #374151;
}

.unresolved-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.unresolved-item {
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-radius: 8px;
  padding: 1rem;
}

.unresolved-content {
  flex: 1;
}

.unresolved-badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.unresolved-badge {
  font-size: 0.75rem;
  font-weight: 700;
  color: #ea580c;
  background: #fed7aa;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  text-transform: uppercase;
}

.unresolved-time {
  font-size: 0.75rem;
  color: #6b7280;
  font-family: 'Courier New', monospace;
}

.unresolved-description {
  font-weight: 500;
  color: #111827;
}

/* Notes Section */
.notes-card {
  background: white;
  border: 1px solid #bfdbfe;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.notes-textarea {
  width: 100%;
  min-height: 128px;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  font-family: inherit;
  font-size: 1rem;
  color: #111827;
  resize: none;
  transition: all 0.2s;
}

.notes-textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.notes-hint {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.5rem;
}

/* Submit Button */
.submit-button {
  width: 100%;
  background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
  color: white;
  font-weight: 700;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
  transition: all 0.3s;
  font-size: 1rem;
}

.submit-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
}

.submit-button:focus {
  outline: 4px solid rgba(37, 99, 235, 0.3);
  outline-offset: 2px;
}
</style>
