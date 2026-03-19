import { ref, computed } from 'vue'

const messages = {
  zh: {
    // Sidebar header
    animationTopic: '动画主题',
    topicPlaceholder: '例如：JavaScript 事件循环机制',
    bilingualSubtitle: '双语字幕',
    resolution: '分辨率',
    techDetails: '技术细节补充',
    techDetailsPlaceholder: '提供额外要求或细节...',

    // Model config
    baseUrl: 'Base URL',
    apiKey: 'API Key',
    configHint: '提示: 填写URL后会自动检测供应商类型',
    apiType: 'API 类型',
    actions: '操作',
    fetchModels: '⬇ 获取模型',
    testConnection: '💗 测试连接',
    compatibleNewApi: '兼容 New API',
    modelList: '模型列表',
    addModel: '＋ 添加模型',
    modelNamePlaceholder: '输入模型名称',
    confirm: '确认',
    noModelsHint: '暂无模型，点击上方"添加模型"或"获取模型"从API获取模型列表',
    selectModel: '选择模型',
    modelName: '模型名称',
    modelPlaceholder: '如 deepseek-chat 或 gpt-4o',

    // Generate
    generateAnimation: '生成动画',

    // Preview
    livePreview: '实时预览',
    generating: '正在生成: ',
    characters: ' 字符...',
    hideLog: '隐藏日志',
    viewDetails: '查看详情',
    abortGenerate: '■ 终止生成',
    exportHtml: '导出 HTML',
    placeholderText: '生成的动画将在此处显示',
    abortedText: '生成已终止',
    abortedHint: '点击「生成动画」重新开始',
    aiGenerating: 'AI 正在为您制作动画... 这可能需要一分钟左右的时间。',
    streamTitle: '流式输出详情',
    close: '关闭',

    // Errors
    errorTopicRequired: '请输入动画主题。',
    errorApiKeyRequired: '必须提供 API Key 才能调用大模型。',
    errorBaseUrlRequired: '请先填写 Base URL',
    errorApiKeyFirst: '请先填写 API Key',
    errorRequestFailed: '请求失败: ',
    errorGenericFail: '请求失败',
    errorAborted: '生成已终止。',
  },
  en: {
    // Sidebar header
    animationTopic: 'Animation Topic',
    topicPlaceholder: 'e.g. JavaScript Event Loop',
    bilingualSubtitle: 'Bilingual Subtitles',
    resolution: 'Resolution',
    techDetails: 'Technical Details',
    techDetailsPlaceholder: 'Provide additional requirements or details...',

    // Model config
    baseUrl: 'Base URL',
    apiKey: 'API Key',
    configHint: 'Hint: Provider type will be auto-detected after entering URL',
    apiType: 'API Type',
    actions: 'Actions',
    fetchModels: '⬇ Fetch Models',
    testConnection: '💗 Test Connection',
    compatibleNewApi: 'Compatible with New API',
    modelList: 'Model List',
    addModel: '＋ Add Model',
    modelNamePlaceholder: 'Enter model name',
    confirm: 'Confirm',
    noModelsHint: 'No models yet. Click "Add Model" or "Fetch Models" above to get the model list from API',
    selectModel: 'Select Model',
    modelName: 'Model Name',
    modelPlaceholder: 'e.g. deepseek-chat or gpt-4o',

    // Generate
    generateAnimation: 'Generate Animation',

    // Preview
    livePreview: 'Live Preview',
    generating: 'Generating: ',
    characters: ' chars...',
    hideLog: 'Hide Log',
    viewDetails: 'View Details',
    abortGenerate: '■ Abort',
    exportHtml: 'Export HTML',
    placeholderText: 'Generated animation will appear here',
    abortedText: 'Generation aborted',
    abortedHint: 'Click "Generate Animation" to restart',
    aiGenerating: 'AI is creating your animation... This may take about a minute.',
    streamTitle: 'Stream Output Details',
    close: 'Close',

    // Errors
    errorTopicRequired: 'Please enter an animation topic.',
    errorApiKeyRequired: 'API Key is required to call the model.',
    errorBaseUrlRequired: 'Please fill in the Base URL first',
    errorApiKeyFirst: 'Please fill in the API Key first',
    errorRequestFailed: 'Request failed: ',
    errorGenericFail: 'Request failed',
    errorAborted: 'Generation aborted.',
  }
}

// Reactive locale state
const locale = ref(localStorage.getItem('explainflow-locale') || 'en')

const t = (key) => {
  return messages[locale.value]?.[key] || messages['en'][key] || key
}

const toggleLocale = () => {
  locale.value = locale.value === 'en' ? 'zh' : 'en'
  localStorage.setItem('explainflow-locale', locale.value)
}

export function useI18n() {
  return {
    locale,
    t: computed(() => t),
    toggleLocale,
  }
}
