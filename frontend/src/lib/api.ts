export const API_BASE = (
  process.env.NEXT_PUBLIC_API_URL || 
  "https://nerdvana-sih-backend.onrender.com"
).replace(/\/+$/, "");

export function getApiUrl(path: string): string {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  
  // If cleanPath already starts with /api/, prepend API_BASE directly
  if (cleanPath.startsWith("/api/")) {
    return `${API_BASE}${cleanPath}`;
  }
  
  // If cleanPath starts with /static/, prepend API_BASE directly
  if (cleanPath.startsWith("/static/")) {
    return `${API_BASE}${cleanPath}`;
  }
  
  return `${API_BASE}/api${cleanPath}`;
}
