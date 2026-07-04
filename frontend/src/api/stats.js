import request from '@/utils/request'

export const getStatsOverviewApi = () =>
  request.get('/stats/overview')

export const getStatsTrendApi = (params) =>
  request.get('/stats/trend', { params })

export const getStatsByTargetApi = (params) =>
  request.get('/stats/by-target', { params })

export const getStatsByMethodApi = (params) =>
  request.get('/stats/by-method', { params })

export const getLogListApi = (params) =>
  request.get('/logs', { params })
