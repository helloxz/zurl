<template>
  <div class="home-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="nav-content">
        <h1 class="logo">{{ siteInfo.title }}</h1>
        <div class="nav-links">
          <a href="https://github.com/helloxz/zurl" :title="$t('go.to.github')" target="_blank" class="github-link">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            GitHub
          </a>
          <router-link to="/login" v-if="!siteStore.is_login" class="login-btn">{{ $t('login') }}</router-link>
          <router-link to="/admin" v-if="siteStore.is_login" class="login-btn">{{ $t('admin') }}</router-link>
        </div>
      </div>
    </nav>

    <!-- 主内容 -->
    <main class="main-content">
      <div class="hero-section">
        <h2 class="hero-title">{{ $t('quickly.shorten.your.link') }}</h2>
        <p class="hero-subtitle">{{ $t('quickly.shorten.your.link.subtitle') }}</p>

        <!-- 表单 -->
        <div class="form-container">
          <el-form 
            :model="formData"
            ref="formRef"
            :rules="rules"
            class="shorten-form"
          >
            <el-form-item prop="long_url" class="url-input-item">
              <el-input
                v-model="formData.long_url"
                :placeholder="$t('home.long_url.placeholder')"
                class="url-input"
                size="large"
              />
            </el-form-item>

            <!-- 高级选项 -->
            <div class="advanced-options" v-if="showAdvanced">
              <el-form-item prop="short_url" class="custom-url-item">
                <div class="custom-url-container">
                  <span class="domain-label">{{ getMainDomain() }}/</span>
                  <el-input
                    v-model="formData.short_url"
                    :placeholder="$t('home.custom_short_url.placeholder')"
                    class="custom-input"
                    size="large"
                  />
                </div>
              </el-form-item>
            </div>

            <div class="form-actions">
              <el-button 
                type="primary" 
                @click="shortenUrl"
                class="shorten-btn"
                size="large"
                :loading="loading"
              >
                {{ loading ? $t('creating') : $t('create.short_url') }}
              </el-button>
              <el-button 
                type="text" 
                @click="showAdvanced = !showAdvanced"
                class="advanced-toggle"
              >
                {{ showAdvanced ? $t('hide') : $t('advanced.options') }}
              </el-button>
            </div>
          </el-form>

          <!-- 结果展示 -->
          <div v-if="result" class="result-container">
            <div class="result-item">
              <label>{{ $t('home.short_url.label') }}</label>
              <div class="result-value">
                <span class="short-url">{{ getShortUrl(result.short_url) }}</span>
                <el-button 
                  type="text" 
                  @click="baseStore.copyText(getShortUrl(result.short_url))"
                  class="copy-btn"
                >
                  {{ $t('copy') }}
                </el-button>
              </div>
            </div>
            <div class="result-item">
              <label>{{ $t('original.url.label') }}</label>
              <div class="result-value">
                <span class="long-url">{{ result.long_url }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <p>&copy; 2025 Powered by <a style="color: #ffffff;text-decoration: none;" href="https://github.com/helloxz/zurl" target="_blank" rel="noopener noreferrer">Zurl</a>. {{ siteInfo.footer }}</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import req from '@/utils/req'
import { ElMessage } from 'element-plus'
import { useSiteStore } from '@/stores/site'
import { useBaseStore } from '@/stores/base'
import { useI18n } from 'vue-i18n'

const router = useRouter()

const { t, locale } = useI18n()

const formRef = ref(null)
const loading = ref(false)
const showAdvanced = ref(false)
const result = ref(null)

const siteStore = useSiteStore()
const baseStore = useBaseStore()

// 网站信息
const siteInfo = ref({
  title:"",
  footer:""
})

// 定义基础 URL（支持非根目录部署）
const baseUrl = computed(() => {
  if (typeof window !== 'undefined') {
    const base = (window.__BASE_PATH__ || import.meta.env.VITE_BASE_URL || '').replace(/\/$/, '')
    return base ? `${window.location.origin}${base}` : window.location.origin
  }
  return ''
})

// 获取主域名（含 base path 时显示为 host/path）
const getMainDomain = () => {
  const base = (window.__BASE_PATH__ || import.meta.env.VITE_BASE_URL || '').replace(/\/$/, '')
  return base ? `${window.location.host}${base}` : window.location.host
}

const formData = ref({
  long_url: '',
  short_url: '',
  title: ''
})

// 短链接仅允许：大小写字母、数字、-_@#$%^&*，禁止 / 或 \
const shortUrlValidator = (_rule, value, callback) => {
  if (!value || !String(value).trim()) {
    callback()
    return
  }
  const v = String(value).trim()
  if (/\/|\\/.test(v)) {
    callback(new Error(t('invalid.short.url.slash')))
    return
  }
  if (!/^[a-zA-Z0-9_\-@#$%^&*]{1,32}$/.test(v)) {
    callback(new Error(t('invalid.short.url')))
    return
  }
  callback()
}

const rules = {
  long_url: [
    { required: true, message: t('home.long_url.required'), trigger: 'blur' },
    { type: 'url', message: t('home.long_url.url'), trigger: 'blur' }
  ],
  short_url: [
    { validator: shortUrlValidator, trigger: 'blur' }
  ]
}

onMounted(async () => {
  // 先拉取站点配置（含 allow_guest_shorten）
  await siteStore.getSiteInfo()
  siteInfo.value.title = siteStore.site_info.title
  siteInfo.value.footer = siteStore.site_info.footer

  // 未登录时再请求一次确认登录状态
  if (siteStore.is_login === false) {
    try {
      const res = await req.get('/api/user/is_login')
      siteStore.is_login = res.data?.code === 200
    } catch {
      siteStore.is_login = false
    }
  }

  // 仅登录用户可创建短链且未登录时，直接跳转登录页
  if (siteStore.site_info.allow_guest_shorten === false && !siteStore.is_login) {
    router.push('/login')
    return
  }
})

// 缩短链接（若站点设置为仅登录用户可创建且未登录，则先提示）
const shortenUrl = () => {
  formRef.value.validate((valid) => {
    if (!valid) return
    const allowGuest = siteStore.site_info.allow_guest_shorten !== false
    if (!allowGuest && !siteStore.is_login) {
      ElMessage.error(t('no.login.msg'))
      return
    }
    loading.value = true
    req.post("/api/shorten_url", formData.value)
      .then(res => {
        if (res.data.code === 200) {
          result.value = res.data.data
          formData.value = {
            long_url: '',
            short_url: '',
            title: ''
          }
        } else {
          ElMessage.error(t(res.data.msg) || t('link.add.error'))
        }
      })
      .catch(err => {
        console.error(err)
        if (err.response && err.response.status === 401) {
          ElMessage.error(t('no.login.msg'))
          return
        }
        ElMessage.error(t('link.add.error'))
      })
      .finally(() => {
        loading.value = false
      })
  })
}

// 生成完整的短链接 URL（含 base path）
const getShortUrl = (shortUrl) => {
  const base = (window.__BASE_PATH__ || import.meta.env.VITE_BASE_URL || '').replace(/\/$/, '')
  const path = base ? `${base}/${shortUrl}` : shortUrl
  return base ? `${window.location.origin}${path}` : `${window.location.origin}/${shortUrl}`
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #ffffff;
  display: flex;
  flex-direction: column;
}

/* 导航栏 */
.navbar {
  background: rgba(26, 26, 46, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem 0;
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.8rem;
  font-weight: bold;
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.github-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #ffffff;
  text-decoration: none;
  opacity: 0.8;
  transition: opacity 0.3s;
}

.github-link:hover {
  opacity: 1;
}

.login-btn {
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  color: white;
  padding: 0.5rem 1.5rem;
  border-radius: 25px;
  text-decoration: none;
  font-weight: 500;
  transition: transform 0.3s;
}

.login-btn:hover {
  transform: translateY(-2px);
}

/* 主内容 */
.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.hero-section {
  text-align: center;
  max-width: 600px;
  width: 100%;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.2rem;
  opacity: 0.8;
  margin-bottom: 3rem;
}

/* 表单样式 */
.form-container {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.shorten-form {
  margin-bottom: 2rem;
}

.url-input-item {
  margin-bottom: 1.5rem;
}

:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  transition: all 0.3s;
}

:deep(.el-input__wrapper:hover) {
  border-color: rgba(79, 172, 254, 0.5);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #4facfe;
  box-shadow: 0 0 20px rgba(79, 172, 254, 0.3);
}

:deep(.el-input__inner) {
  color: #ffffff;
  font-size: 1.1rem;
}

:deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.5);
}

/* 自定义短链接样式 */
.custom-url-container {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  width: 100%;
}

.custom-url-container:hover {
  border-color: rgba(79, 172, 254, 0.5);
  background: rgba(255, 255, 255, 0.12);
}

.custom-url-container:focus-within {
  border-color: #4facfe;
  box-shadow: 0 0 20px rgba(79, 172, 254, 0.3);
  background: rgba(255, 255, 255, 0.15);
}

.domain-label {
  background: linear-gradient(45deg, rgba(79, 172, 254, 0.3), rgba(0, 242, 254, 0.3));
  color: #ffffff;
  padding: 0 16px;
  font-size: 1.1rem;
  font-weight: 500;
  white-space: nowrap;
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  height: 40px;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.custom-url-container:focus-within .domain-label {
  background: linear-gradient(45deg, rgba(79, 172, 254, 0.5), rgba(0, 242, 254, 0.5));
  border-right-color: #4facfe;
}

.custom-url-item :deep(.el-input) {
  flex: 1;
}

.custom-url-item :deep(.el-input__wrapper) {
  background: transparent;
  border: none;
  border-radius: 0;
  box-shadow: none;
  padding: 0 16px;
}

.custom-url-item :deep(.el-input__wrapper:hover) {
  background: transparent;
  border: none;
  box-shadow: none;
}

.custom-url-item :deep(.el-input__wrapper.is-focus) {
  background: transparent;
  border: none;
  box-shadow: none;
}

.custom-url-item :deep(.el-input__inner) {
  color: #ffffff;
  font-size: 1.1rem;
  height: 40px;
}

.custom-url-item :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.5);
}

:deep(.el-input-group__prepend) {
  display: none;
}

:deep(.el-input-group .el-input__wrapper) {
  border-left: unset;
  border-radius: 12px;
}

:deep(.el-input-group__prepend:hover + .el-input .el-input__wrapper) {
  border-color: rgba(79, 172, 254, 0.5);
}

:deep(.el-input-group .el-input__wrapper.is-focus) {
  border-color: #4facfe;
  box-shadow: 0 0 20px rgba(79, 172, 254, 0.3);
}

:deep(.el-input-group .el-input__wrapper.is-focus + .el-input-group__prepend),
:deep(.el-input-group__prepend + .el-input .el-input__wrapper.is-focus) {
  border-color: #4facfe;
}

:deep(.el-input-group:has(.el-input__wrapper.is-focus) .el-input-group__prepend) {
  border-color: #4facfe;
}

:deep(.el-input-group__prepend + .el-input .el-input__wrapper:hover) {
  border-color: rgba(79, 172, 254, 0.5);
}

:deep(.el-input-group:hover .el-input-group__prepend) {
  border-color: rgba(79, 172, 254, 0.5);
}

.advanced-options {
  margin-bottom: 1.5rem;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
}

.shorten-btn {
  background: linear-gradient(45deg, #4facfe, #00f2fe);
  border: none;
  border-radius: 25px;
  padding: 0.8rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  transition: transform 0.3s;
}

:deep(.shorten-btn:hover) {
  transform: translateY(-2px);
  background: linear-gradient(45deg, #4facfe, #00f2fe);
}

.advanced-toggle {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: underline;
}

/* 结果展示 */
.result-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.result-item {
  margin-bottom: 1rem;
  text-align: left;
}

.result-item label {
  display: block;
  font-size: 0.9rem;
  opacity: 0.7;
  margin-bottom: 0.5rem;
}

.result-value {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.05);
  padding: 0.8rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.short-url {
  color: #4facfe;
  font-weight: 600;
  flex: 1;
  word-break: break-all;
}

.long-url {
  flex: 1;
  opacity: 0.8;
  word-break: break-all;
}

.copy-btn {
  color: #4facfe;
  font-size: 0.9rem;
  flex-shrink: 0;
}

/* 页脚 */
.footer {
  text-align: center;
  padding: 2rem;
  opacity: 0.6;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-content {
    padding: 0 1rem;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .form-container {
    padding: 1.5rem;
    margin: 0 0rem;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .result-value {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .copy-btn {
    align-self: flex-end;
  }
  .main-content{
    align-items: start;
  }
}

@media (max-width: 480px) {
  .nav-links {
    gap: 1rem;
  }
  
  .github-link span {
    display: none;
  }
  
  .hero-title {
    font-size: 1.8rem;
  }
  
  .main-content {
    padding: 1rem;
    align-items: start;
  }

  .form-container {
    padding: 1.5rem;
    margin: 0 0rem;
  }
}
</style>