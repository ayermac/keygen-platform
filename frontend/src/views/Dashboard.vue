<template>
  <div class="kg-page">
    <!-- Stat Cards -->
    <div class="stats-grid">
      <div
        v-for="(stat, index) in statCards"
        :key="stat.label"
        class="stat-card"
        :style="{ animationDelay: `${index * 80}ms` }"
      >
        <div class="stat-card-header">
          <div class="stat-icon-wrap" :style="{ background: stat.iconBg }">
            <el-icon :size="22" :style="{ color: stat.iconColor }">
              <component :is="stat.icon" />
            </el-icon>
          </div>
          <div class="stat-trend" :class="stat.trendType">
            <el-icon :size="12"><Top /></el-icon>
          </div>
        </div>
        <div class="stat-value">{{ stat.value }}</div>
        <div class="stat-label">{{ stat.label }}</div>
      </div>
    </div>

    <!-- Quick Info -->
    <div class="dashboard-grid">
      <div class="info-card">
        <div class="info-card-title">
          <el-icon><InfoFilled /></el-icon>
          快速指南
        </div>
        <div class="info-steps">
          <div class="info-step">
            <div class="step-number">1</div>
            <div class="step-content">
              <div class="step-title">创建产品</div>
              <div class="step-desc">设置兑换码类型和额度规则</div>
            </div>
          </div>
          <div class="info-step">
            <div class="step-number">2</div>
            <div class="step-content">
              <div class="step-title">批量生成</div>
              <div class="step-desc">按产品批量生成兑换码</div>
            </div>
          </div>
          <div class="info-step">
            <div class="step-number">3</div>
            <div class="step-content">
              <div class="step-title">分发使用</div>
              <div class="step-desc">通过 C 端 API 兑换和消耗</div>
            </div>
          </div>
        </div>
      </div>

      <div class="info-card">
        <div class="info-card-title">
          <el-icon><Connection /></el-icon>
          API 端点
        </div>
        <div class="api-list">
          <div class="api-item">
            <span class="api-method post">POST</span>
            <code>/api/v1/codes/balance</code>
          </div>
          <div class="api-item">
            <span class="api-method post">POST</span>
            <code>/api/v1/codes/redeem</code>
          </div>
          <div class="api-item">
            <span class="api-method post">POST</span>
            <code>/api/v1/codes/consume</code>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Key,
  CircleCheck,
  TrendCharts,
  Timer,
} from '@element-plus/icons-vue'
import { getStatsOverview } from '../api/stats'

const overview = ref({
  total_codes: 0,
  activated_codes: 0,
  total_credits_consumed: 0,
  today_redemptions: 0,
})

const statCards = computed(() => [
  {
    label: '总兑换码数',
    value: overview.value.total_codes.toLocaleString(),
    icon: Key,
    iconBg: 'linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%)',
    iconColor: '#6366f1',
    trendType: 'up',
  },
  {
    label: '已兑换数',
    value: overview.value.activated_codes.toLocaleString(),
    icon: CircleCheck,
    iconBg: 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)',
    iconColor: '#10b981',
    trendType: 'up',
  },
  {
    label: '总额度消耗',
    value: overview.value.total_credits_consumed.toLocaleString(),
    icon: TrendCharts,
    iconBg: 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)',
    iconColor: '#f59e0b',
    trendType: 'up',
  },
  {
    label: '今日兑换',
    value: overview.value.today_redemptions.toLocaleString(),
    icon: Timer,
    iconBg: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)',
    iconColor: '#3b82f6',
    trendType: 'up',
  },
])

onMounted(async () => {
  const res: any = await getStatsOverview()
  overview.value = res.data
})
</script>

<style scoped>
/* ---- Stat Cards Grid ---- */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--kg-surface);
  border: 1px solid var(--kg-border);
  border-radius: 14px;
  padding: 24px;
  transition: all 0.25s ease;
  animation: fadeInUp 0.5s ease both;
  cursor: default;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--kg-shadow-lg);
  border-color: transparent;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.stat-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-trend {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-trend.up {
  background: #ecfdf5;
  color: #10b981;
}

.stat-value {
  font-size: 32px;
  font-weight: 800;
  color: var(--kg-text);
  letter-spacing: -0.025em;
  line-height: 1;
  margin-bottom: 8px;
  font-variant-numeric: tabular-nums;
}

.stat-label {
  font-size: 14px;
  color: var(--kg-text-secondary);
  font-weight: 500;
}

/* ---- Dashboard Grid ---- */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.info-card {
  background: var(--kg-surface);
  border: 1px solid var(--kg-border);
  border-radius: 14px;
  padding: 24px;
  animation: fadeInUp 0.5s ease 0.4s both;
}

.info-card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--kg-text);
  margin-bottom: 20px;
}

.info-card-title .el-icon {
  color: var(--kg-primary);
}

/* ---- Steps ---- */
.info-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-step {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px;
  border-radius: 10px;
  background: var(--kg-bg);
  transition: all 0.2s ease;
}

.info-step:hover {
  background: var(--kg-primary-bg);
}

.step-number {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}

.step-title {
  font-weight: 600;
  color: var(--kg-text);
  font-size: 14px;
  margin-bottom: 2px;
}

.step-desc {
  font-size: 13px;
  color: var(--kg-text-secondary);
}

/* ---- API List ---- */
.api-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.api-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  background: var(--kg-bg);
  font-size: 13px;
  transition: all 0.2s ease;
}

.api-item:hover {
  background: var(--kg-primary-bg);
}

.api-method {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  flex-shrink: 0;
}

.api-method.get {
  background: #dbeafe;
  color: #2563eb;
}

.api-method.post {
  background: #dcfce7;
  color: #16a34a;
}

.api-item code {
  font-family: 'SF Mono', 'Fira Code', monospace;
  color: var(--kg-text);
  font-size: 13px;
}

/* ---- Responsive ---- */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>
