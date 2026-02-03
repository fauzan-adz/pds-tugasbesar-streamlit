from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import pandas as pd

browser = webdriver.Chrome()
url_target = "https://www.traveloka.com/id-id/hotel/detail?spec=21-01-2026.22-01-2026.1.1.HOTEL.1000000570828.Four%20Points%20by%20Sheraton%20Bandung.2&loginPromo=1&prevSearchId=1854918976111406135"

browser.get(url_target)
sleep(20) # Menunggu loading awal halaman

try:
    # Scroll ke area review agar script JS Traveloka memicu render data
    view_review = WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[@data-testid='review-list-container']"))
    )
    browser.execute_script("arguments[0].scrollIntoView();", view_review)
    sleep(10) 
except Exception as err:
    print(f"Error navigasi atau elemen tidak muncul: {err}")

# Ambil list item review
review_items = browser.find_elements(By.XPATH, "//div[@data-testid='review-list-container']/div/div")

hasil_scraping = []
index = 1

for item in review_items:
    try:
        # Ekstrak Skor
        rating = item.find_elements(By.XPATH, ".//div[@data-testid='tvat-ratingScore']")
        val_score = rating[0].text.strip() if rating else "0"

        # Ekstrak Waktu Posting
        post_date = item.find_elements(By.XPATH, ".//div[contains(text(), 'Diulas')]")
        val_date = post_date[0].text.replace("Diulas ", "").strip() if post_date else "-"

        # Ekstrak Teks Komentar
        # Logika: Cari elemen div yang isinya cukup panjang (asumsi itu teks ulasan)
        text_elements = item.find_elements(By.XPATH, ".//div[@dir='auto']")
        val_review = ""
        for div in text_elements:
            txt = div.text.strip()
            if len(txt) > 35 and "Diulas" not in txt:
                val_review = txt
                break

        if val_review:
            hasil_scraping.append({
                "No": index,
                "Rating": val_score,
                "Tanggal": val_date,
                "Isi Ulasan": val_review
            })
            index += 1

    except:
        continue

browser.quit()

# Export data ke file excel
dataset = pd.DataFrame(hasil_scraping)
dataset.to_excel("hasil_data_traveloka.xlsx", index=False)

print(f"Data Berhasil Disimpan. Total: {len(dataset)} baris.")