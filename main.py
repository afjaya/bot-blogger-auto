import os
import json
import random
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google import genai
from google.genai import types

BLOG_ID = "9018939718289832902"  # <--- Pastikan ID Blog kamu benar

def buat_artikel_resep_gemini():
    print("🤖 Gemini sedang meracik artikel resep kreatif...")
    
    keys_raw = os.environ.get("GEMINI_API_KEYS", "")
    if not keys_raw:
        keys_raw = os.environ.get("GEMINI_API_KEY", "")
        
    api_keys = [k.strip() for k in keys_raw.split(",") if k.strip()]
    
    if not api_keys:
        raise Exception("❌ API Key Gemini tidak ditemukan di Secrets!")

    random.shuffle(api_keys)
    
    prompt = """
Bertindaklah sebagai Chef Rumahan dan Food Blogger kreatif yang ramah, berpengalaman, dan pandai membagikan resep masakan serta minuman harian yang lezat dan praktis.
 
TOLONG BUATKAN 1 ARTIKEL RESEP LENGKAP:
- Jenis Resep: Pilihlah secara RANDOM 1 ide resep makanan atau minuman harian populer.
- Target Pembaca: Ibu rumah tangga, anak kos, atau siapa saja yang suka masak praktis di rumah.
 
ATURAN GAYA PENULISAN & TONE:
1. Panggilan Diri: Gunakan "Aku" atau "Gua" secara konsisten.
2. Panggilan Pembaca: Gunakan "Kamu" atau "Bestie" agar terasa akrab dan hangat.
3. Gaya Bahasa: Santai, mengalir, ramah.
4. JANGAN gunakan kata-kata kaku khas AI seperti: "Di era modern ini", "Sangat krusial", "Kesimpulannya".
 
ATURAN JUDUL & SEO:
1. Judul Artikel: Singkat, padat, menarik (Maksimal 6-8 kata).
2. Meta Description: Ringkasan menarik (120-150 karakter).
3. Poin Plus: Cantumkan estimasi waktu masak, porsi, dan "Tips Rahasia Anti-Gagal".
 
FORMAT HTML:
Gunakan tag <h2>, <p>, <ul>, <ol>, <li>, <blockquote>.
 
FORMAT OUTPUT (MUST BE VALID JSON):
{
 "recipe_name": "Nama Resep",
 "title": "Judul Artikel",
 "meta_description": "Deskripsi singkat",
 "content_html": "<p>Isi artikel format HTML...</p>"
}
"""

    # Daftar nama model yang akan dicoba secara berurutan
    candidate_models = ["gemini-2.5-flash", "gemini-1.5-flash"]

    for index, key in enumerate(api_keys, 1):
        for model_name in candidate_models:
            try:
                print(f"🔑 Mencoba API Key ke-{index} dengan model [{model_name}]...")
                client = genai.Client(api_key=key)
                
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                
                data = json.loads(response.text)
                print(f"✅ Berhasil generate konten menggunakan model {model_name}!")
                return data
                
            except Exception as e:
                print(f"⚠️ API Key ke-{index} ({model_name}) gagal: {e}")
                time.sleep(2) # Beri jeda 2 detik sebelum mencoba lagi

    raise Exception("❌ Semua API Key & Model Gemini gagal dipanggil!")

def post_ke_blogger(judul, isi_html):
    print("🚀 Mengirim artikel ke Blogspot...")
    
    token_info = json.loads(os.environ["BLOGGER_TOKEN"])

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
        "labels": ["Resep Masakan", "Kuliner Nusantara", "Resep Praktis"],
    }

    posts = service.posts()
    hasil = posts.insert(blogId=BLOG_ID, body=body).execute()

    print(f"🎉 BERHASIL! Artikel terbit di: {hasil['url']}")

if __name__ == "__main__":
    resep_data = buat_artikel_resep_gemini()
    
    judul_artikel = resep_data["title"]
    konten_html = resep_data["content_html"]
    
    print(f"📌 Judul buatan Gemini: {judul_artikel}")
    post_ke_blogger(judul_artikel, konten_html)