import axios from "axios";

const authApiClient = axios.create({
  baseURL: import.meta.env.VITE_AUTH_API,
});

authApiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("bns_id_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default authApiClient;
