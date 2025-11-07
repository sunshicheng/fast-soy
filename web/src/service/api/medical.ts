import { request } from '../request';

/**
 * 开始诊断测试
 */
export function startTest(data: { disease_id: number; max_rounds?: number }) {
  return request({
    url: '/medical/diagnosis/start',
    method: 'post',
    data
  });
}

/**
 * 获取执行详情
 */
export function getExecutionDetail(executionId: string) {
  return request({
    url: `/medical/diagnosis/execution/${executionId}`,
    method: 'get'
  });
}

/**
 * 获取疾病列表
 */
export function getDiseases() {
  return request({
    url: '/medical/diagnosis/diseases',
    method: 'get'
  });
}

/**
 * 更新疾病描述
 */
export function updateDisease(diseaseId: number, data: { description: string }) {
  return request({
    url: `/medical/diagnosis/diseases/${diseaseId}`,
    method: 'patch',
    data
  });
}
