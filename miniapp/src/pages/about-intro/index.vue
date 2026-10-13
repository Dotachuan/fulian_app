<template>
  <view class="page ppt-page">
    <view class="slide-flow">
      <view v-for="(slide, index) in section.slides" :key="slide.no" class="slide-card">
        <image
          v-if="!failedSlides[slide.no]"
          class="slide-image"
          :src="slideUrls[index]"
          mode="widthFix"
          lazy-load
          show-menu-by-longpress
          @click="previewSlide(index)"
          @error="markSlideFailed(slide.no)"
        />
        <view v-else class="slide-error">
          <view class="slide-error-title">图片暂未加载</view>
          <view class="slide-error-text">请检查 PPT 图片是否已同步到服务器</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getFulianPptImagePath, getFulianPptSection } from '../../utils/fulian-ppt'
import { normalizeMediaUrl } from '../../utils/media'

const section = ref(getFulianPptSection('organization'))
const failedSlides = ref({})
const slideUrls = computed(() =>
  section.value.slides.map((slide) => normalizeMediaUrl(getFulianPptImagePath(slide.no)))
)

onLoad((options = {}) => {
  section.value = getFulianPptSection(options.section || 'organization')
  uni.setNavigationBarTitle({ title: section.value.title })
})

function previewSlide(index) {
  uni.previewImage({
    current: slideUrls.value[index],
    urls: slideUrls.value,
  })
}

function markSlideFailed(slideNo) {
  failedSlides.value = { ...failedSlides.value, [slideNo]: true }
}
</script>

<style scoped>
.ppt-page {
  min-height: 100vh;
  padding: 28rpx 28rpx 56rpx;
  background: linear-gradient(180deg, #f6f8fc 0%, #fbfcff 100%);
}

.slide-flow {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.slide-card {
  overflow: hidden;
  border: 1rpx solid #e4ebf4;
  border-radius: 8rpx;
  background: #ffffff;
  box-shadow: 0 18rpx 44rpx rgba(29, 45, 68, 0.06);
}

.slide-image {
  display: block;
  width: 100%;
  background: #f3f5f8;
}

.slide-error {
  display: flex;
  min-height: 340rpx;
  padding: 30rpx;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  text-align: center;
  background: #f7f9fc;
}

.slide-error-title {
  color: #344054;
  font-size: 28rpx;
  font-weight: 700;
}

.slide-error-text {
  margin-top: 12rpx;
  color: #7c899c;
  font-size: 23rpx;
}
</style>
