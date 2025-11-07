<script setup lang="ts">
import { ref, h, onMounted } from 'vue';
import type { DataTableColumns } from 'naive-ui';
import { NButton, NCard, NDataTable, NInput } from 'naive-ui';
import { getDiseases, startTest, updateDisease } from '@/service/api';
import { useRouter } from 'vue-router';
import { useAppStore } from '@/store/modules/app';

const appStore = useAppStore();

interface Disease {
  id: number;
  name: string;
  description: string;
  symptoms_count: number;
}

const loading = ref(false);
const diseases = ref<Disease[]>([]);
const router = useRouter();

// 分页配置
const pagination = ref({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 30],
  itemCount: 0,
  onChange: (page: number) => {
    pagination.value.page = page;
  },
  onUpdatePageSize: (pageSize: number) => {
    pagination.value.pageSize = pageSize;
    pagination.value.page = 1;
  },
  prefix: (info: any) => {
    return `共 ${pagination.value.itemCount} 条`;
  }
});

const columns: DataTableColumns<Disease> = [
  {
    title: 'ID',
    key: 'id',
    width: 80,
    align: 'center'
  },
  {
    title: '疾病名称',
    key: 'name',
    width: 300,
    ellipsis: {
      tooltip: true
    }
  },
  {
    title: '描述',
    key: 'description',
    width: 500,
    render(row) {
      const text = row.description || '';
      const displayText = text.length > 200 ? text.substring(0, 200) + '...' : text;
      return h('div', { style: { whiteSpace: 'pre-wrap', wordBreak: 'break-word' } }, displayText);
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    align: 'center',
    render(row) {
      return h(
        'div',
        { class: 'flex-center gap-8px' },
        [
          h(
            NButton,
            {
              size: 'small',
              onClick: () => handleEdit(row)
            },
            { default: () => '编辑' }
          ),
          h(
            NButton,
            {
              size: 'small',
              type: 'primary',
              onClick: () => handleStartTest(row.id)
            },
            { default: () => '开始测试' }
          )
        ]
      );
    }
  }
];

async function loadDiseases() {
  loading.value = true;
  try {
    const { data } = await getDiseases();
    console.log('加载疾病数据:', data); // 调试信息
    diseases.value = data || [];
    pagination.value.itemCount = diseases.value.length;
    console.log('diseases.value:', diseases.value.length); // 调试信息
  } catch (error) {
    window.$message?.error('加载疾病列表失败');
    console.error('加载失败:', error);
  } finally {
    loading.value = false;
  }
}

async function handleStartTest(diseaseId: number) {
  const dialog = window.$dialog?.info({
    title: '开始测试',
    content: '确定要开始测试这个疾病吗？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      if (dialog) {
        dialog.loading = true;
      }
      try {
        const result: any = await startTest({ disease_id: diseaseId, max_rounds: 10 });
        window.$message?.success(`测试已启动，执行ID: ${result.execution_id}`);
        // 跳转到执行详情页
        router.push(`/medical/execution-detail/${result.execution_id}`);
      } catch (error) {
        window.$message?.error('启动测试失败');
        console.error(error);
      } finally {
        if (dialog) {
          dialog.loading = false;
        }
      }
    }
  });
}

function handleEdit(disease: Disease) {
  const editContent = ref(disease.description || '');
  
  window.$dialog?.create({
    title: `编辑疾病: ${disease.name}`,
    content: () =>
      h(NInput, {
        type: 'textarea',
        value: editContent.value,
        onUpdateValue: (value: string) => {
          editContent.value = value;
        },
        rows: 20,
        style: { fontFamily: 'monospace' }
      }),
    positiveText: '保存',
    negativeText: '取消',
    style: { width: '800px' },
    onPositiveClick: async () => {
      try {
        await updateDisease(disease.id, { description: editContent.value });
        
        window.$message?.success('保存成功');
        await loadDiseases();
      } catch (error) {
        window.$message?.error('保存失败');
        console.error(error);
        return false; // 阻止关闭对话框
      }
    }
  });
}

// 组件挂载时加载数据
onMounted(() => {
  loadDiseases();
});
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <NCard title="疾病列表" :bordered="false" size="small" class="sm:flex-1-hidden card-wrapper">
      <template #header-extra>
        <NButton @click="loadDiseases" :loading="loading">
          <template #icon>
            <icon-ic-round-refresh />
          </template>
          刷新
        </NButton>
      </template>
      <NDataTable
        :columns="columns"
        :data="diseases"
        size="small"
        :flex-height="!appStore.isMobile"
        :loading="loading"
        :bordered="false"
        :single-line="false"
        :scroll-x="1200"
        :pagination="pagination"
        :row-key="(row: Disease) => row.id"
        class="sm:h-full"
      />
    </NCard>
  </div>
</template>

<style scoped></style>
