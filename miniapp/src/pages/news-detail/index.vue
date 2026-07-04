<template>
  <view class="page">
    <view class="page-shell">
      <view class="card redirect-card">
        <view class="section-title">正在跳转原文</view>
        <view class="content">
          {{ message }}
        </view>
        <view v-if="canRetry" class="button-secondary retry-btn" @click="retryOpen">
          重新打开
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getPublicNewsDetail } from '../../api/public'
import { openExternalLink } from '../../utils/external-link'

const message = ref('正在为您打开相关新闻原文，请稍候。')
const canRetry = ref(false)
const sourceUrl = ref('')
const sourceTitle = ref('公众号推文')

async function openNewsSource(id) {
  const detail = await getPublicNewsDetail(id)
  sourceUrl.value = detail?.source_url || ''
  sourceTitle.value = detail?.title || '公众号推文'

  if (!sourceUrl.value) {
    message.value = '当前新闻未配置原文链接。'
    canRetry.value = false
    return
  }

  message.value = '已获取原文链接，正在跳转。'
  canRetry.value = true
  openExternalLink(sourceUrl.value, sourceTitle.value)
}

function retryOpen() {
  if (!sourceUrl.value) return
  openExternalLink(sourceUrl.value, sourceTitle.value)
}

onLoad((options) => {
  if (!options?.id) {
    message.value = '未找到新闻编号。'
    canRetry.value = false
    return
  }

  openNewsSource(options.id).catch(() => {
    message.value = '获取新闻原文失败，请稍后重试。'
    canRetry.value = false
  })
})
</script>

<style scoped>
.redirect-card {
  min-height: 280rpx;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.content {
  margin-top: 16rpx;
  color: #4f5d6b;
  line-height: 1.9;
  white-space: pre-wrap;
}

.retry-btn {
  margin-top: 28rpx;
}
</style>
