<script setup lang="tsx">
import { NButton, NCard, NDataTable, NForm, NFormItem, NInput, NSelect, NPopconfirm, NTag } from 'naive-ui';
import { fetchGetAgentList, fetchDeleteAgent, fetchBatchDeleteAgents } from '@/service/api';
import { $t } from '@/locales';
import { useTable, useTableOperate } from '@/hooks/common/table';
import { statusTypeRecord } from '@/constants/business';
import AgentOperateDrawer from '@/views/agent/config/modules/agent-operate-drawer.vue';

const {
  columns,
  data,
  getData,
  loading,
  pagination,
  searchParams,
  resetSearchParams
} = useTable({
  apiFn: fetchGetAgentList,
  apiParams: {
    current: 1,
    size: 10,
    name: null,
    agentType: null,
    statusType: null
  },
  columns: () => [
    {
      key: 'index',
      title: $t('common.index'),
      align: 'center',
      width: 64
    },
    {
      key: 'name',
      title: 'Agent名称',
      align: 'center',
      minWidth: 150
    },
    {
      key: 'agentType',
      title: 'Agent类型',
      align: 'center',
      width: 120,
      render: row => {
        const typeMap: Record<Api.SystemManage.AgentType, { label: string; type: NaiveUI.ThemeColor }> = {
          business: { label: '业务场景类', type: 'primary' },
          function: { label: '功能类', type: 'success' }
        };
        const typeInfo = typeMap[row.agentType];
        return <NTag type={typeInfo.type}>{typeInfo.label}</NTag>;
      }
    },
    {
      key: 'description',
      title: '描述',
      align: 'center',
      minWidth: 200,
      ellipsis: { tooltip: true }
    },
    {
      key: 'version',
      title: '版本',
      align: 'center',
      width: 100
    },
    {
      key: 'statusType',
      title: '状态',
      align: 'center',
      width: 100,
      render: row => {
        if (!row.statusType) return null;
        const tagMap: Record<string, NaiveUI.ThemeColor> = {
          '1': 'success',
          '2': 'error'
        };
        const label = $t(statusTypeRecord[row.statusType]);
        return <NTag type={tagMap[row.statusType] || 'default'}>{label}</NTag>;
      }
    },
    {
      key: 'operate',
      title: $t('common.action'),
      align: 'center',
      width: 150,
      render: row => (
        <div class="flex justify-center gap-8px">
          <NButton size="small" onClick={() => edit(row)}>
            {$t('common.edit')}
          </NButton>
          <NPopconfirm onPositiveClick={() => handleDelete(row)}>
            {{
              trigger: () => (
                <NButton size="small" type="error">
                  {$t('common.delete')}
                </NButton>
              ),
              default: () => $t('common.confirmDelete')
            }}
          </NPopconfirm>
        </div>
      )
    }
  ]
});

const {
  drawerVisible,
  operateType,
  editingData,
  handleAdd,
  handleEdit,
  checkedRowKeys,
  onBatchDeleted,
  onDeleted
} = useTableOperate(data, getData);

async function handleBatchDelete() {
  const { error } = await fetchBatchDeleteAgents({ ids: checkedRowKeys.value });
  if (!error) {
    onBatchDeleted();
  }
}

async function handleDelete(row: Api.SystemManage.Agent) {
  const { error } = await fetchDeleteAgent(row.id);
  if (!error) {
    window.$message?.success($t('common.deleteSuccess'));
    onDeleted();
  }
}

function edit(row: Api.SystemManage.Agent) {
  handleEdit(row.id);
}
</script>

<template>
  <div class="flex-col gap-16px p-16px">
    <NCard :bordered="false">
      <template #header>
        <span class="text-18px font-500">Agent管理</span>
      </template>
      <template #header-extra>
        <NButton type="primary" @click="handleAdd">
          {{ $t('common.add') }}
        </NButton>
      </template>

      <!-- 搜索表单 -->
      <div class="mb-16px">
        <NForm
          :model="searchParams"
          label-placement="left"
          :label-width="80"
          inline
        >
          <NFormItem label="Agent名称">
            <NInput
              v-model:value="searchParams.name"
              placeholder="请输入Agent名称"
              clearable
            />
          </NFormItem>
          <NFormItem label="Agent类型">
            <NSelect
              v-model:value="searchParams.agentType"
              placeholder="请选择类型"
              clearable
              :options="[
                { label: '业务场景类', value: 'business' },
                { label: '功能类', value: 'function' }
              ]"
            />
          </NFormItem>
          <NFormItem label="状态">
            <NSelect
              v-model:value="searchParams.statusType"
              placeholder="请选择状态"
              clearable
              :options="[
                { label: $t(statusTypeRecord['1']), value: '1' },
                { label: $t(statusTypeRecord['2']), value: '2' }
              ]"
            />
          </NFormItem>
          <NFormItem>
            <NButton type="primary" @click="getData">
              {{ $t('common.search') }}
            </NButton>
            <NButton class="ml-8px" @click="resetSearchParams">
              {{ $t('common.reset') }}
            </NButton>
          </NFormItem>
        </NForm>
      </div>

      <!-- 数据表格 -->
      <NDataTable
        :columns="columns"
        :data="data"
        :loading="loading"
        :pagination="pagination"
        @update:page="getData"
        @update:page-size="getData"
      />
    </NCard>
    <AgentOperateDrawer
      v-model:visible="drawerVisible"
      :operate-type="operateType"
      :row-data="editingData"
      @submitted="getData"
    />
  </div>
</template>

<style scoped></style>

