<template>
  <view class="page certificate-page">
    <view class="page-shell">
      <view v-if="!loggedIn" class="state-band">
        <view class="section-title">请先登录</view>
        <view class="section-subtitle">登录后可根据本人捐赠记录生成捐赠证书。</view>
        <view class="button-primary state-action" @click="goLogin">去登录</view>
      </view>

      <view v-else-if="memberState !== 'bound'" class="state-band">
        <view class="section-title">{{ stateTitle }}</view>
        <view class="section-subtitle">{{ stateDescription }}</view>
        <view class="button-secondary state-action" @click="goMy">查看会员绑定</view>
      </view>

      <template v-else>
        <view class="state-band certificate-intro">
          <view class="section-title">捐赠证书</view>
        </view>

        <view class="certificate-panel">
          <view v-if="loading" class="empty-block">证书生成中...</view>
          <view v-else-if="errorText" class="empty-block">{{ errorText }}</view>
          <template v-else>
            <view class="certificate-preview">
              <view class="template-stage" :class="{ calibrating: showCoordinateTools }">
                <image
                  class="template-image"
                  :src="previewImageUrl"
                  mode="widthFix"
                  show-menu-by-longpress
                  @click="previewCertificate"
                />

                <view v-if="showCoordinateTools" class="calibration-grid"></view>
                <view v-if="showCoordinateTools" class="calibration-axis x-axis"></view>
                <view v-if="showCoordinateTools" class="calibration-axis y-axis"></view>

                <text v-if="showOverlayText" class="fill-text" :style="fieldStyle('donorName')">{{ certificateData.donorName }}</text>
                <text v-if="showOverlayText && selectedTemplateHasCurrentDonation" class="fill-text" :style="fieldStyle('currentAmount')">
                  {{ displayCertificateData.currentYearAmount }}
                </text>
                <text v-if="showOverlayText" class="fill-text" :style="fieldStyle(totalAmountKey)">{{ displayCertificateData.totalAmount }}</text>
                <text v-if="showOverlayText" class="fill-text" :style="fieldStyle('supportYears')">{{ certificateData.supportYears }}</text>
                <text v-if="showOverlayText" class="fill-text" :style="fieldStyle('issuedYear')">{{ issuedDate.year }}</text>
                <text v-if="showOverlayText" class="fill-text" :style="fieldStyle('issuedMonth')">{{ issuedDate.month }}</text>
                <text v-if="showOverlayText" class="fill-text" :style="fieldStyle('issuedDay')">{{ issuedDate.day }}</text>

                <template v-if="showCoordinateTools">
                  <view
                    v-for="marker in calibrationMarkers"
                    :key="marker.key"
                    class="calibration-marker"
                    :style="markerStyle(marker)"
                  >
                    <view class="marker-dot"></view>
                    <view class="marker-label">{{ marker.label }} {{ marker.left }}%, {{ marker.top }}%</view>
                  </view>
                </template>
              </view>
            </view>

            <view v-if="certificateDebugEnabled" class="calibration-tools">
              <view>
                <view class="calibration-title">模板调试模式</view>
                <view v-if="templateDebugMode" class="calibration-template">当前模板：{{ selectedTemplate.key }}</view>
              </view>
              <switch :checked="templateDebugMode" color="#485291" @change="toggleTemplateDebug" />
            </view>

            <view v-if="certificateDebugEnabled && templateDebugMode" class="template-debug-panel">
              <view class="template-debug-title">模板预览切换</view>
              <view class="template-debug-grid">
                <view
                  v-for="item in templateOptions"
                  :key="item.key"
                  class="template-debug-option"
                  :class="{ active: selectedTemplateKey === item.key }"
                  @click="selectDebugTemplate(item.key)"
                >
                  {{ item.shortLabel }}
                </view>
              </view>
            </view>

            <view v-if="certificateDebugEnabled" class="calibration-tools coordinate-tools">
              <view>
                <view class="calibration-title">坐标显示</view>
                <view v-if="coordinateMode" class="calibration-template">显示网格、标记点和坐标列表</view>
              </view>
              <switch :checked="coordinateMode" color="#485291" @change="toggleCoordinate" />
            </view>

            <view v-if="showCoordinateTools" class="coordinate-panel">
              <view v-for="marker in calibrationMarkers" :key="`coord-${marker.key}`" class="coordinate-row">
                <view class="coordinate-name">{{ marker.label }}</view>
                <view class="coordinate-value">left: {{ marker.left }}%; top: {{ marker.top }}%</view>
              </view>
            </view>

            <view class="certificate-actions">
              <view class="button-secondary action-btn" @click="refreshCertificate">重新生成</view>
              <view class="button-primary action-btn" @click="savePoster">保存证书</view>
            </view>
          </template>
        </view>
      </template>
    </view>

    <canvas
      canvas-id="certificateCanvas"
      id="certificateCanvas"
      class="export-canvas"
      :style="{ width: `${canvasWidth}px`, height: `${canvasHeight}px` }"
      :width="canvasWidth"
      :height="canvasHeight"
    />
  </view>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getMemberCertificate } from '../../api/member'
import { getAssetOrigin } from '../../config/env'
import { getBindingDescription, getMember, getMemberAccessState, goLogin, isLoggedIn } from '../../utils/auth'

const assetOrigin = getAssetOrigin()
const templateBaseUrl = `${assetOrigin}/uploads/certificate-templates`
const templateAssetVersion = '20260904-1'
const certificateDebugEnabled = false
const certificateNameFontFamily = 'KaiTi, STKaiti, serif'
const certificateNumberFontFamily = '"Times New Roman", Times, serif'

const templates = {
  memberWithCurrent: {
    key: 'memberWithCurrent',
    label: '会员捐赠人 · 本年有捐赠',
    url: `${templateBaseUrl}/member-with-current.jpg?v=${templateAssetVersion}`,
  },
  memberWithoutCurrent: {
    key: 'memberWithoutCurrent',
    label: '会员捐赠人 · 本年无捐赠',
    url: `${templateBaseUrl}/member-without-current.jpg?v=${templateAssetVersion}`,
  },
  directorWithCurrent: {
    key: 'directorWithCurrent',
    label: '理事捐赠人 · 本年有捐赠',
    url: `${templateBaseUrl}/director-with-current.jpg?v=${templateAssetVersion}`,
  },
  directorWithoutCurrent: {
    key: 'directorWithoutCurrent',
    label: '理事捐赠人 · 本年无捐赠',
    url: `${templateBaseUrl}/director-without-current.jpg?v=${templateAssetVersion}`,
  },
}

const templateOptions = [
  { key: 'memberWithCurrent', shortLabel: '会员有捐赠' },
  { key: 'memberWithoutCurrent', shortLabel: '会员无捐赠' },
  { key: 'directorWithCurrent', shortLabel: '理事有捐赠' },
  { key: 'directorWithoutCurrent', shortLabel: '理事无捐赠' },
]

const canvasWidth = 1870
const canvasHeight = 1322

function position(label, left, top, width, size, canvasSize, maxWidth, weight = '500') {
  return { label, left, top, width, size, canvasSize, maxWidth, weight }
}

// left/top 为相对模板图片左上角的百分比坐标；四套模板分开配置，方便逐个微调。
// size 控制页面预览字体，canvasSize 控制保存到相册后的字体。
const templateFillPositions = {
  memberWithCurrent: {
    donorName: position('姓名', 28.0, 38.85, 13, 18, 33, 230, '700'),
    currentAmount: position('今年金额', 40.7, 46.7, 15, 16, 30, 250),
    totalAmountWithCurrent: position('累计金额', 74.4, 46.7, 15, 16, 30, 270),
    supportYears: position('年头', 46.2, 59.15, 6, 16, 30, 90),
    issuedYear: position('年', 72.15, 80.95, 6, 15, 28, 92),
    issuedMonth: position('月', 77.85, 80.95, 4, 15, 28, 56),
    issuedDay: position('日', 81.45, 80.95, 4, 15, 28, 56),
  },
  memberWithoutCurrent: {
    donorName: position('姓名', 28.0, 38.85, 13, 18, 33, 230, '700'),
    totalAmountWithoutCurrent: position('累计金额', 42.6, 46.7, 15, 16, 30, 270),
    supportYears: position('年头', 46.2, 59.15, 6, 16, 30, 90),
    issuedYear: position('年', 72.15, 80.95, 6, 15, 28, 92),
    issuedMonth: position('月',77.85, 80.95, 4, 15, 28, 56),
    issuedDay: position('日', 81.45, 80.95, 4, 15, 28, 56),
  },
  directorWithCurrent: {
    donorName: position('姓名', 28.0, 38.85, 13, 18, 33, 230, '700'),
    currentAmount: position('今年金额', 42.2, 46.7, 15, 16, 30, 250),
    totalAmountWithCurrent: position('累计金额', 79.4, 46.7, 15, 16, 30, 270),
    supportYears: position('年头', 46.2, 59.15, 6, 16, 30, 90),
    issuedYear: position('年', 72.15, 80.95, 6, 15, 28, 92),
    issuedMonth: position('月', 77.85, 80.95, 4, 15, 28, 56),
    issuedDay: position('日', 81.45, 80.95, 4, 15, 28, 56),
  },
  directorWithoutCurrent: {
    donorName: position('姓名', 28.0, 38.85, 13, 18, 33, 230, '700'),
    totalAmountWithoutCurrent: position('累计金额', 44.5, 46.7, 15, 16, 30, 270),
    supportYears: position('年头', 46.2, 59.15, 6, 16, 30, 90),
    issuedYear: position('年', 72.15, 80.95, 6, 15, 28, 92),
    issuedMonth: position('月', 77.85, 80.95, 4, 15, 28, 56),
    issuedDay: position('日', 81.45, 80.95, 4, 15, 28, 56),
  },
}

const member = ref(getMember())
const posterPath = ref('')
const loading = ref(false)
const errorText = ref('')
const templateImagePath = ref('')
const rawCertificate = ref(null)
const templateDebugMode = ref(false)
const coordinateMode = ref(false)
const debugTemplateKey = ref('')
const templateCacheKey = ref(Date.now())
const previewStageWidth = ref(0)

const loggedIn = computed(() => isLoggedIn())
const memberState = computed(() => getMemberAccessState(member.value))
const stateTitle = computed(() => {
  return {
    pending: '待管理员绑定',
    ambiguous: '待人工处理',
  }[memberState.value] || '当前不可生成证书'
})
const stateDescription = computed(() => getBindingDescription(member.value))

const certificateData = computed(() => {
  const data = rawCertificate.value || {}
  const currentYearAmountValue = Number(data.current_year_amount || 0)
  return {
    donorName: data.donor_name || member.value?.donor_name || member.value?.name || '福莲会员',
    memberLevel: member.value?.member_level || data.member_level || 'member',
    currentYearAmount: formatAmount(currentYearAmountValue),
    totalAmount: formatAmount(data.total_amount),
    supportYears: String(data.support_years || 1),
    hasCurrentDonation: currentYearAmountValue > 0,
  }
})

const autoTemplateKey = computed(() => {
  const isDirector = certificateData.value.memberLevel === 'director'
  const hasCurrent = certificateData.value.hasCurrentDonation
  if (isDirector && hasCurrent) return 'directorWithCurrent'
  if (isDirector) return 'directorWithoutCurrent'
  if (hasCurrent) return 'memberWithCurrent'
  return 'memberWithoutCurrent'
})

const selectedTemplateKey = computed(() => {
  if (certificateDebugEnabled && templateDebugMode.value && debugTemplateKey.value && templates[debugTemplateKey.value]) {
    return debugTemplateKey.value
  }
  return autoTemplateKey.value
})

const selectedTemplate = computed(() => templates[selectedTemplateKey.value])
const selectedTemplateUrl = computed(() => `${selectedTemplate.value.url}&cache=${templateCacheKey.value}`)
const serverPosterUrl = computed(() => {
  if (certificateDebugEnabled && templateDebugMode.value) return ''
  return rawCertificate.value?.poster_url || ''
})
const previewImageUrl = computed(() => serverPosterUrl.value || selectedTemplateUrl.value)
const showOverlayText = computed(() => !serverPosterUrl.value)
const currentPositions = computed(() => templateFillPositions[selectedTemplateKey.value])
const showCoordinateTools = computed(() => certificateDebugEnabled && coordinateMode.value)
const selectedTemplateHasCurrentDonation = computed(() => selectedTemplateKey.value.endsWith('WithCurrent'))
const totalAmountKey = computed(() => {
  return selectedTemplateHasCurrentDonation.value ? 'totalAmountWithCurrent' : 'totalAmountWithoutCurrent'
})

const displayCertificateData = computed(() => {
  if (!certificateDebugEnabled || !templateDebugMode.value) return certificateData.value
  const isDirectorTemplate = selectedTemplateKey.value.startsWith('director')
  return {
    ...certificateData.value,
    currentYearAmount: formatAmount(isDirectorTemplate ? 100000 : 2000),
    totalAmount: formatAmount(isDirectorTemplate ? 1000000 : 20000),
  }
})

const issuedDate = computed(() => {
  const raw = rawCertificate.value?.issued_on
  const date = raw ? new Date(raw) : new Date()
  if (Number.isNaN(date.getTime())) return splitDate(new Date())
  return splitDate(date)
})

const calibrationMarkers = computed(() => {
  const keys = ['donorName']
  if (selectedTemplateHasCurrentDonation.value) keys.push('currentAmount')
  keys.push(totalAmountKey.value, 'supportYears', 'issuedYear', 'issuedMonth', 'issuedDay')
  return keys.map((key) => ({ key, ...currentPositions.value[key] })).filter((item) => item.left !== undefined)
})

function splitDate(date) {
  return {
    year: String(date.getFullYear()),
    month: String(date.getMonth() + 1),
    day: String(date.getDate()),
  }
}

function formatAmount(value) {
  return Number(value || 0).toLocaleString('zh-CN', {
    maximumFractionDigits: 0,
  })
}

function fieldStyle(key) {
  const item = currentPositions.value[key]
  if (!item) return {}
  return {
    left: `${item.left}%`,
    top: `${item.top}%`,
    width: `${item.width}%`,
    fontSize: `${item.size}rpx`,
    fontWeight: item.weight,
    fontFamily: getFieldFontFamily(key),
  }
}

function markerStyle(marker) {
  return {
    left: `${marker.left}%`,
    top: `${marker.top}%`,
  }
}

function pctToX(value) {
  return (Number(value) / 100) * canvasWidth
}

function pctToY(value) {
  return (Number(value) / 100) * canvasHeight
}

function getCanvasFontSize(item) {
  const stageWidth = previewStageWidth.value || uni.getSystemInfoSync().windowWidth
  const previewFontPx = uni.upx2px(item.size)
  return Math.max(10, Math.round((previewFontPx * canvasWidth) / stageWidth))
}

function getFieldFontFamily(key) {
  if (key === 'donorName') return certificateNameFontFamily
  return certificateNumberFontFamily
}

function updatePreviewStageWidth() {
  return new Promise((resolve) => {
    nextTick(() => {
      uni
        .createSelectorQuery()
        .select('.template-stage')
        .boundingClientRect((rect) => {
          if (rect?.width) {
            previewStageWidth.value = rect.width
          }
          resolve()
        })
        .exec()
    })
  })
}

function drawText(ctx, key, text) {
  const item = currentPositions.value[key]
  if (!item || text === undefined || text === null) return
  ctx.setFillStyle('#241f1b')
  ctx.setTextAlign('center')
  ctx.setTextBaseline('middle')
  ctx.font = `${item.weight || '500'} ${getCanvasFontSize(item)}px ${getFieldFontFamily(key)}`
  ctx.fillText(String(text), pctToX(item.left), pctToY(item.top))
}

function resolveImagePath(url) {
  return new Promise((resolve, reject) => {
    uni.downloadFile({
      url,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300 && res.tempFilePath) {
          resolve(res.tempFilePath)
          return
        }
        reject(new Error(`template download failed: ${res.statusCode}`))
      },
      fail: reject,
    })
  })
}

async function ensureTemplateImage() {
  templateImagePath.value = await resolveImagePath(selectedTemplateUrl.value)
}

async function drawCertificate() {
  if (!templateImagePath.value) return
  await updatePreviewStageWidth()
  const ctx = uni.createCanvasContext('certificateCanvas')
  ctx.clearRect(0, 0, canvasWidth, canvasHeight)
  ctx.drawImage(templateImagePath.value, 0, 0, canvasWidth, canvasHeight)

  drawText(ctx, 'donorName', certificateData.value.donorName)
  if (selectedTemplateHasCurrentDonation.value) {
    drawText(ctx, 'currentAmount', displayCertificateData.value.currentYearAmount)
  }
  drawText(ctx, totalAmountKey.value, displayCertificateData.value.totalAmount)
  drawText(ctx, 'supportYears', certificateData.value.supportYears)
  drawText(ctx, 'issuedYear', issuedDate.value.year)
  drawText(ctx, 'issuedMonth', issuedDate.value.month)
  drawText(ctx, 'issuedDay', issuedDate.value.day)

  ctx.draw(false, () => {
    setTimeout(() => {
      uni.canvasToTempFilePath({
        canvasId: 'certificateCanvas',
        x: 0,
        y: 0,
        width: canvasWidth,
        height: canvasHeight,
        destWidth: canvasWidth,
        destHeight: canvasHeight,
        fileType: 'jpg',
        quality: 1,
        success: (res) => {
          posterPath.value = res.tempFilePath
        },
        fail: () => {
          errorText.value = '证书图片生成失败，请重新生成'
        },
      })
    }, 250)
  })
}

async function loadData() {
  member.value = getMember()
  templateCacheKey.value = Date.now()
  posterPath.value = ''
  errorText.value = ''
  rawCertificate.value = null
  templateImagePath.value = ''
  if (!loggedIn.value || memberState.value !== 'bound') return

  loading.value = true
  try {
    const res = await getMemberCertificate()
    if (!res?.total_count) {
      errorText.value = '当前暂无可生成证书的捐赠数据'
      return
    }
    rawCertificate.value = res
    if (serverPosterUrl.value) {
      posterPath.value = ''
      return
    }
    await ensureTemplateImage()
    await drawCertificate()
  } catch (error) {
    console.error('load certificate failed', error)
    errorText.value = '证书数据或模板加载失败，请稍后再试'
  } finally {
    loading.value = false
  }
}

function toggleTemplateDebug(event) {
  if (!certificateDebugEnabled) return
  templateDebugMode.value = !!event.detail.value
  if (templateDebugMode.value && !debugTemplateKey.value) {
    debugTemplateKey.value = autoTemplateKey.value
  }
  if (!templateDebugMode.value) {
    debugTemplateKey.value = ''
  }
}

function toggleCoordinate(event) {
  if (!certificateDebugEnabled) return
  coordinateMode.value = !!event.detail.value
}

function refreshCertificate() {
  templateCacheKey.value = Date.now()
  loadData().catch(() => {})
}

function selectDebugTemplate(key) {
  if (!certificateDebugEnabled) return
  debugTemplateKey.value = key
  templateCacheKey.value = Date.now()
}

function goMy() {
  uni.switchTab({ url: '/pages/my/index' })
}

function previewCertificate() {
  const imageUrl = serverPosterUrl.value || posterPath.value || previewImageUrl.value
  if (!imageUrl) {
    uni.showToast({ title: '证书仍在生成，请稍后再试', icon: 'none' })
    return
  }
  uni.previewImage({
    current: imageUrl,
    urls: [imageUrl],
  })
}

async function savePoster() {
  let filePath = posterPath.value

  const hasAlbumPermission = await ensureSaveAlbumPermission()
  if (!hasAlbumPermission) return

  if (serverPosterUrl.value) {
    try {
      filePath = await resolveImagePath(serverPosterUrl.value)
    } catch (error) {
      console.error('download certificate poster failed', error)
      uni.showToast({ title: '证书下载失败，请稍后再试', icon: 'none' })
      return
    }
  }

  if (!filePath) {
    uni.showToast({ title: '证书仍在生成，请稍后再试', icon: 'none' })
    return
  }
  uni.saveImageToPhotosAlbum({
    filePath,
    success: () => {
      uni.showToast({ title: '已保存到相册', icon: 'none' })
    },
    fail: (error) => {
      const message = String(error?.errMsg || error?.message || '')
      if (isPermissionDenied(message)) {
        showPermissionGuide('需要打开相册权限后才能保存证书')
      } else {
        uni.showToast({ title: '保存失败，请稍后再试', icon: 'none' })
      }
    },
  })
}

function ensureSaveAlbumPermission() {
  return new Promise((resolve) => {
    // #ifndef MP-WEIXIN
    resolve(true)
    // #endif

    // #ifdef MP-WEIXIN
    uni.getSetting({
      success: (setting) => {
        const value = setting.authSetting?.['scope.writePhotosAlbum']
        if (value === true) {
          resolve(true)
          return
        }
        if (value === false) {
          showPermissionGuide('需要打开相册权限后才能保存证书')
          resolve(false)
          return
        }
        uni.authorize({
          scope: 'scope.writePhotosAlbum',
          success: () => resolve(true),
          fail: () => {
            showPermissionGuide('需要打开相册权限后才能保存证书')
            resolve(false)
          },
        })
      },
      fail: () => resolve(true),
    })
    // #endif
  })
}

function isPermissionDenied(message) {
  return /auth|authorize|permission|denied|fail auth|privacy|相册|权限/i.test(message)
}

function showPermissionGuide(content) {
  uni.showModal({
    title: '权限未开启',
    content,
    confirmText: '去设置',
    success: (res) => {
      if (res.confirm) {
        uni.openSetting()
      }
    },
  })
}

onShow(() => {
  loadData().catch(() => {})
})

watch(selectedTemplateKey, async () => {
  if (!rawCertificate.value || loading.value || serverPosterUrl.value) return
  posterPath.value = ''
  errorText.value = ''
  templateCacheKey.value = Date.now()
  try {
    await ensureTemplateImage()
    await drawCertificate()
  } catch (error) {
    console.error('switch certificate template failed', error)
    errorText.value = '证书模板切换失败，请稍后再试'
  }
})
</script>

<style scoped>
.certificate-page {
  background: linear-gradient(180deg, #f3f6fb 0%, #fafcff 42%, #f8fbff 100%);
}

.state-band,
.certificate-panel {
  background: #ffffff;
  padding: 30rpx 28rpx;
}

.certificate-intro {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

.certificate-type {
  flex-shrink: 0;
  color: #a27b42;
  font-size: 22rpx;
  font-weight: 700;
}

.certificate-panel {
  margin-top: 16rpx;
  border-radius: 24rpx;
  box-shadow: 0 16rpx 42rpx rgba(35, 48, 67, 0.06);
}

.certificate-preview {
  padding: 18rpx;
  background: #f8fbff;
  border-radius: 24rpx;
  margin-bottom: 20rpx;
  border: 1px solid rgba(212, 222, 236, 0.9);
}

.template-stage {
  position: relative;
  width: 100%;
  overflow: hidden;
  border-radius: 14rpx;
  background: #fbf4e8;
}

.template-stage.calibrating {
  box-shadow: inset 0 0 0 2rpx rgba(72, 82, 145, 0.5);
}

.template-image {
  display: block;
  width: 100%;
  background: #fbf4e8;
}

.fill-text {
  position: absolute;
  color: #241f1b;
  font-family: "Songti SC", STSong, SimSun, STFangsong, FangSong, serif;
  text-align: center;
  line-height: 1;
  transform: translate(-50%, -50%);
  white-space: nowrap;
}

.calibration-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(to right, rgba(72, 82, 145, 0.18) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(72, 82, 145, 0.18) 1px, transparent 1px),
    linear-gradient(to right, rgba(176, 124, 64, 0.36) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(176, 124, 64, 0.36) 1px, transparent 1px);
  background-size: 10% 10%, 10% 10%, 50% 50%, 50% 50%;
  pointer-events: none;
}

.calibration-axis {
  position: absolute;
  pointer-events: none;
  background: rgba(220, 78, 78, 0.55);
}

.x-axis {
  left: 0;
  right: 0;
  top: 50%;
  height: 1px;
}

.y-axis {
  top: 0;
  bottom: 0;
  left: 50%;
  width: 1px;
}

.calibration-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  pointer-events: none;
  z-index: 5;
}

.marker-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: #d94a48;
  box-shadow: 0 0 0 6rpx rgba(217, 74, 72, 0.18);
}

.marker-label {
  position: absolute;
  left: 14rpx;
  top: 12rpx;
  padding: 4rpx 8rpx;
  border-radius: 6rpx;
  background: rgba(23, 34, 51, 0.82);
  color: #ffffff;
  font-size: 18rpx;
  white-space: nowrap;
}

.calibration-tools {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 76rpx;
  border-bottom: 1rpx solid rgba(218, 226, 238, 0.95);
}

.calibration-title {
  color: #1b2536;
  font-size: 27rpx;
  font-weight: 700;
}

.calibration-template {
  margin-top: 6rpx;
  color: #74829a;
  font-size: 20rpx;
}

.template-debug-panel {
  padding: 18rpx 0 4rpx;
  border-bottom: 1rpx solid rgba(218, 226, 238, 0.95);
}

.template-debug-title {
  margin-bottom: 14rpx;
  color: #1b2536;
  font-size: 24rpx;
  font-weight: 700;
}

.template-debug-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12rpx;
}

.template-debug-option {
  min-height: 64rpx;
  border: 1rpx solid rgba(156, 169, 190, 0.55);
  border-radius: 12rpx;
  color: #536177;
  font-size: 23rpx;
  font-weight: 700;
  line-height: 64rpx;
  text-align: center;
  background: #f8fbff;
}

.template-debug-option.active {
  border-color: #485291;
  color: #ffffff;
  background: #485291;
  box-shadow: 0 10rpx 24rpx rgba(72, 82, 145, 0.18);
}

.coordinate-panel {
  margin: 18rpx 0 22rpx;
  padding: 16rpx 0;
  border-top: 1rpx solid rgba(218, 226, 238, 0.95);
  border-bottom: 1rpx solid rgba(218, 226, 238, 0.95);
}

.coordinate-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  padding: 8rpx 0;
}

.coordinate-name {
  color: #1b2536;
  font-size: 23rpx;
  font-weight: 700;
}

.coordinate-value {
  color: #74829a;
  font-size: 22rpx;
}

.certificate-actions {
  display: flex;
  gap: 16rpx;
  margin-top: 22rpx;
}

.action-btn {
  flex: 1;
}

.state-action {
  margin-top: 24rpx;
}

.export-canvas {
  position: fixed;
  left: -9999px;
  top: -9999px;
  width: 1870px;
  height: 1322px;
  opacity: 0;
  pointer-events: none;
  z-index: 0;
}
</style>
