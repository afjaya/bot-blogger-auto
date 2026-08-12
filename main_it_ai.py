import json
import os
import random
import re
import time
from google import genai
from google.genai import types
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ==========================================
# 1. KONFIGURASI BLOGGER (Blog IT/AI)
# ==========================================
BLOG_ID = "5691370053604799116"


# ==========================================
# HELPER: CLEAN & PARSE JSON FROM GEMINI TEXT
# ==========================================
def clean_and_parse_json(raw_text: str) -> dict:
    """Membersihkan wrapper Markdown dan karakter kontrol tak terlihat yang merusak JSON"""
    cleaned = re.sub(r"```json\s*|\s*```", "", raw_text).strip()
    cleaned = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", cleaned)
    return json.loads(cleaned, strict=False)


# ==========================================
# 2. GENERATE KONTEN PAKAI GEMINI
# ==========================================
def buat_artikel_it_ai_gemini():
    print("🤖 Gemini sedang meracik artikel IT/AI kreatif...")

    keys_raw = os.environ.get("GEMINI_API_KEYS", "")
    if not keys_raw:
        keys_raw = os.environ.get("GEMINI_API_KEY", "")

    api_keys = [k.strip() for k in keys_raw.split(",") if k.strip()]

    if not api_keys:
        raise Exception("❌ API Key Gemini tidak ditemukan di Secrets!")

    random.shuffle(api_keys)

    prompt = """
Bertindaklah sebagai IT Specialist, Prompt Engineer, dan Tech Blogger berpengalaman yang ramah, komunikatif, dan pandai menjelaskan hal teknis secara mudah dipahami.
 
TOLONG BUATKAN 1 ARTIKEL TUTORIAL / TIPS IT ATAU AI LENGKAP:
- Topik Artikel: Pilihlah secara RANDOM 1 topik tren terkini seputar dunia IT, Tips Windows/Linux/Mac, Trik AI (Gemini, ChatGPT, Midjourney, dll), Tools Otomatisasi, Cybersecurity Dasar, atau Produktivitas Digital.
- Target Pembaca: Pelajar, mahasiswa, pekerja kantoran, pemula tech, atau pegiat digital.
 
ATURAN GAYA PENULISAN & TONE:
1. Panggilan Diri: Gunakan "Saya" atau "Gua" secara konsisten.
2. Panggilan Pembaca: Gunakan "Lu" atau "Sob" / "Bro" agar terasa akrab.
3. Gaya Bahasa: Edukatif, santai, solutif, mudah diikuti step-by-step.
4. JANGAN gunakan kata-kata kaku khas AI seperti: "Di era digital yang berkembang pesat ini", "Sangat krusial", "Kesimpulannya".
 
ATURAN JUDUL & SEO:
1. Judul Artikel: Clickable, to the point, memuat kata kunci utama (Maksimal 7-10 kata, contoh: "Cara Pakai AI Gemini untuk Bikin Presentasi Otomatis" atau "5 Trik Mempercepat Laptop Lemot Tanpa Aplikasi").
2. Meta Description: Ringkasan menarik (120-150 karakter) memuat manfaat baca artikelnya.
3. Nilai Tambah AdSense: Cantumkan studi kasus singkat, langkah jelas, dan "Tips Tambahan / Solusi Trouble".
 
ATURAN STRUKTUR & FORMAT HTML:
Gunakan tag <h2>, <h3>, <p>, <ul>, <ol>, <li>, <code> untuk sintaks/perintah (jika ada), dan <blockquote> untuk catatan penting.
 
FORMAT OUTPUT (JSON HANYA TANPA PEMBUNGKUS LAIN):
{
 "title": "Judul Artikel Menarik & To The Point",
 "meta_description": "Deskripsi singkat artikel untuk SEO",
 "content_html": "<p>Isi artikel lengkap format HTML...</p>"
}
"""

    candidate_models = [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-flash-latest",
    ]

    for index, key in enumerate(api_keys, 1):
        for model_name in candidate_models:
            try:
                print(
                    f"🔑 Mencoba API Key ke-{index} dengan model [{model_name}]..."
                )
                client = genai.Client(api_key=key)

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    ),
                )

                data = clean_and_parse_json(response.text)
                print(
                    f"✅ Artikel IT/AI berhasil dibuat dengan model [{model_name}]!"
                )
                return data

            except Exception as e:
                err_msg = str(e)
                print(
                    f"⚠️ Kunci ke-{index} dengan model ({model_name}) gagal: {err_msg}"
                )

                # Jika terkena Rate Limit / Quota Exhausted, beri jeda sebelum coba lagi
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    print("⏳ Terkena Rate Limit, menunggu 15 detik...")
                    time.sleep(15)

    raise Exception("❌ Semua API Key & Model Gemini gagal dipanggil!")


# ==========================================
# 3. POSTING KE BLOGGER VIA API
# ==========================================
def post_ke_blogger(judul, isi_html):
    print("🚀 Mengirim artikel ke Blogspot IT/AI...")

    token_raw = os.environ.get("BLOGGER_TOKEN")
    if not token_raw:
        raise Exception("❌ Secret BLOGGER_TOKEN tidak ditemukan!")

    token_info = json.loads(token_raw)

    creds = Credentials(
        token=token_info["token"],
        refresh_token=token_info["refresh_token"],
        token_uri=token_info["token_uri"],
        client_id=token_info["client_id"],
        client_secret=token_info["client_secret"],
        scopes=token_info["scopes"],
    )

    service = build("blogger", "v3", credentials=creds)

    body = {
        "kind": "blogger#post",
        "title": judul,
        "content": isi_html,
        "labels": ["Tips IT", "Kecerdasan Buatan", "Tutorial AI", "Teknologi"],
    }

    posts = service.posts()
    hasil = posts.insert(blogId=BLOG_ID, body=body).execute()

    print(f"🎉 BERHASIL! Artikel terbit di: {hasil['url']}")


if __name__ == "__main__":
    data_artikel = buat_artikel_it_ai_gemini()

    judul_artikel = data_artikel["title"]
    konten_html = data_artikel["content_html"]

    print(f"📌 Judul: {judul_artikel}")
    post_ke_blogger(judul_artikel, konten_html)
