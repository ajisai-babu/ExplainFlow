import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  timeout: 300000, // 300s timeout for LLM generation
});

export const generateAnimation = async (data) => {
  try {
    const response = await api.post('/generate', data);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || '动画生成失败。');
    }
    throw new Error('网络错误或超时。请检查后端服务是否已启动。');
  }
};
