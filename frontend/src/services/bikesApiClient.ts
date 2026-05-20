import axios from "axios";

const bikesApiClient = axios.create({
  baseURL: import.meta.env.VITE_BIKE_API,
});

bikesApiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("bns_id_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

bikesApiClient.interceptors.response.use(
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

export default bikesApiClient;
