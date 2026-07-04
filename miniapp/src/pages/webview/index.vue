<template>
  <web-view v-if="url" :src="url"></web-view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { isWechatArticleUrl } from '../../utils/external-link'

const url = ref('')

onLoad((options) => {
  const nextUrl = decodeURIComponent(options?.url || '')
  const title = decodeURIComponent(options?.title || '公众号推文')

  if (!nextUrl) {
    uni.showToast({
      title: '链接不存在',
      icon: 'none',
    })
    return
  }

  if (!isWechatArticleUrl(nextUrl)) {
    uni.showToast({
      title: '当前仅支持打开公众号推文',
      icon: 'none',
    })
    setTimeout(() => {
      uni.navigateBack({ delta: 1 })
    }, 500)
    return
  }

  url.value = nextUrl
  uni.setNavigationBarTitle({
    title: title || '公众号推文',
  })
})
</script>

<style scoped>
.webview-page-placeholder {
  display: block;
}
</style>
