import streamlit as st
import pandas as pd
import folium
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from streamlit_folium import st_folium
from geopy.distance import geodesic

st.set_page_config(page_title="GIS Sheraton Bandung", layout="wide")

st.sidebar.header("Menu Utama")
menu = st.sidebar.radio(
    "Pilih Tampilan:",
    ["Analisis Rating & Ulasan", "Peta GIS & Lokasi Strategis"]
)

@st.cache_data
def load_wisata():
    df_wisata = pd.read_excel("Data/Lokasi_Sekitar_Sheraton.xlsx")
    df_wisata.columns = df_wisata.columns.str.strip()
    df_wisata["Kategori"] = df_wisata["Kategori"].astype(str).str.strip()
    return df_wisata

@st.cache_data
def load_reviews():
    df = pd.read_excel("Data/Review_Sheraton_Traveloka_Marriot.xlsx")
    df = df.dropna(subset=["Ulasan", "Waktu", "Skor"])
    return df

df_wisata = load_wisata()
df = load_reviews()
hotel_coords = [-6.87466, 107.62021]
hotel_name = "Sheraton Bandung Hotel"

def konversi_waktu(teks):
    now = datetime.now()
    teks = str(teks).lower()
    try:
        angka = int(teks.split()[1])
        if "tahun" in teks: return now - timedelta(days=365 * angka)
        if "bulan" in teks: return now - timedelta(days=30 * angka)
        if "minggu" in teks: return now - timedelta(weeks=angka)
    except:
        pass
    return now

df["Tanggal"] = df["Waktu"].apply(konversi_waktu)
df["Tahun"] = df["Tanggal"].dt.year

kata_negatif = ["apek", "bad", "bau", "berantakan", "berdebu", "berisik", "bocor", "buruk", 
                "crowded", "cuek", "dingin", "hambar", "jelek", "kasar", "kecewa", "kecil", 
                "kotor", "kuno", "kurang", "kusam", "lama", "lambat", "lelet", "lembab", 
                "macet", "mahal", "mengecewakan", "nyesel", "overpriced", "pahit", "payah", 
                "pending", "rusak", "sempit", "susah", "tua"]
kata_positif = ["adem", "aesthetic", "asri", "bagus", "baik", "bersih", "cepat", "enak", 
                "excellent", "hebat", "helpful", "homey", "indah", "keren", "lengkap", 
                "lezat", "luas", "mantap", "nyaman", "pemandangan", "puas", "ramah", 
                "recommended", "segala", "sejuk", "sopan", "strategis", "top", "variatif", 
                "view", "worth it"]

def analisis_ulasan_hybrid(row):
    teks = str(row["Ulasan"]).lower()
    skor = row["Skor"]
    for k in kata_negatif:
        if k in teks: return "Negatif"
    for k in kata_positif:
        if k in teks: return "Positif"
    return "Positif" if skor >= 4 else "Negatif" if skor <= 2 else "Netral"

df["ulasan"] = df.apply(analisis_ulasan_hybrid, axis=1)

if menu == "Analisis Rating & Ulasan":
    st.title("Analisis Kualitas Pelayanan")
    
    col_metric1, col_metric2 = st.columns(2)
    col_metric1.metric("Rata-rata Rating", f"{df['Skor'].mean():.2f} / 10.0")
    col_metric2.metric("Total Ulasan", len(df))

    col_grafik, col_pie = st.columns(2)
    bg_color = "#0e1117"
    text_color = "white"

    with col_grafik:
        rata = df.groupby("Tahun")["Skor"].mean().reset_index()
        # Perkecil figsize ke (3, 2) atau (3.5, 2.5)
        fig, ax = plt.subplots(figsize=(3, 2), dpi=100, constrained_layout=True)
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        ax.plot(rata["Tahun"], rata["Skor"], marker="o", color="#00f2ff", markersize=4)
        
        # Perkecil ukuran font agar tetap terbaca di grafik kecil
        ax.set_title("Tren Rating Tahunan", color=text_color, fontsize=8)
        ax.tick_params(colors=text_color, labelsize=7)
        
        # Gunakan use_container_width=False agar mengikuti ukuran figsize asli
        st.pyplot(fig, width="content")

    with col_pie:
        hasil = df["ulasan"].value_counts()
        # Samakan figsize dengan grafik di sebelah (3, 2)
        fig2, ax2 = plt.subplots(figsize=(3, 2), dpi=100, constrained_layout=True)
        fig2.patch.set_facecolor(bg_color)
        
        warna_map = {'Positif': '#00ff88', 'Negatif': '#ff4b4b', 'Netral': '#ffcc00'}
        colors = [warna_map.get(x, '#3498db') for x in hasil.index]
        
        # Perkecil ukuran font label (textprops)
        ax2.pie(hasil.values, labels=hasil.index, autopct="%1.1f%%", 
                colors=colors, textprops={'color': text_color, 'fontsize': 7})
        ax2.set_title("Proporsi ulasan", color=text_color, fontsize=8)
        
        st.pyplot(fig2, width="content")

    st.subheader("Sampel 20 Ulasan Terbaru")
    st.dataframe(df[["Waktu", "Skor","ulasan", "Ulasan"]].head(20), hide_index=True, width="stretch")

else:
    st.title("Peta GIS & Aksesibilitas")
    
    radius = st.sidebar.slider("Radius (KM)", 0.5, 5.0, 2.0)
    kategori_list = [k for k in df_wisata["Kategori"].unique() if k != "Hotel"]
    kategori_pilih = st.sidebar.multiselect("Kategori Wisata", kategori_list, default=kategori_list)

    m = folium.Map(location=hotel_coords, zoom_start=14)
    html_hotel = f"""<div style="font-family:sans-serif;font-size:12px;"><b>{hotel_name}</b><br>Lokasi Utama<br><a href="https://www.google.com/maps?q={hotel_coords[0]},{hotel_coords[1]}" target="_blank">Buka Maps</a></div>"""
    folium.Marker(
        location=hotel_coords, 
        popup=folium.Popup(html_hotel, max_width=150), 
        icon=folium.Icon(color="red", icon="star", prefix="fa")
    ).add_to(m)
    
    folium.Circle(location=hotel_coords, radius=radius * 1000, color="red", fill=True, fill_opacity=0.1).add_to(m)

    filtered_wisata = []
    for _, row in df_wisata.iterrows():
        if row["Nama"] == hotel_name or row["Kategori"] == "Hotel": continue
        coords = [row["Latitude"], row["Longitude"]]
        dist = geodesic(hotel_coords, coords).km
        
        if row["Kategori"] in kategori_pilih and dist <= radius:
            filtered_wisata.append({"Nama": row["Nama"], "Kategori": row["Kategori"], "Jarak (KM)": round(dist, 2)})
            warna = "orange" if row["Kategori"] == "Kuliner" else "blue" if row["Kategori"] in ["Budaya", "Seni"] else "green"
            icon = "coffee" if row["Kategori"] == "Kuliner" else "landmark" if row["Kategori"] in ["Budaya", "Seni"] else "leaf"
            
            html = f"""<div style="font-family:sans-serif;font-size:12px;"><b>{row['Nama']}</b><br>{dist:.2f} km<br><a href="https://www.google.com/maps/search/?api=1&query={row['Latitude']},{row['Longitude']}" target="_blank">Buka Maps</a></div>"""
            folium.Marker(location=coords, popup=folium.Popup(html, max_width=150), icon=folium.Icon(color=warna, icon=icon, prefix='fa')).add_to(m)

    col_map, col_table = st.columns([2, 1])
    with col_map:
        st_folium(m, width=800, height=500)
    with col_table:
        st.metric("Daftar Wisata dalam Radius", len(filtered_wisata))
        st.dataframe(pd.DataFrame(filtered_wisata), hide_index=True, width="stretch")

    st.markdown("---")
    st.subheader("Ulasan Terkait yang Menunjukkan Lokasi Hotel Strategis")
    keywords = ["strategis", "dekat", "lokasi", "akses", "dago", "kuliner", "jalan kaki"]
    df_strat = df[df["Ulasan"].str.lower().str.contains('|'.join(keywords))].head(15)
    st.dataframe(df_strat[["Skor", "Waktu", "Ulasan"]], hide_index=True, width="stretch")