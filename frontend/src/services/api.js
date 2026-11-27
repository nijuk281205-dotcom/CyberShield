import axios from "axios";

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api",
  timeout: 15000,
});

export function errorMessage(err) {
  if (err.response?.data?.error) return err.response.data.error;
  if (err.response?.status === 429) return "Too many requests. Please wait a moment.";
  if (err.code === "ECONNABORTED") return "The server took too long to respond.";
  if (!err.response) return "Can't reach the server. Check that the backend is running.";
  return "Something went wrong. Please try again.";
}

export const scan = (type, input) => client.post("/scan", { type, input }).then((r) => r.data);
export const getStats = () => client.get("/stats").then((r) => r.data);
export const getHistory = (params) => client.get("/history", { params }).then((r) => r.data);
export const deleteScan = (id) => client.delete(`/history/${id}`).then((r) => r.data);
export const clearHistory = () => client.delete("/history").then((r) => r.data);
