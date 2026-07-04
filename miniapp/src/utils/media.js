import { getBaseUrl } from '../config/env'

const API_PREFIX = '/api/v1'
const LOCAL_MEDIA_HOST_RE = /^(localhost|127(?:\.\d{1,3}){3}|0\.0\.0\.0)$/i

function getAssetOrigin() {
  const baseUrl = getBaseUrl()
  if (baseUrl.endsWith(API_PREFIX)) {
    return baseUrl.slice(0, -API_PREFIX.length)
  }
  return baseUrl
}

function isSameAssetHost(parsedUrl) {
  try {
    const assetOrigin = new URL(getAssetOrigin())
    return parsedUrl.hostname === assetOrigin.hostname
  } catch {
    return false
  }
}

function rewriteLocalAssetUrl(url) {
  try {
    const parsed = new URL(url)
    const shouldRewriteToAssetOrigin =
      parsed.pathname.startsWith('/uploads/') &&
      (LOCAL_MEDIA_HOST_RE.test(parsed.hostname) || isSameAssetHost(parsed))

    if (!shouldRewriteToAssetOrigin) {
      return url
    }
    return `${getAssetOrigin()}${parsed.pathname}${parsed.search || ''}${parsed.hash || ''}`
  } catch {
    return url
  }
}

export function normalizeMediaUrl(url) {
  if (!url || typeof url !== 'string') return ''
  if (/^https?:\/\//i.test(url)) return rewriteLocalAssetUrl(url)
  if (url.startsWith('//')) return `https:${url}`
  if (url.startsWith('/')) return `${getAssetOrigin()}${url}`
  return `${getAssetOrigin()}/${url}`
}
