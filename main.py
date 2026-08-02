import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ==========================================
# 1. MASUKKAN BLOG ID KAMU DI SINI
# ==========================================
BLOG_ID = "9018939718289832902"  # <--- Ganti angka ini dengan Blog ID milikmu


def post_ke_blogger(judul, isi_html):
    # Ambil kredensial dari token JSON yang sudah dipasang
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
        "labels": ["Resep", "Kuliner"],  # Kategori / Label di Blogspot
    }

    # Kirim postingan ke blog
    posts = service.posts()
    hasil = posts.insert(blogId=BLOG_ID, body=body).execute()

    print(f"✅ Artikel Berhasil Terbit! URL: {hasil['url']}")


if __name__ == "__main__":
    # Tes posting artikel sederhana
    judul_tes = "Resep Aam Gurih Lezat - Tes Bot Automatic"
    isi_tes = "<p>Ini adalah postingan percobaaan otomatis dari Bot Gemini Python!</p>"

    post_ke_blogger(judul_tes, isi_tes)