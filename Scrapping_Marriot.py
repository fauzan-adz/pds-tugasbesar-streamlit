from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import pandas as pd

# Setup Browser
tampilan_web = webdriver.Chrome()
url_sheraton = "https://www.marriott.com/id/hotels/bdosi-sheraton-bandung-hotel-and-towers/reviews/"

tampilan_web.get(url_sheraton)

# Tunggu proses loading page
sleep(25)

# Trigger lazy loading dengan scroll manual melalui script
tampilan_web.execute_script("window.scrollTo(0, 1200);")
sleep(20)

list_ulasan = []
nomor_urut = 1

# Identifikasi container review berdasarkan class 'user-review'
elemen_review = tampilan_web.find_elements(By.CLASS_NAME, "user-review")

for box in elemen_review:
    try:
        # Ekstraksi Skor Rating
        skor_item = box.find_elements(By.CLASS_NAME, "numReviews_number")
        nilai_rating = skor_item[0].text.strip() if skor_item else "-"

        # Ekstraksi Waktu (Cari teks relatif: ago/bulan/tahun)
        waktu_posting = box.find_elements(By.XPATH, ".//div[contains(@class, 't-msg-color') and (contains(text(), 'ago') or contains(text(), 'tahun') or contains(text(), 'bulan'))]")
        txt_waktu = waktu_posting[0].text.strip() if waktu_posting else "Tidak tertera"

        # Ekstraksi Konten Ulasan
        # Mencari tag <p> di dalam kontainer pesan
        teks_box = box.find_elements(By.XPATH, ".//div[contains(@class, 't-msg-color')]//p")
        if not teks_box:
             teks_box = box.find_elements(By.XPATH, ".//div[contains(@class, 't-subtitle-m')]/following-sibling::div")
        
        konten_review = teks_box[0].text.strip() if teks_box else ""

        # Validasi: Masukkan ke list jika ulasan tidak kosong
        if len(konten_review) > 10:
            list_ulasan.append({
                "No": nomor_urut,
                "Skor": nilai_rating,
                "Waktu": txt_waktu,
                "Review": konten_review
            })
            nomor_urut += 1

    except Exception as e:
        print(f"Melewati satu data karena error: {e}")
        continue

tampilan_web.quit()

# Export hasil ke format Excel
df_hasil = pd.DataFrame(list_ulasan)
df_hasil.to_excel("data_review_sheraton_marriott.xlsx", index=False)

print(f"Proses selesai. Mendapatkan {len(df_hasil)} data.")