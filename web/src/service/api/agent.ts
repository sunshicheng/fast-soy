import { request } from '../request';

/** get agent list */
export function fetchGetAgentList(data?: Api.SystemManage.AgentSearchParams) {
  return request<Api.SystemManage.AgentList>({
    url: '/system-manage/agents/all/',
    method: 'post',
    data
  });
}

/** get agent detail */
export function fetchGetAgentDetail(id: number) {
  return request<Api.SystemManage.Agent>({
    url: `/system-manage/agents/${id}`,
    method: 'get'
  });
}

/** create agent */
export function fetchCreateAgent(data: Api.SystemManage.AgentAddParams) {
  return request({
    url: '/system-manage/agents',
    method: 'post',
    data
  });
}

/** update agent */
export function fetchUpdateAgent(id: number, data: Api.SystemManage.AgentUpdateParams) {
  return request({
    url: `/system-manage/agents/${id}`,
    method: 'patch',
    data
  });
}

/** delete agent */
export function fetchDeleteAgent(id: number) {
  return request({
    url: `/system-manage/agents/${id}`,
    method: 'delete'
  });
}

/** batch delete agents */
export function fetchBatchDeleteAgents(data: Api.SystemManage.CommonBatchDeleteParams) {
  return request({
    url: '/system-manage/agents',
    method: 'delete',
    data
  });
}

