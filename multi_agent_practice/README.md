# Praktik Awal Multi-Agent Code Review

Proyek latihan ini memperagakan alur awal penelitian:

1. Dua agen (simulasi) memeriksa kode dan requirement.
2. Fix-Guided Verification Filter menjalankan test pada kode asli dan kode perbaikan.
3. Hasil akhirnya ditampilkan sebagai keputusan review.

## Tahap 1: Jalankan tanpa API (gratis)

Pastikan Python 3.10+ terpasang. Buka terminal di folder proyek ini.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python main.py
```

Jika perintah `py` tidak tersedia, coba `python`.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python main.py
```

Tahap ini tidak membutuhkan API key dan tidak mengirim kode ke layanan luar.

## Tahap 2: Integrasi API (belum diaktifkan dalam demo ini)

File `.env.example` hanya contoh nama variabel. Salin menjadi `.env` saat masuk tahap integrasi, lalu isi key secara lokal. Jangan pernah mengirimkan key ke chat atau commit ke GitHub.

Model ID dapat berubah. Sebelum eksperimen formal, verifikasi model yang benar-benar tersedia di akun dan dokumentasi resmi masing-masing penyedia.

- OpenAI: https://platform.openai.com/docs/models
- Gemini: https://ai.google.dev/gemini-api/docs/models
- Groq: https://console.groq.com/docs/models

Catatan penelitian: Groq adalah penyedia inferensi/API; `openai/gpt-oss-120b` adalah model yang di-host melalui Groq, bukan model buatan Groq.

## Batasan keselamatan

Kode demo hanya menjalankan dua fungsi Python yang ditulis dan dikendalikan di dalam proyek latihan ini. Jangan menjalankan kode dari Pull Request atau kode hasil generasi LLM dengan `exec()` atau subprocess biasa pada mesin utama. Untuk penelitian sungguhan, eksekusi harus dilakukan di sandbox/container yang dibatasi (misalnya tanpa jaringan, hak akses minimum, batas CPU/memori, dan timeout).

## Batasan metodologis

Lulus pada seluruh test case bukan bukti bahwa dua implementasi ekuivalen untuk semua input. Dataset, oracle/expected output, dan test suite perlu dirancang dan divalidasi untuk eksperimen.
