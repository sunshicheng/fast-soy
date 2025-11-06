<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { NButton, NForm, NFormItem, NInput, NModal, NRadio, NRadioGroup, NSelect, NSpace } from 'naive-ui';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { fetchCreateAgent, fetchUpdateAgent } from '@/service/api';
import { $t } from '@/locales';
import { statusTypeOptions } from '@/constants/business';

defineOptions({
  name: 'AgentOperateDrawer'
});

interface Props {
  /** the type of operation */
  operateType: NaiveUI.TableOperateType;
  /** the edit row data */
  rowData?: Api.SystemManage.Agent | null;
}

const props = defineProps<Props>();

interface Emits {
  (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', {
  default: false
});

const { formRef, validate, restoreValidation } = useNaiveForm();
const { defaultRequiredRule } = useFormRules();

const title = computed(() => {
  const titles: Record<NaiveUI.TableOperateType, string> = {
    add: '添加Agent',
    edit: '编辑Agent'
  };
  return titles[props.operateType];
});

const model: Api.SystemManage.AgentUpdateParams = reactive(createDefaultModel());

function createDefaultModel(): Api.SystemManage.AgentUpdateParams {
  return {
    name: '',
    agentType: 'business',
    description: '',
    version: '1.0.0',
    config: null,
    statusType: '1'
  };
}

type RuleKey = Extract<keyof Api.SystemManage.AgentUpdateParams, 'name' | 'agentType' | 'statusType'>;

const rules = ref<Record<RuleKey, App.Global.FormRule>>({
  name: defaultRequiredRule,
  agentType: defaultRequiredRule,
  statusType: defaultRequiredRule
});

const agentTypeOptions = [
  { label: '业务场景类', value: 'business' },
  { label: '功能类', value: 'function' }
];

function handleInitModel() {
  Object.assign(model, createDefaultModel());

  if (props.operateType === 'edit' && props.rowData) {
    Object.assign(model, {
      id: props.rowData.id,
      name: props.rowData.name,
      agentType: props.rowData.agentType,
      description: props.rowData.description || '',
      version: props.rowData.version || '1.0.0',
      config: props.rowData.config,
      statusType: props.rowData.statusType || '1'
    });
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  if (props.operateType === 'add') {
    const { error } = await fetchCreateAgent({
      name: model.name!,
      agentType: model.agentType!,
      description: model.description || null,
      version: model.version || '1.0.0',
      config: model.config,
      statusType: model.statusType || '1'
    });
    if (!error) {
      window.$message?.success($t('common.addSuccess'));
    }
  } else if (props.operateType === 'edit' && model.id) {
    const { error } = await fetchUpdateAgent(model.id, {
      name: model.name,
      agentType: model.agentType,
      description: model.description,
      version: model.version,
      config: model.config,
      statusType: model.statusType
    });
    if (!error) {
      window.$message?.success($t('common.updateSuccess'));
    }
  }

  closeDrawer();
  emit('submitted');
}

watch(visible, () => {
  if (visible.value) {
    handleInitModel();
    restoreValidation();
  }
});
</script>

<template>
  <NModal v-model:show="visible" preset="dialog" :title="title" style="width: 600px">
    <NForm
      ref="formRef"
      :model="model"
      :rules="rules"
      label-placement="left"
      label-width="auto"
      require-mark-placement="right-hanging"
      size="medium"
    >
      <NFormItem label="Agent名称" path="name">
        <NInput
          v-model:value="model.name"
          placeholder="请输入Agent名称"
          :disabled="operateType === 'edit'"
        />
      </NFormItem>
      <NFormItem label="Agent类型" path="agentType">
        <NSelect
          v-model:value="model.agentType"
          :options="agentTypeOptions"
          placeholder="请选择Agent类型"
        />
      </NFormItem>
      <NFormItem label="描述" path="description">
        <NInput
          v-model:value="model.description"
          type="textarea"
          placeholder="请输入Agent描述"
          :rows="3"
          :maxlength="500"
          show-count
        />
      </NFormItem>
      <NFormItem label="版本" path="version">
        <NInput
          v-model:value="model.version"
          placeholder="请输入版本号，如：1.0.0"
        />
      </NFormItem>
      <NFormItem label="状态" path="statusType">
        <NRadioGroup v-model:value="model.statusType">
          <NRadio v-for="item in statusTypeOptions" :key="item.value" :value="item.value" :label="$t(item.label)" />
        </NRadioGroup>
      </NFormItem>
    </NForm>
    <template #action>
      <NSpace :size="16">
        <NButton @click="closeDrawer">{{ $t('common.cancel') }}</NButton>
        <NButton type="primary" @click="handleSubmit">{{ $t('common.confirm') }}</NButton>
      </NSpace>
    </template>
  </NModal>
</template>

<style scoped></style>

