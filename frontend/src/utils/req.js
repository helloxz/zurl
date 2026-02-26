import axios from 'axios';

// 支持非根目录部署：优先使用服务端注入的 __BASE_PATH__，否则使用构建时 VITE_BASE_URL
function getBaseURL() {
  if (typeof window !== 'undefined' && window.__BASE_PATH__ !== undefined && window.__BASE_PATH__ !== '') {
    return String(window.__BASE_PATH__).replace(/\/$/, '');
  }
  const env = import.meta.env.VITE_BASE_URL || import.meta.env.VITE_API_URL || '';
  return String(env).replace(/\/$/, '') || '';
}

const req = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
});


// 请求拦截器
req.interceptors.request.use(
  (config) => {
    // 从 localStorage 或 sessionStorage 中获取 token
    const token = localStorage.getItem('token');

    // 如果 token 存在，则将其添加到请求头中
    if (token) {
      config.headers['Authorization'] = "Bearer " + token; // 设置 X-Token 头
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export function toForm(data) {
  const formData = new FormData();
  for (const key in data) {
      if (data.hasOwnProperty(key)) {
          formData.append(key, data[key]);
      }
  }
  return formData;
}

export default req;