import axios from 'axios';

const api = axios.create({
  baseURL: 'https://breathe-esg-production-5bf3.up.railway.app/api',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Token ${token}`;
  return config;
});

export default api;