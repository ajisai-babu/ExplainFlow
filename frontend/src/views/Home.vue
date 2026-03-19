<script setup>
import { ref, reactive, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useI18n } from '../i18n/index.js'

const { locale, t, toggleLocale } = useI18n()

// API base URL: uses env var in dev, relative path in Docker/production
const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const form = reactive({
  topic: '',
  bilingual: true,
  resolution: '1080p',
  tech_details: '',
  model: '',
  api_key: '',
  base_url: 'https://api.deepseek.com/v1'
})

const loading = ref(false)
const error = ref('')
const generatedHtml = ref('')
const previewFrame = ref(null)
const iframeContainer = ref(null)
const progressCount = ref(0)
const showRawStream = ref(false)
const rawStreamContent = ref('')
const previewScale = ref(1)
const aborted = ref(false)
let currentAbortController = null

// Resolution map for iframe native dimensions
const resolutionMap = {
  '1080p': { width: 1920, height: 1080 },
  '2k': { width: 2560, height: 1440 },
  '4k': { width: 3840, height: 2160 },
}
const nativeRes = computed(() => resolutionMap[form.resolution] || resolutionMap['1080p'])

// Compute scale to fit the native resolution into the container
const updatePreviewScale = () => {
  if (!iframeContainer.value) return
  const containerWidth = iframeContainer.value.clientWidth
  const containerHeight = iframeContainer.value.clientHeight
  const scaleX = containerWidth / nativeRes.value.width
  const scaleY = containerHeight / nativeRes.value.height
  previewScale.value = Math.min(scaleX, scaleY)
}

let resizeObserver = null
onMounted(() => {
  resizeObserver = new ResizeObserver(updatePreviewScale)
  if (iframeContainer.value) {
    resizeObserver.observe(iframeContainer.value)
  }
})
onUnmounted(() => {
  if (resizeObserver) resizeObserver.disconnect()
})

// Model config state
const apiType = ref('openai-completions')
const compatibleNewApi = ref(false)
const modelList = ref([])
const fetchingModels = ref(false)
const testingConnection = ref(false)
const connectionStatus = ref(null) // { success: bool, message: string }
const modelInputVisible = ref(false)
const newModelName = ref('')

const handleFetchModels = async () => {
  if (!form.base_url) {
    error.value = t.value('errorBaseUrlRequired')
    return
  }
  if (!form.api_key) {
    error.value = t.value('errorApiKeyFirst')
    return
  }
  error.value = ''
  fetchingModels.value = true
  try {
    const resp = await fetch(`${API_BASE}/fetch-models`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        base_url: form.base_url,
        api_key: form.api_key,
        api_type: apiType.value,
        compatible_new_api: compatibleNewApi.value
      })
    })
    const data = await resp.json()
    if (data.models && data.models.length > 0) {
      modelList.value = data.models
      if (!form.model && data.models.length > 0) {
        form.model = data.models[0]
      }
    }
    connectionStatus.value = { success: data.models?.length > 0, message: data.message }
  } catch (e) {
    connectionStatus.value = { success: false, message: t.value('errorRequestFailed') + e.message }
  } finally {
    fetchingModels.value = false
  }
}

const handleTestConnection = async () => {
  if (!form.base_url) {
    error.value = t.value('errorBaseUrlRequired')
    return
  }
  if (!form.api_key) {
    error.value = t.value('errorApiKeyFirst')
    return
  }
  error.value = ''
  testingConnection.value = true
  connectionStatus.value = null
  try {
    const resp = await fetch(`${API_BASE}/test-connection`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        base_url: form.base_url,
        api_key: form.api_key,
        api_type: apiType.value
      })
    })
    const data = await resp.json()
    connectionStatus.value = data
  } catch (e) {
    connectionStatus.value = { success: false, message: t.value('errorRequestFailed') + e.message }
  } finally {
    testingConnection.value = false
  }
}

const addModelManually = () => {
  const name = newModelName.value.trim()
  if (name && !modelList.value.includes(name)) {
    modelList.value.push(name)
    if (!form.model) form.model = name
  }
  newModelName.value = ''
  modelInputVisible.value = false
}

const removeModel = (index) => {
  const removed = modelList.value[index]
  modelList.value.splice(index, 1)
  if (form.model === removed) {
    form.model = modelList.value.length > 0 ? modelList.value[0] : ''
  }
}

const cleanMarkdown = (text) => {
  // Try to find content between ```html and ```
  const htmlMatch = text.match(/```html\s*([\s\S]*?)\s*```/i);
  if (htmlMatch && htmlMatch[1]) {
    return htmlMatch[1].trim();
  }
  
  // Try to find content between generic ``` and ```
  const genericMatch = text.match(/```\s*([\s\S]*?)\s*```/);
  if (genericMatch && genericMatch[1]) {
    return genericMatch[1].trim();
  }

  // If no markdown blocks found, but <html> exists, try to extract from <html> to </html>
  const tagMatch = text.match(/<html[\s\S]*?<\/html>/i);
  if (tagMatch) {
    return tagMatch[0].trim();
  }
  
  // Fallback to original trimming logic if no blocks found
  return text.trim().replace(/^```html\s*/i, '').replace(/\s*```$/i, '');
}

const handleGenerate = async () => {
  if (!form.topic) {
    error.value = t.value('errorTopicRequired')
    return
  }
  if (!form.api_key) {
    error.value = t.value('errorApiKeyRequired')
    return
  }

  error.value = ''
  loading.value = true
  aborted.value = false
  generatedHtml.value = ''
  progressCount.value = 0
  rawStreamContent.value = ''
  
  // Create a new AbortController for this request
  currentAbortController = new AbortController()
  const signal = currentAbortController.signal
  
  try {
    const response = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      signal,
      body: JSON.stringify({
        topic: form.topic,
        bilingual: form.bilingual,
        tech_details: form.tech_details,
        resolution: form.resolution,
        api_key: form.api_key,
        base_url: form.base_url || null,
        model: form.model
      })
    });

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || t.value('errorGenericFail'));
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let result = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value, { stream: true });
      if (chunk.startsWith('ERROR:')) {
        throw new Error(chunk.replace('ERROR:', ''));
      }
      result += chunk;
      rawStreamContent.value = result;
      progressCount.value = result.length;
    }
    
    const finalHtml = cleanMarkdown(result);
    generatedHtml.value = finalHtml;
    
    // Auto-update iframe content
    await nextTick()
    updatePreviewScale()
    if (previewFrame.value) {
      const doc = previewFrame.value.contentWindow.document
      doc.open()
      doc.write(finalHtml)
      doc.close()
    }
    
  } catch (err) {
    if (err.name === 'AbortError') {
      // User aborted — try to render what we have so far
      const partial = rawStreamContent.value
      if (partial) {
        const partialHtml = cleanMarkdown(partial)
        if (partialHtml) {
          generatedHtml.value = partialHtml
          await nextTick()
          updatePreviewScale()
          if (previewFrame.value) {
            const doc = previewFrame.value.contentWindow.document
            doc.open()
            doc.write(partialHtml)
            doc.close()
          }
        }
      }
      error.value = t.value('errorAborted')
      aborted.value = true
    } else {
      error.value = err.message
    }
  } finally {
    currentAbortController = null
    loading.value = false
  }
}

const handleAbort = () => {
  if (currentAbortController) {
    currentAbortController.abort()
  }
}

const downloadHtml = () => {
  if (!generatedHtml.value) return
  
  const blob = new Blob([generatedHtml.value], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  
  const a = document.createElement('a')
  a.href = url
  // create a safe filename
  const filename = form.topic.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/gi, '_').toLowerCase() + '_动画.html'
  a.download = filename || 'animation.html'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="app-container">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo-icon">✨</div>
        <h1>ExplainFlow</h1>
        <button class="lang-toggle" @click="toggleLocale" :title="locale === 'zh' ? 'Switch to English' : '切换至中文'">
          <span class="lang-label" :class="{ active: locale === 'zh' }">中</span>
          <span class="lang-divider">/</span>
          <span class="lang-label" :class="{ active: locale === 'en' }">En</span>
        </button>
      </div>
      
      <div class="form-group">
        <label>{{ t('animationTopic') }}</label>
        <input v-model="form.topic" type="text" :placeholder="t('topicPlaceholder')" />
      </div>

      <div class="form-row">
        <div class="form-group toggle-group">
          <label>{{ t('bilingualSubtitle') }}</label>
          <label class="switch">
            <input type="checkbox" v-model="form.bilingual">
            <span class="slider round"></span>
          </label>
        </div>

        <div class="form-group">
          <label>{{ t('resolution') }}</label>
          <select v-model="form.resolution">
            <option value="1080p">1080p (1920x1080)</option>
            <option value="2k">2K (2560x1440)</option>
            <option value="4k">4K (3840x2160)</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>{{ t('techDetails') }}</label>
        <textarea v-model="form.tech_details" rows="3" :placeholder="t('techDetailsPlaceholder')"></textarea>
      </div>

      <hr class="divider"/>

      <div class="model-config-section">
        <div class="form-group">
          <label>{{ t('baseUrl') }} <span class="required">*</span></label>
          <input v-model="form.base_url" type="text" placeholder="https://api.example.com/v1" />
        </div>
        <div class="form-group">
          <label>{{ t('apiKey') }}</label>
          <input v-model="form.api_key" type="password" placeholder="sk-..." />
        </div>
        <p class="config-hint">{{ t('configHint') }}</p>

        <div class="form-group">
          <label>{{ t('apiType') }} <span class="required">*</span></label>
          <select v-model="apiType">
            <option value="openai-completions">openai-completions</option>
            <option value="openai-responses">openai-responses</option>
            <option value="anthropic-messages">anthropic-messages</option>
            <option value="google-generative-ai">google-generative-ai</option>
            <option value="github-copilot">github-copilot</option>
            <option value="bedrock-converse-stream">bedrock-converse-stream</option>
          </select>
        </div>

        <div class="form-group config-actions">
          <label>{{ t('actions') }}</label>
          <div class="action-buttons">
            <button class="btn-fetch" @click="handleFetchModels" :disabled="fetchingModels">
              <span v-if="!fetchingModels">{{ t('fetchModels') }}</span>
              <span v-else class="mini-loader"></span>
            </button>
            <button class="btn-test" @click="handleTestConnection" :disabled="testingConnection">
              <span v-if="!testingConnection">{{ t('testConnection') }}</span>
              <span v-else class="mini-loader"></span>
            </button>
          </div>
        </div>

        <div class="checkbox-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="compatibleNewApi" />
            <span>{{ t('compatibleNewApi') }}</span>
          </label>
        </div>

        <div v-if="connectionStatus" class="connection-status" :class="connectionStatus.success ? 'status-success' : 'status-error'">
          {{ connectionStatus.message }}
        </div>

        <div class="model-list-section">
          <div class="model-list-header">
            <label class="section-title">{{ t('modelList') }}</label>
            <button class="btn-add-model" @click="modelInputVisible = !modelInputVisible">{{ t('addModel') }}</button>
          </div>

          <div v-if="modelInputVisible" class="model-input-row">
            <input v-model="newModelName" type="text" :placeholder="t('modelNamePlaceholder')" @keyup.enter="addModelManually" />
            <button class="btn-confirm" @click="addModelManually">{{ t('confirm') }}</button>
          </div>

          <div v-if="modelList.length === 0" class="model-list-empty">
            {{ t('noModelsHint') }}
          </div>
          <div v-else class="model-tags">
            <span v-for="(m, idx) in modelList" :key="m" class="model-tag" :class="{ active: form.model === m }" @click="form.model = m">
              {{ m }}
              <button class="tag-remove" @click.stop="removeModel(idx)">×</button>
            </span>
          </div>
        </div>

        <div v-if="modelList.length > 0" class="form-group">
          <label>{{ t('selectModel') }}</label>
          <select v-model="form.model">
            <option v-for="m in modelList" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
        <div v-else class="form-group">
          <label>{{ t('modelName') }}</label>
          <input v-model="form.model" type="text" :placeholder="t('modelPlaceholder')" />
        </div>
      </div>

      <button class="generate-btn" @click="handleGenerate" :disabled="loading">
        <span class="btn-text" v-if="!loading">{{ t('generateAnimation') }}</span>
        <span class="loader" v-else></span>
      </button>

      <div class="error-msg" v-if="error">{{ error }}</div>
    </aside>

    <main class="preview-area">
      <div class="preview-header">
        <h2>{{ t('livePreview') }}</h2>
        <div class="actions">
          <div v-if="loading" class="progress-info">
            <span>{{ t('generating') }}{{ progressCount }}{{ t('characters') }}</span>
            <button class="text-link-btn" @click="showRawStream = !showRawStream">
              {{ showRawStream ? t('hideLog') : t('viewDetails') }}
            </button>
            <button class="btn-abort" @click="handleAbort">
              {{ t('abortGenerate') }}
            </button>
          </div>
          <button class="action-btn" @click="downloadHtml" v-if="generatedHtml && !loading">
            {{ t('exportHtml') }}
          </button>
        </div>
      </div>
      
      <div class="iframe-container" :class="{'loading': loading}" ref="iframeContainer">
        <div class="placeholder" v-if="!generatedHtml && !loading && !aborted">
          <div class="placeholder-icon">🎥</div>
          <p>{{ t('placeholderText') }}</p>
        </div>
        <div class="aborted-state" v-if="aborted && !generatedHtml && !loading">
          <div class="placeholder-icon">⏹</div>
          <p>{{ t('abortedText') }}</p>
          <p class="aborted-hint">{{ t('abortedHint') }}</p>
        </div>
        <div class="generating-state" v-if="loading">
          <div class="spinner"></div>
          <p>{{ t('aiGenerating') }}</p>
        </div>
        <iframe 
          v-if="generatedHtml" 
          ref="previewFrame" 
          class="animation-frame" 
          sandbox="allow-scripts allow-same-origin"
          :style="{
            width: nativeRes.width + 'px',
            height: nativeRes.height + 'px',
            transform: 'scale(' + previewScale + ')',
            transformOrigin: 'top left'
          }"
        ></iframe>
        
        <div v-if="showRawStream" class="raw-stream-overlay">
          <div class="raw-stream-header">
            <h3>{{ t('streamTitle') }}</h3>
            <button @click="showRawStream = false">{{ t('close') }}</button>
          </div>
          <pre class="raw-stream-content">{{ rawStreamContent }}</pre>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Language Toggle Button */
.lang-toggle {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--border-color);
  padding: 5px 12px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  transition: all 0.3s ease;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  white-space: nowrap;
}

.lang-toggle:hover {
  border-color: var(--accent-color);
  background: rgba(255, 255, 255, 1);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
  transform: translateY(-1px);
}

.lang-label {
  color: var(--text-secondary);
  transition: all 0.25s ease;
}

.lang-label.active {
  background: linear-gradient(to right, #2563eb, #7c3aed);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
}

.lang-divider {
  color: #cbd5e1;
  font-weight: 400;
  margin: 0 1px;
}

.progress-info {
  font-size: 0.85rem;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.text-link-btn {
  background: none;
  border: none;
  color: #4f6df5;
  cursor: pointer;
  font-size: 0.85rem;
  padding: 0;
  text-decoration: underline;
}

.raw-stream-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.95);
  color: #e2e8f0;
  z-index: 100;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  font-family: 'JetBrains Mono', monospace;
}

.raw-stream-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #334155;
}

.raw-stream-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #94a3b8;
}

.raw-stream-header button {
  background: #334155;
  border: none;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
}

.raw-stream-content {
  flex: 1;
  overflow-y: auto;
  margin: 0;
  font-size: 0.85rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
