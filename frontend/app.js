document.getElementById('uploadBtn')?.addEventListener('click', async () => {
  const input = document.getElementById('fileInput');
  if (!input.files.length) return alert('select a file');
  const file = input.files[0];
  const fd = new FormData();
  fd.append('file', file);

  const res = await fetch('/api/upload', { method: 'POST', body: fd });
  const j = await res.json();
  if (res.ok) {
    document.getElementById('text').value = j.text || '';
  } else {
    alert(j.error || 'upload failed');
  }
});

document.querySelectorAll('#summary button').forEach(btn => {
  btn.addEventListener('click', async () => {
    const level = btn.dataset.level;
    const text = document.getElementById('text').value;
    if (!text) return alert('no text to summarize');
  const res = await fetch('/api/summarize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, level })
    });
    const j = await res.json();
    if (res.ok) {
      document.getElementById('summaryOut').innerText = j.summary || '';
    } else {
      alert(j.error || 'summarization failed');
    }
  });
});
