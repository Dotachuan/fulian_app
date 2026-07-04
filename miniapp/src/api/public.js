import { request } from '../utils/request'

export const getPublicNews = (data) =>
  request({ url: '/public/news', data })

export const getPublicNewsDetail = (id) =>
  request({ url: `/public/news/${id}` })

export const getPublicNotices = (data) =>
  request({ url: '/public/notices', data })

export const getPublicNoticeDetail = (id) =>
  request({ url: `/public/notices/${id}` })

export const getPublicSiteContent = () =>
  request({ url: '/public/site-content' })

export const getPublicContact = () =>
  request({ url: '/public/contact' })

export const getPublicIndustrialPark = () =>
  request({ url: '/public/industrial-park' })

export const getPublicProjectProgress = () =>
  request({ url: '/public/project-progress' })

export const getPublicProjectLinks = (data) =>
  request({ url: '/public/project-links', data })
