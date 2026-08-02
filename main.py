import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google import genai
from google.genai import types

# ==========================================
# 1. KONFIGURASI BLOGGER
# ==========================================
BLOG_ID = "9018939718289832902"  # <--- Pastikan ID Blog kamu sudah benar

# ==========================================
# 2. GENERATE KONTEN PAKAI GEMINI (PROMPT SUPER)
# ==========================================
def buat_artikel_resep_gemini():
    print("🤖 Gemini sedang meracik artikel resep kreatif...")
    
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    prompt = """
Bertindaklah sebagai Chef Rumahan dan Food Blogger kreatif yang ramah, berpengalaman, dan pandai membagikan resep masakan serta minuman harian yang lezat dan praktis.
 
TOLONG BUATKAN 1 ARTIKEL RESEP LENGKAP:
- Jenis Resep: Pilihlah secara RANDOM 1 ide resep makanan atau minuman harian populer (bisa masakan rumahan, camilan, minuman segar, atau kreasi kekinian).
- Target Pembaca: Ibu rumah tangga, anak kos, atau siapa saja yang suka masak praktis di rumah.
 
ATURAN GAYA PENULISAN & TONE:
1. Panggilan Diri: Gunakan "Aku" atau "Gua" secara konsisten.
2. Panggilan Pembaca: Gunakan "Kamu" atau "Bestie" agar terasa akrab dan hangat.
3. Gaya Bahasa: Santai, mengalir, ramah, seolah-olah sedang mengajari teman dekat di dapur.
4. JANGAN gunakan kata-kata kaku khas AI seperti: "Di era modern ini", "Sangat krusial", "Kesimpulannya", "Mari kita bahas", atau "Mahakarya kuliner".
 
ATURAN JUDUL & SEO (RAMAH GOOGLE ADSENSE):
1. Judul Artikel: Singkat, padat, menarik, dan TO THE POINT (Maksimal 6-8 kata, contoh: "Resep Es Kopi Susu Gula Aren Praktis" atau "Cara Bikin Tumis Kangkung Terasi Enak"). Jangan buat judul yang bertele-tele.
2. Meta Description: Buat ringkasan menarik (120-150 karakter) memuat nama resep.
3. Nilai Tambah AdSense (High-Value Content):
   - Jangan cuma kasih daftar bahan dan langkah! Tambahkan "Tips Rahasia / Anti-Gagal" di bagian akhir agar konten benar-benar bermanfaat unik bagi pembaca.
   - Cantumkan estimasi waktu masak, tingkat kesulitan, dan perkiraan porsi.
 
ATURAN STRUKTUR & FORMAT HTML (UNTUK BLOGSPOT):
1. Gunakan tag HTML bersih yang siap diunggah ke Blogspot:
   - <h2> untuk judul bagian utama (Deskripsi Singkat, Bahan-bahan, Cara Membuat, Tips Anti Gagal).
   - <p> untuk paragraf pembuka dan cerita singkat di balik resep.
   - <ul> dan <li> untuk daftar bahan-bahan.
   - <ol> dan <li> untuk langkah-langkah memasak secara urut dan jelas.
   - <blockquote> untuk poin penting atau tips rahasia.
 
FORMAT OUTPUT YANG DIHARAPKAN (JSON):
{
 "recipe_name": "Nama Resep Singkat",
 "title": "Judul Artikel Singkat & To The Point",
 "meta_description": "Deskripsi singkat resep untuk SEO",
 "content_html": "<p>Isi artikel lengkap format HTML...</p>"
}
"""
    
    # Pakai model gemini-2.0-flash dan kunci respon ke format JSON
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    
    # Parse hasil JSON dari Gemini
    data = json.loads(response.text)
    return data

# ==========================================
# 3. POSTING KE BLOGGER VIA API
# ==========================================
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
        "labels": ["Resep Masakan", "Kuliner Nusantara", "Ide Jualan", "Resep Praktis"],
    }

    posts = service.posts()
    hasil = posts.insert(blogId=BLOG_ID, body=body).execute()

    print(f"🎉 BERHASIL! Artikel terbit di: {hasil['url']}")

# ==========================================
# 4. JALANKAN PROGRAM UTAMA
# ==========================================
if __name__ == "__main__":
    resep_data = buat_artikel_resep_gemini()
    
    judul_artikel = resep_data["title"]
    konten_html = resep_data["content_html"]
    
    print(f"📌 Judul buatan Gemini: {judul_artikel}")
    
    post_ke_blogger(judul_artikel, konten_html)