const TOKEN_KEY = 'member_token'
const MEMBER_KEY = 'member_profile'

export function getToken() {
  return uni.getStorageSync(TOKEN_KEY) || ''
}

export function setToken(token) {
  uni.setStorageSync(TOKEN_KEY, token)
}

export function clearToken() {
  uni.removeStorageSync(TOKEN_KEY)
}

export function getMember() {
  return uni.getStorageSync(MEMBER_KEY) || null
}

export function setMember(member) {
  uni.setStorageSync(MEMBER_KEY, member)
}

export function clearMember() {
  uni.removeStorageSync(MEMBER_KEY)
}

export function isLoggedIn() {
  return !!getToken()
}

export function getBindingStatus(member = getMember()) {
  return member?.binding_status || 'guest'
}

export function isBoundMember(member = getMember()) {
  return getBindingStatus(member) === 'bound'
}

export function isBindingPending(member = getMember()) {
  return getBindingStatus(member) === 'unbound'
}

export function isBindingAmbiguous(member = getMember()) {
  return getBindingStatus(member) === 'ambiguous'
}

export function getMemberAccessState(member = getMember()) {
  if (!member) return 'guest'
  if (isBoundMember(member)) return 'bound'
  if (isBindingPending(member)) return 'pending'
  if (isBindingAmbiguous(member)) return 'ambiguous'
  return 'member'
}

export function getBindingText(member = getMember()) {
  return {
    guest: '尚未登录',
    bound: '已完成绑定',
    pending: '待管理员绑定',
    ambiguous: '待人工处理',
    member: '状态待确认',
  }[getMemberAccessState(member)]
}

export function getBindingBadgeClass(member = getMember()) {
  return {
    guest: 'badge-info',
    bound: 'badge-success',
    pending: 'badge-warning',
    ambiguous: 'badge-danger',
    member: 'badge-info',
  }[getMemberAccessState(member)]
}

export function getBindingDescription(member = getMember()) {
  return {
    guest: '登录后可查看本人捐赠、开票申请、会员通讯录与基金公示信息。',
    bound: '当前手机号已完成资料匹配，可以正常使用会员专属服务。',
    pending: '当前手机号尚未匹配到唯一捐赠人，请联系后台管理员完成绑定。',
    ambiguous: '当前手机号匹配到多条记录，需要后台人工确认后开放完整能力。',
    member: '当前会员状态待确认，请稍后再试或联系管理员。',
  }[getMemberAccessState(member)]
}

export function getMemberLevelLabel(member = getMember()) {
  return member?.member_level_label || '非会员'
}

export function getMemberLevelClass(member = getMember()) {
  return {
    director: 'badge-primary',
    member: 'badge-info',
    non_member: 'badge-muted',
  }[member?.member_level || 'non_member']
}

export function goLogin() {
  uni.navigateTo({ url: '/pages/login/index' })
}

export function requireMemberAuth() {
  if (!isLoggedIn()) {
    goLogin()
    return false
  }
  return true
}

export function clearAuth() {
  clearToken()
  clearMember()
}

export function logoutMember() {
  clearAuth()
}
