function normalizeUrl(url) {
  if (!url || typeof url !== 'string') return ''
  return url.trim().replace(/^['"]|['"]$/g, '')
}

export function isWechatArticleUrl(url) {
  const normalized = normalizeUrl(url)
  if (!normalized) return false

  const directMatch = /^https?:\/\/mp\.weixin\.qq\.com\//i.test(normalized)
  if (directMatch) return true

  try {
    const parsed = new URL(normalized)
    return parsed.hostname === 'mp.weixin.qq.com'
  } catch {
    return /mp\.weixin\.qq\.com\//i.test(normalized)
  }
}

export function openExternalLink(url, title = '公众号推文') {
  const normalized = normalizeUrl(url)

  if (!normalized) {
    uni.showToast({
      title: '链接不存在',
      icon: 'none',
    })
    return
  }

  if (!isWechatArticleUrl(normalized)) {
    uni.showToast({
      title: '当前仅支持打开公众号推文',
      icon: 'none',
    })
    return
  }

  // #ifdef H5
  window.open(normalized, '_blank', 'noopener,noreferrer')
  // #endif

  // #ifndef H5
  uni.navigateTo({
    url: `/pages/webview/index?title=${encodeURIComponent(title || '公众号推文')}&url=${encodeURIComponent(normalized)}`,
  })
  // #endif
}
