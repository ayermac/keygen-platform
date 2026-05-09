<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>总激活码数</template>
          <div class="stat-value">{{ overview.total_keys }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>已激活数</template>
          <div class="stat-value">{{ overview.activated_keys }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>总 Score 消耗</template>
          <div class="stat-value">{{ overview.total_score_consumed }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>今日激活</template>
          <div class="stat-value">{{ overview.today_activations }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getStatsOverview } from '../api/stats'

const overview = ref({
  total_keys: 0,
  activated_keys: 0,
  total_score_consumed: 0,
  today_activations: 0,
})

onMounted(async () => {
  const res: any = await getStatsOverview()
  overview.value = res.data
})
</script>

<style scoped>
.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  text-align: center;
}
</style>
