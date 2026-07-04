<template>
  <view class="page certificate-page">
    <view class="page-shell">
      <view v-if="!loggedIn" class="state-band">
        <view class="section-title">请先登录</view>
        <view class="section-subtitle">登录后可基于本人累计捐赠数据生成正式捐赠证书。</view>
        <view class="button-primary state-action" @click="goLogin">去登录</view>
      </view>

      <view v-else-if="memberState !== 'bound'" class="state-band">
        <view class="section-title">{{ stateTitle }}</view>
        <view class="section-subtitle">{{ stateDescription }}</view>
        <view class="button-secondary state-action" @click="goMy">查看会员状态</view>
      </view>

      <template v-else>
        <view class="state-band certificate-intro">
          <view>
            <view class="section-title">捐赠证书</view>
            <view class="section-subtitle">证书将根据当前会员捐赠记录自动生成，可保存到相册留存。</view>
          </view>
        </view>

        <view class="certificate-panel">
          <view v-if="loading" class="empty-block">证书生成中...</view>
          <view v-else-if="errorText" class="empty-block">{{ errorText }}</view>
          <template v-else>
            <view class="certificate-preview">
              <image
                v-if="posterPath"
                class="certificate-image"
                :src="posterPath"
                mode="widthFix"
                show-menu-by-longpress
              />
              <view v-else class="empty-block preview-empty">证书预览生成中...</view>
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
      class="hidden-canvas"
      :style="{ width: `${canvasWidth}px`, height: `${canvasHeight}px` }"
      :width="canvasWidth"
      :height="canvasHeight"
    />
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getMemberCertificate } from '../../api/member'
import { getBindingDescription, getMember, getMemberAccessState, goLogin, isLoggedIn } from '../../utils/auth'
import { normalizeMediaUrl } from '../../utils/media'
import certificateBorderAsset from '../../static/certificate-border-rococo-v4.jpg'
import certificateTitleAsset from '../../static/certificate-title-gold-sans.png'

const member = ref(getMember())
const posterPath = ref('')
const loading = ref(false)
const errorText = ref('')
const sealImagePath = ref('')
const borderImagePath = ref(certificateBorderAsset)
const titleImagePath = ref(certificateTitleAsset)

const canvasWidth = 1200
const canvasHeight = 1697
const certificateLogoUrl = normalizeMediaUrl('/uploads/system/foundation-logo.jpg')

const loggedIn = computed(() => isLoggedIn())
const memberState = computed(() => getMemberAccessState(member.value))
const stateTitle = computed(() => {
  return {
    pending: '待管理员绑定',
    ambiguous: '待人工处理',
  }[memberState.value] || '当前不可生成证书'
})
const stateDescription = computed(() => getBindingDescription(member.value))

function formatAmount(value) {
  return Number(value || 0).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function formatIssuedOn(value) {
  if (!value) return ''
  const parts = String(value).split('-')
  if (parts.length !== 3) return String(value)
  return `${parts[0]}年${Number(parts[1])}月${Number(parts[2])}日`
}

function wrapText(ctx, text, x, y, maxWidth, lineHeight, firstLineIndent = 0) {
  let line = ''
  let currentY = y
  let currentX = x + firstLineIndent
  let currentMaxWidth = maxWidth - firstLineIndent
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i]
    const testLine = line + char
    if (ctx.measureText(testLine).width > currentMaxWidth && line) {
      ctx.fillText(line, currentX, currentY)
      currentY += lineHeight
      line = char
      currentX = x
      currentMaxWidth = maxWidth
    } else {
      line = testLine
    }
  }
  if (line) {
    ctx.fillText(line, currentX, currentY)
    currentY += lineHeight
  }
  return currentY
}

function applyCanvasFont(ctx, size, family = 'sans-serif', weight = 'normal') {
  ctx.setFontSize(size)
  try {
    ctx.font = `${weight} ${size}px ${family}`
  } catch {
    // Keep miniapp canvas fallback behavior when custom font family is unsupported.
  }
}

function drawFoilText(ctx, text, x, y, options = {}) {
  const {
    size = 100,
    family = 'serif',
    weight = '700',
    align = 'center',
    letterSpacing = 0,
    glow = false,
  } = options

  const gradient = ctx.createLinearGradient(x, y - size, x, y + 24)
  gradient.addColorStop(0, '#f7ebbf')
  gradient.addColorStop(0.22, '#e5cc74')
  gradient.addColorStop(0.5, '#b88d2e')
  gradient.addColorStop(0.78, '#f0dc97')
  gradient.addColorStop(1, '#9f7524')

  ctx.save()
  ctx.setTextAlign(align)
  applyCanvasFont(ctx, size, family, weight)

  if (glow) {
    ctx.setGlobalAlpha(0.22)
    ctx.setFillStyle('#fff6d2')
    drawSpacedText(ctx, text, x, y - 3, letterSpacing, align)
    ctx.setGlobalAlpha(1)
  }

  ctx.setFillStyle('rgba(126, 90, 24, 0.28)')
  drawSpacedText(ctx, text, x, y + 3, letterSpacing, align)
  ctx.setFillStyle(gradient)
  drawSpacedText(ctx, text, x, y, letterSpacing, align)
  ctx.restore()
}

function drawSpacedText(ctx, text, x, y, spacing = 0, align = 'left') {
  if (!spacing) {
    ctx.fillText(text, x, y)
    return
  }

  const chars = String(text).split('')
  let startX = x
  if (align === 'center') {
    const totalWidth =
      chars.reduce((sum, char) => sum + ctx.measureText(char).width, 0) + spacing * Math.max(chars.length - 1, 0)
    startX = x - totalWidth / 2
  } else if (align === 'right') {
    const totalWidth =
      chars.reduce((sum, char) => sum + ctx.measureText(char).width, 0) + spacing * Math.max(chars.length - 1, 0)
    startX = x - totalWidth
  }

  ctx.save()
  ctx.setTextAlign('left')
  let cursorX = startX
  chars.forEach((char) => {
    ctx.fillText(char, cursorX, y)
    cursorX += ctx.measureText(char).width + spacing
  })
  ctx.restore()
}

function strokeEmbossPath(ctx, drawPath, options = {}) {
  const {
    light = 'rgba(201, 172, 149, 0.34)',
    dark = '#7f5655',
    width = 1.5,
    offsetX = 0.9,
    offsetY = 0.9,
  } = options

  ctx.save()
  ctx.translate(offsetX, offsetY)
  ctx.setStrokeStyle(light)
  ctx.setLineWidth(width)
  ctx.beginPath()
  drawPath(ctx)
  ctx.stroke()
  ctx.restore()

  ctx.save()
  ctx.setStrokeStyle(dark)
  ctx.setLineWidth(width)
  ctx.beginPath()
  drawPath(ctx)
  ctx.stroke()
  ctx.restore()
}

function drawCorner(ctx, x, y, scaleX = 1, scaleY = 1) {
  ctx.save()
  ctx.translate(x, y)
  ctx.scale(scaleX, scaleY)
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(0, 128)
    path.bezierCurveTo(0, 36, 36, 0, 128, 0)
  }, { width: 1.45, dark: '#8c5f60' })
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(14, 128)
    path.bezierCurveTo(14, 48, 48, 14, 128, 14)
  }, { width: 1.0, dark: '#a06f6c', light: 'rgba(210, 188, 171, 0.28)' })
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(8, 20)
    path.bezierCurveTo(32, 10, 58, 18, 76, 42)
    path.bezierCurveTo(66, 44, 56, 54, 52, 70)
    path.bezierCurveTo(40, 48, 24, 30, 6, 22)
  }, { width: 1.55, dark: '#7a4d4f' })
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(42, 10)
    path.bezierCurveTo(58, 8, 74, 16, 86, 30)
    path.bezierCurveTo(92, 14, 108, 4, 128, 6)
    path.bezierCurveTo(112, 18, 100, 36, 96, 56)
    path.bezierCurveTo(82, 38, 64, 20, 42, 10)
  }, { width: 1.35, dark: '#835456' })
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(16, 82)
    path.bezierCurveTo(34, 88, 48, 106, 52, 126)
    path.bezierCurveTo(66, 104, 84, 86, 108, 74)
  }, { width: 1.3, dark: '#87585b' })
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(18, 112)
    path.bezierCurveTo(34, 104, 48, 110, 54, 126)
  }, { width: 1.0, dark: '#9c6b69' })
  strokeEmbossPath(ctx, (path) => {
    path.arc(92, 18, 6, 0, Math.PI * 2)
  }, { width: 1.15, dark: '#8d5e5d' })
  strokeEmbossPath(ctx, (path) => {
    path.arc(64, 44, 4.6, 0, Math.PI * 2)
  }, { width: 1.0, dark: '#9a6868' })
  strokeEmbossPath(ctx, (path) => {
    path.arc(30, 92, 4.1, 0, Math.PI * 2)
  }, { width: 0.95, dark: '#9e6d6c' })
  ctx.restore()
}

function drawHeaderOrnament(ctx) {
  ctx.save()
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(410, 126)
    path.bezierCurveTo(458, 84, 516, 74, 566, 94)
    path.bezierCurveTo(582, 68, 594, 58, 600, 58)
    path.bezierCurveTo(606, 58, 618, 68, 634, 94)
    path.bezierCurveTo(684, 74, 742, 84, 790, 126)
  }, { width: 1.65, dark: '#845758' })
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(452, 150)
    path.bezierCurveTo(500, 118, 548, 116, 584, 142)
    path.bezierCurveTo(590, 126, 596, 118, 600, 118)
    path.bezierCurveTo(604, 118, 610, 126, 616, 142)
    path.bezierCurveTo(652, 116, 700, 118, 748, 150)
  }, { width: 1.25, dark: '#916463' })
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(520, 92)
    path.bezierCurveTo(544, 94, 560, 112, 566, 136)
    path.bezierCurveTo(548, 138, 536, 148, 528, 164)
    path.bezierCurveTo(534, 138, 532, 114, 520, 92)
  }, { width: 1.15, dark: '#865859' })
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(680, 92)
    path.bezierCurveTo(656, 94, 640, 112, 634, 136)
    path.bezierCurveTo(652, 138, 664, 148, 672, 164)
    path.bezierCurveTo(666, 138, 668, 114, 680, 92)
  }, { width: 1.15, dark: '#865859' })
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(566, 78)
    path.bezierCurveTo(582, 90, 592, 106, 600, 126)
    path.bezierCurveTo(608, 106, 618, 90, 634, 78)
  }, { width: 1.05, dark: '#9a6b67' })
  strokeEmbossPath(ctx, (path) => {
    path.arc(600, 138, 15.5, 0, Math.PI * 2)
  }, { width: 1.0, dark: '#8f6160' })
  ctx.restore()
}

function drawSideFlourish(ctx, x, y, flipX = 1) {
  ctx.save()
  ctx.translate(x, y)
  ctx.scale(flipX, 1)
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(0, -48)
    path.bezierCurveTo(16, -48, 28, -36, 30, -18)
    path.bezierCurveTo(32, -2, 22, 12, 8, 18)
    path.bezierCurveTo(24, 26, 34, 42, 32, 62)
    path.bezierCurveTo(28, 82, 14, 94, -4, 96)
  }, { width: 1.4 })
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(10, -28)
    path.bezierCurveTo(22, -26, 28, -14, 24, -2)
    path.bezierCurveTo(20, 10, 10, 18, -6, 22)
  }, { width: 1.15 })
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(12, 24)
    path.bezierCurveTo(24, 28, 30, 40, 28, 54)
    path.bezierCurveTo(24, 68, 14, 78, 0, 82)
  }, { width: 1.15 })
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(6, 6)
    path.bezierCurveTo(18, 2, 26, 6, 30, 18)
  }, { width: 1.0 })
  strokeEmbossPath(ctx, (path) => {
    path.arc(24, 10, 4.2, 0, Math.PI * 2)
  }, { width: 1.0 })
  strokeEmbossPath(ctx, (path) => {
    path.arc(22, 48, 3.8, 0, Math.PI * 2)
  }, { width: 1.0 })
  ctx.restore()
}

function drawMiniCornerFlourish(ctx, x, y, scaleX = 1, scaleY = 1) {
  ctx.save()
  ctx.translate(x, y)
  ctx.scale(scaleX, scaleY)
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(0, 26)
    path.bezierCurveTo(0, 8, 8, 0, 26, 0)
  }, { width: 0.95, light: 'rgba(202, 173, 150, 0.24)', dark: 'rgba(157, 111, 101, 0.72)' })
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(4, 10)
    path.bezierCurveTo(12, 10, 18, 14, 20, 24)
  }, { width: 0.95, light: 'rgba(202, 173, 150, 0.24)', dark: 'rgba(157, 111, 101, 0.72)' })
  ctx.restore()
}

function drawLeafPair(ctx, x, y, flipX = 1) {
  ctx.save()
  ctx.translate(x, y)
  ctx.scale(flipX, 1)
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(0, 0)
    path.bezierCurveTo(14, -8, 28, -6, 36, 8)
    path.bezierCurveTo(24, 8, 10, 12, 0, 22)
  }, { width: 0.95, dark: '#9a6a68' })
  strokeEmbossPath(ctx, (path) => {
    path.moveTo(8, 8)
    path.bezierCurveTo(18, 16, 22, 30, 18, 44)
    path.bezierCurveTo(8, 34, 2, 22, 0, 10)
  }, { width: 0.95, dark: '#9a6a68' })
  ctx.restore()
}

function ensureSealImage() {
  if (sealImagePath.value) {
    return Promise.resolve(sealImagePath.value)
  }
  return new Promise((resolve, reject) => {
    uni.getImageInfo({
      src: certificateLogoUrl,
      success: (res) => {
        sealImagePath.value = res.path
        resolve(res.path)
      },
      fail: reject,
    })
  })
}

function ensureBorderImage() {
  if (borderImagePath.value) {
    return Promise.resolve(borderImagePath.value)
  }
  return new Promise((resolve, reject) => {
    uni.getImageInfo({
      src: certificateBorderAsset,
      success: (res) => {
        borderImagePath.value = res.path
        resolve(res.path)
      },
      fail: () => {
        borderImagePath.value = certificateBorderAsset
        resolve(certificateBorderAsset)
      },
    })
  })
}

function ensureTitleImage() {
  if (titleImagePath.value) {
    return Promise.resolve(titleImagePath.value)
  }
  return new Promise((resolve, reject) => {
    uni.getImageInfo({
      src: certificateTitleAsset,
      success: (res) => {
        titleImagePath.value = res.path
        resolve(res.path)
      },
      fail: () => {
        titleImagePath.value = certificateTitleAsset
        resolve(certificateTitleAsset)
      },
    })
  })
}

function drawSealWatermark(ctx) {
  if (!sealImagePath.value) return
  ctx.save()
  const centerX = 600
  const centerY = 820
  const diameter = 520
  const drawX = centerX - diameter / 2
  const drawY = centerY - diameter / 2

  ctx.setGlobalAlpha(0.055)
  ctx.beginPath()
  ctx.arc(centerX, centerY, diameter / 2, 0, Math.PI * 2)
  ctx.clip()
  ctx.drawImage(sealImagePath.value, drawX, drawY, diameter, diameter)
  ctx.restore()
}

function drawSealStamp(ctx) {
  if (!sealImagePath.value) return
  ctx.save()
  const centerX = 840
  const centerY = 1298
  const diameter = 156
  const drawX = centerX - diameter / 2
  const drawY = centerY - diameter / 2

  ctx.setGlobalAlpha(0.82)
  ctx.beginPath()
  ctx.arc(centerX, centerY, diameter / 2, 0, Math.PI * 2)
  ctx.clip()
  ctx.drawImage(sealImagePath.value, drawX, drawY, diameter, diameter)
  ctx.restore()
}

function drawSubtleFrame(ctx, width, height) {
  ctx.save()
  ctx.setStrokeStyle('rgba(149, 103, 98, 0.78)')
  ctx.setLineWidth(1.15)
  ctx.strokeRect(46, 46, width - 92, height - 92)
  ctx.strokeRect(58, 58, width - 116, height - 116)
  ctx.setStrokeStyle('rgba(203, 177, 154, 0.26)')
  ctx.setLineWidth(0.7)
  ctx.strokeRect(72, 72, width - 144, height - 144)
  ctx.restore()

  drawCorner(ctx, 54, 54, 1, 1)
  drawCorner(ctx, width - 54, 54, -1, 1)
  drawCorner(ctx, 54, height - 54, 1, -1)
  drawCorner(ctx, width - 54, height - 54, -1, -1)
  drawMiniCornerFlourish(ctx, 92, 92, 1, 1)
  drawMiniCornerFlourish(ctx, width - 92, 92, -1, 1)
  drawMiniCornerFlourish(ctx, 92, height - 92, 1, -1)
  drawMiniCornerFlourish(ctx, width - 92, height - 92, -1, -1)
  drawSideFlourish(ctx, 72, 380, 1)
  drawSideFlourish(ctx, width - 72, 380, -1)
  drawSideFlourish(ctx, 72, height - 430, 1)
  drawSideFlourish(ctx, width - 72, height - 430, -1)
  drawLeafPair(ctx, 120, 330, 1)
  drawLeafPair(ctx, width - 120, 330, -1)
  drawLeafPair(ctx, 120, height - 380, 1)
  drawLeafPair(ctx, width - 120, height - 380, -1)
  drawHeaderOrnament(ctx)
}

function drawPaperTexture(ctx, width, height) {
  ctx.save()
  ctx.setFillStyle('rgba(120, 102, 78, 0.018)')
  for (let i = 0; i < 24; i += 1) {
    const x = 54 + (i % 6) * 184
    const y = 54 + Math.floor(i / 6) * 392
    ctx.beginPath()
    ctx.arc(x, y, 54, 0, Math.PI * 2)
    ctx.fill()
  }
  ctx.restore()
}

function drawFoilLogo(ctx, centerX, topY, size) {
  if (!sealImagePath.value) return
  const drawX = centerX - size / 2
  const drawY = topY
  const radius = size / 2
  const badgeGradient = ctx.createLinearGradient(drawX, drawY, drawX + size, drawY + size)
  badgeGradient.addColorStop(0, '#fcf6e8')
  badgeGradient.addColorStop(0.5, '#f5edd8')
  badgeGradient.addColorStop(1, '#efe3c0')

  ctx.save()
  ctx.setGlobalAlpha(0.1)
  ctx.setFillStyle('rgba(176, 141, 71, 0.18)')
  ctx.beginPath()
  ctx.arc(centerX, drawY + radius + 4, radius + 12, 0, Math.PI * 2)
  ctx.fill()
  ctx.restore()

  ctx.save()
  ctx.beginPath()
  ctx.arc(centerX, drawY + radius, radius, 0, Math.PI * 2)
  ctx.clip()
  ctx.setFillStyle(badgeGradient)
  ctx.fillRect(drawX, drawY, size, size)
  const inset = 10
  ctx.setGlobalAlpha(1)
  ctx.drawImage(sealImagePath.value, drawX + inset, drawY + inset, size - inset * 2, size - inset * 2)
  ctx.setGlobalAlpha(0.18)
  ctx.setFillStyle('rgba(214, 191, 129, 0.95)')
  ctx.fillRect(drawX + inset, drawY + inset, size - inset * 2, size - inset * 2)
  ctx.restore()

  ctx.save()
  ctx.setStrokeStyle('rgba(190, 151, 62, 0.92)')
  ctx.setLineWidth(2.2)
  ctx.beginPath()
  ctx.arc(centerX, drawY + radius, radius + 1.5, 0, Math.PI * 2)
  ctx.stroke()
  ctx.setStrokeStyle('rgba(222, 201, 138, 0.82)')
  ctx.setLineWidth(1.1)
  ctx.beginPath()
  ctx.arc(centerX, drawY + radius, radius - 5.5, 0, Math.PI * 2)
  ctx.stroke()
  ctx.restore()
}

function drawTopIdentity(ctx, width) {
  if (!sealImagePath.value) return
  drawFoilLogo(ctx, width - 255, 1110, 124)
}

function drawHighlightedName(ctx, data) {
  const prefix = '尊敬的 '
  const suffix = ' 理事：'
  const startX = 166
  const baselineY = 638

  ctx.setFillStyle('#4e4032')
  applyCanvasFont(ctx, 38, '"STSong","SimSun",serif', '600')
  ctx.fillText(prefix, startX, baselineY)

  const prefixWidth = ctx.measureText(prefix).width
  const nameX = startX + prefixWidth
  applyCanvasFont(ctx, 48, '"STSong","SimSun",serif', '700')
  ctx.fillText(data.donor_name, nameX, baselineY)
  ctx.fillText(data.donor_name, nameX + 1.2, baselineY)

  const nameWidth = ctx.measureText(data.donor_name).width
  applyCanvasFont(ctx, 38, '"STSong","SimSun",serif', '600')
  ctx.fillText(suffix, nameX + nameWidth + 8, baselineY)
}

function exportPoster() {
  uni.canvasToTempFilePath({
    canvasId: 'certificateCanvas',
    x: 0,
    y: 0,
    width: canvasWidth,
    height: canvasHeight,
    destWidth: canvasWidth,
    destHeight: canvasHeight,
    fileType: 'png',
    quality: 1,
    success: (res) => {
      posterPath.value = res.tempFilePath
    },
    fail: () => {
      errorText.value = '证书生成失败，请稍后再试'
    },
  })
}

function drawCertificate(data) {
  const ctx = uni.createCanvasContext('certificateCanvas')
  const width = canvasWidth
  const height = canvasHeight

  ctx.setFillStyle('#faf7f1')
  ctx.fillRect(0, 0, width, height)
  const borderSrc = borderImagePath.value || certificateBorderAsset
  if (borderSrc) {
    ctx.drawImage(borderSrc, 0, 0, width, height)
  } else {
    ctx.setFillStyle('#f8f4ea')
    ctx.fillRect(0, 0, width, height)
    ctx.setFillStyle('#f5efe2')
    ctx.fillRect(24, 24, width - 48, height - 48)
    ctx.setFillStyle('rgba(255, 252, 245, 0.94)')
    ctx.fillRect(78, 78, width - 156, height - 156)
    drawPaperTexture(ctx, width, height)
    drawSubtleFrame(ctx, width, height)
  }
  drawSealWatermark(ctx)
  drawTopIdentity(ctx, width)

  const titleSrc = titleImagePath.value || certificateTitleAsset
  if (titleSrc) {
    const titleWidth = 470
    const titleHeight = 140
    ctx.drawImage(titleSrc, width / 2 - titleWidth / 2, 344, titleWidth, titleHeight)
  } else {
    drawFoilText(ctx, '捐赠证书', width / 2, 438, {
      size: 108,
      family: '"STXinwei","华文新魏","STLiti","LiSu","STSong",serif',
      weight: '700',
      align: 'center',
      letterSpacing: 6,
      glow: true,
    })
  }

  drawFoilText(ctx, 'CERTIFICATE OF DONATION', width / 2, 508, {
    size: 26,
    family: '"Times New Roman","Times",serif',
    weight: '700',
    align: 'center',
    letterSpacing: 3,
  })

  drawHighlightedName(ctx, data)

  applyCanvasFont(ctx, 34, '"STSong","SimSun",serif', '600')
  ctx.setFillStyle('#4a433c')
  const lines = [
    `感谢您今年捐赠人民币 ${formatAmount(data.current_year_amount)} 元，截至目前，您已累计捐赠 ${formatAmount(data.total_amount)} 元。`,
    '您的福业，福莲的未来。您的每一分捐赠，都将用于连城教育事业的发展！',
    '花开福莲，香溢四海！',
  ]

  let y = 760
  lines.forEach((line, index) => {
    y = wrapText(ctx, line, 188, y, 824, 76, 50)
    y += index === lines.length - 1 ? 0 : 20
  })

  ctx.setFillStyle('#4c4338')
  ctx.setTextAlign('right')
  applyCanvasFont(ctx, 38, '"STSong","SimSun",serif', '600')
  ctx.fillText('福莲教育促进会', width - 156, 1328)
  applyCanvasFont(ctx, 32, '"STSong","SimSun",serif', '600')
  ctx.fillText(formatIssuedOn(data.issued_on), width - 156, 1390)
  ctx.setTextAlign('left')

  ctx.draw(false, () => {
    setTimeout(() => {
      exportPoster()
    }, 180)
  })
}

async function loadData() {
  member.value = getMember()
  posterPath.value = ''
  errorText.value = ''
  if (!loggedIn.value || memberState.value !== 'bound') return

  loading.value = true
  try {
    await Promise.all([ensureSealImage(), ensureBorderImage(), ensureTitleImage()])
    const res = await getMemberCertificate()
    if (!res?.total_count) {
      errorText.value = '当前暂无可生成证书的捐赠数据'
      return
    }
    drawCertificate(res)
  } catch {
    errorText.value = '证书数据加载失败，请稍后再试'
  } finally {
    loading.value = false
  }
}

function refreshCertificate() {
  loadData().catch(() => {})
}

function goMy() {
  uni.switchTab({ url: '/pages/my/index' })
}

function savePoster() {
  if (!posterPath.value) {
    uni.showToast({ title: '证书仍在生成，请稍后再试', icon: 'none' })
    return
  }
  uni.saveImageToPhotosAlbum({
    filePath: posterPath.value,
    success: () => {
      uni.showToast({ title: '已保存到相册', icon: 'none' })
    },
    fail: () => {
      uni.showToast({ title: '保存失败，请检查系统权限', icon: 'none' })
    },
  })
}

onShow(() => {
  loadData().catch(() => {})
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
  align-items: flex-start;
  justify-content: space-between;
  gap: 20rpx;
}

.intro-chip {
  flex-shrink: 0;
  min-width: 108rpx;
  height: 52rpx;
  padding: 0 18rpx;
  border-radius: 999rpx;
  background: #f4ede3;
  color: #8b6c3f;
  font-size: 22rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.certificate-panel {
  margin-top: 16rpx;
  border-radius: 24rpx;
  box-shadow: 0 16rpx 42rpx rgba(35, 48, 67, 0.06);
}

.certificate-preview {
  padding: 22rpx;
  background: linear-gradient(180deg, #f7f2e8 0%, #fdfaf3 100%);
  border-radius: 24rpx;
  margin-bottom: 24rpx;
  border: 1px solid rgba(214, 199, 165, 0.8);
}

.certificate-image {
  display: block;
  width: 100%;
  border-radius: 18rpx;
  background: #f8f1e4;
}

.preview-empty {
  padding: 60rpx 20rpx;
}

.certificate-actions {
  display: flex;
  gap: 16rpx;
}

.action-btn {
  flex: 1;
}

.state-action {
  margin-top: 24rpx;
}

.hidden-canvas {
  position: fixed;
  left: -9999px;
  top: -9999px;
  opacity: 0;
  pointer-events: none;
}
</style>
