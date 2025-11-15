const BASE = import.meta.env.VITE_API_BASE_URL || "";

async function handle(res) {
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

export async function uploadFile(file) {
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(`${BASE}/api/upload`, { method: "POST", body: fd });
  return handle(res);
}

export async function summarizeText(text, level = "short") {
  const res = await fetch(`${BASE}/api/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, level }),
  });

  return handle(res);
}
