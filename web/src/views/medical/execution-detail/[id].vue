<script setup lang="ts">
import { ref, onMounted, computed, h } from 'vue';
import { useRoute } from 'vue-router';
import { NButton, NTag, NCard, NSteps, NStep, NTimeline, NTimelineItem, NDescriptions, NDescriptionsItem, NSpin } from 'naive-ui';
import { getExecutionDetail } from '@/service/api';

interface ExecutionStep {
  step_name: string;
  step_order: number;
  status: string;
  start_time: string | null;
  end_time: string | null;
  output_data: any;
  error_message: string | null;
}

interface Conversation {
  round: number;
  role: string;
  message: string;
  timestamp: string;
}

interface ExecutionDetail {
  execution_id: string;
  disease_name: string;
  status: string;
  start_time: string;
  end_time: string | null;
  steps: ExecutionStep[];
  conversations: Conversation[];
  result: any;
}

const route = useRoute();
const loading = ref(false);
const detail = ref<ExecutionDetail | null>(null);

const executionId = computed(() => route.params.id as string);

const statusMap: Record<string, { type: any; text: string }> = {
  pending: { type: 'default', text: '待执行' },
  running: { type: 'info', text: '执行中' },
  success: { type: 'success', text: '成功' },
  failed: { type: 'error', text: '失败' },
  error: { type: 'error', text: '错误' }
};

const currentStep = computed(() => {
  if (!detail.value?.steps) return 0;
  const runningStep = detail.value.steps.findIndex(s => s.status === 'running');
  if (runningStep !== -1) return runningStep;
  const successSteps = detail.value.steps.filter(s => s.status === 'success').length;
  return successSteps;
});

async function loadDetail() {
  loading.value = true;
  try {
    const data: any = await getExecutionDetail(executionId.value);
    detail.value = data;
  } catch (error) {
    window.$message?.error('加载执行详情失败');
    console.error(error);
  } finally {
    loading.value = false;
  }
}

function getStepStatus(status: string) {
  const map: Record<string, any> = {
    pending: 'wait',
    running: 'process',
    success: 'finish',
    failed: 'error',
    error: 'error'
  };
  return map[status] || 'wait';
}

onMounted(() => {
  loadDetail();
});
</script>

<template>
  <div class="h-full overflow-auto p-4">
    <NSpin :show="loading">
      <div v-if="detail" class="space-y-4">
        <!-- 基本信息 -->
        <NCard title="执行信息" :bordered="false">
          <template #header-extra>
            <NButton @click="loadDetail" :loading="loading">
              <template #icon>
                <icon-ic-round-refresh />
              </template>
              刷新
            </NButton>
          </template>
          <NDescriptions :column="2" bordered>
            <NDescriptionsItem label="执行ID">
              {{ detail.execution_id }}
            </NDescriptionsItem>
            <NDescriptionsItem label="疾病名称">
              {{ detail.disease_name }}
            </NDescriptionsItem>
            <NDescriptionsItem label="执行状态">
              <NTag :type="statusMap[detail.status]?.type || 'default'">
                {{ statusMap[detail.status]?.text || detail.status }}
              </NTag>
            </NDescriptionsItem>
            <NDescriptionsItem label="开始时间">
              {{ detail.start_time }}
            </NDescriptionsItem>
            <NDescriptionsItem label="结束时间">
              {{ detail.end_time || '未结束' }}
            </NDescriptionsItem>
          </NDescriptions>
        </NCard>

        <!-- 执行步骤 -->
        <NCard title="执行步骤" :bordered="false">
          <NSteps :current="currentStep" :status="detail.status === 'error' ? 'error' : 'process'">
            <NStep
              v-for="step in detail.steps"
              :key="step.step_order"
              :title="step.step_name"
              :status="getStepStatus(step.status)"
            >
              <template #description>
                <div class="text-xs">
                  <div v-if="step.start_time">开始: {{ step.start_time }}</div>
                  <div v-if="step.end_time">结束: {{ step.end_time }}</div>
                  <div v-if="step.error_message" class="text-red-500">
                    错误: {{ step.error_message }}
                  </div>
                </div>
              </template>
            </NStep>
          </NSteps>
        </NCard>

        <!-- 对话记录 -->
        <NCard title="对话记录" :bordered="false" v-if="detail.conversations && detail.conversations.length > 0">
          <NTimeline>
            <NTimelineItem
              v-for="conv in detail.conversations"
              :key="`${conv.round}-${conv.role}`"
              :type="conv.role === 'doctor' ? 'success' : 'info'"
              :title="`第 ${conv.round} 轮 - ${conv.role === 'doctor' ? '医生' : '患者'}`"
              :time="conv.timestamp"
            >
              <div class="whitespace-pre-wrap">{{ conv.message }}</div>
            </NTimelineItem>
          </NTimeline>
        </NCard>

        <!-- 诊断结果 -->
        <NCard title="诊断结果" :bordered="false" v-if="detail.result">
          <NDescriptions :column="1" bordered>
            <NDescriptionsItem
              v-for="(value, key) in detail.result"
              :key="key"
              :label="String(key)"
            >
              <template v-if="typeof value === 'boolean'">
                <NTag :type="value ? 'success' : 'error'">
                  {{ value ? '是' : '否' }}
                </NTag>
              </template>
              <template v-else>
                {{ value }}
              </template>
            </NDescriptionsItem>
          </NDescriptions>
        </NCard>
      </div>
    </NSpin>
  </div>
</template>

<style scoped>
.space-y-4 > * + * {
  margin-top: 1rem;
}
</style>
