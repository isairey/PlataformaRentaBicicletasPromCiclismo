import axios from "axios";

const mapApiClient = axios.create({
  baseURL: import.meta.env.VITE_MAP_API,
});

mapApiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("bns_id_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

mapApiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("bns_id_token");
      localStorage.removeItem("bns_refresh_token");
      window.location.replace("/login");
    }
    return Promise.reject(error);
  },
);

export default mapApiClient;
