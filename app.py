import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="IndaQua Fizibilite Analizi",
    page_icon="💧",
    layout="wide"
)

# --- HESAPLAMA FONKSİYONU (Çekirdek Mantık) ---
def hesapla_fizibilite(sizinti_debisi, su_maliyeti, sensor_maliyeti, yillik_sizinti_sayisi, geleneksel_tespit_suresi):
    """Verilen parametrelere göre fizibilite analizi yapar ve sonuçları döndürür."""
    # Sabitler
    DAKIKA_SAAT = 60
    SAAT_GUN = 24
    LITRE_M3 = 1000
    KURULACAK_SENSOR_SAYISI = 200
    TESPIT_SURESI_IndaQua_GUN = 1

    # Geleneksel Yöntem Kaybı
    yillik_kayip_geleneksel_lt = (sizinti_debisi * DAKIKA_SAAT * SAAT_GUN * geleneksel_tespit_suresi) * yillik_sizinti_sayisi
    yillik_maliyet_geleneksel_tl = (yillik_kayip_geleneksel_lt / LITRE_M3) * su_maliyeti

    # IndaQua Yöntemi Kaybı
    yillik_kayip_IndaQua_lt = (sizinti_debisi * DAKIKA_SAAT * SAAT_GUN * TESPIT_SURESI_IndaQua_GUN) * yillik_sizinti_sayisi
    yillik_maliyet_IndaQua_tl = (yillik_kayip_IndaQua_lt / LITRE_M3) * su_maliyeti
    
    # Net Fayda ve ROI
    kurtarilan_su_m3 = (yillik_kayip_geleneksel_lt - yillik_kayip_IndaQua_lt) / LITRE_M3
    tasarruf_tl = yillik_maliyet_geleneksel_tl - yillik_maliyet_IndaQua_tl
    yatirim_tl = KURULACAK_SENSOR_SAYISI * sensor_maliyeti
    
    roi_yil = yatirim_tl / tasarruf_tl if tasarruf_tl > 0 else float('inf')

    return {
        "kurtarilan_su_m3": kurtarilan_su_m3,
        "tasarruf_tl": tasarruf_tl,
        "yatirim_tl": yatirim_tl,
        "roi_yil": roi_yil
    }

# --- ARAYÜZ TASARIMI ---

# --- Başlık ve Giriş ---
st.title("💧 IndaQua: Potansiyel Etki ve Fizibilite Simülatörü")
st.markdown("""
Bu interaktif simülatör, **IndaQua** projesinin potansiyel çevresel ve ekonomik etkisini modellemektedir. 
Yandaki menüden parametreleri değiştirerek projenin farklı koşullar altındaki performansını ve yatırım geri dönüş süresini (ROI) analiz edebilirsiniz.
""")

# --- YAN MENÜ (SIDEBAR) - Parametre Kontrol Paneli ---
st.sidebar.header("🔬 Model Parametreleri")
st.sidebar.info("Temel senaryo bu parametrelere göre hesaplanır. Diğer senaryolar bu temel değerlere göre oransal olarak oluşturulur.")

su_maliyeti_input = st.sidebar.slider(
    "1 m³ Suyun Maliyeti (TL)", 
    min_value=20.0, max_value=100.0, value=52.88, step=0.1, format="%.2f TL"
)
sensor_maliyeti_input = st.sidebar.slider(
    "Tek Bir Sensörün Maliyeti (TL)",
    min_value=500.0, max_value=1500.0, value=750.0, step=10.0, format="%f TL"
)
sizinti_debisi_input = st.sidebar.slider(
    "Ortalama Sızıntı Debisi (Litre/Dakika)",
    min_value=0.25, max_value=3.0, value=1.0, step=0.05, format="%.2f L/dk"
)
yillik_sizinti_sayisi_input = st.sidebar.slider(
    "100 km'lik Hatta Yıllık Ortalama Sızıntı Sayısı",
    min_value=10, max_value=100, value=50, step=1
)
geleneksel_tespit_suresi_input = st.sidebar.slider(
    "Geleneksel Yöntemle Ortalama Tespit Süresi (Gün)",
    min_value=7, max_value=60, value=30, step=1
)

# --- HESAPLAMALAR ---
# Senaryoları tanımla (temel senaryo ve diğerleri)
senaryolar = {
    "Temel Senaryo": {
        "sizinti_debisi": sizinti_debisi_input, "su_maliyeti": su_maliyeti_input, "sensor_maliyeti": sensor_maliyeti_input,
        "yillik_sizinti_sayisi": yillik_sizinti_sayisi_input, "geleneksel_tespit_suresi": geleneksel_tespit_suresi_input
    },
    "İyimser Senaryo (Su Fiyatları Artarsa)": {
        "sizinti_debisi": sizinti_debisi_input, "su_maliyeti": su_maliyeti_input * 1.25, "sensor_maliyeti": sensor_maliyeti_input,
        "yillik_sizinti_sayisi": yillik_sizinti_sayisi_input, "geleneksel_tespit_suresi": geleneksel_tespit_suresi_input
    },
    "Kötümser Senaryo (Yatırım Artarsa)": {
        "sizinti_debisi": sizinti_debisi_input, "su_maliyeti": su_maliyeti_input, "sensor_maliyeti": sensor_maliyeti_input * 1.25,
        "yillik_sizinti_sayisi": yillik_sizinti_sayisi_input, "geleneksel_tespit_suresi": geleneksel_tespit_suresi_input
    },
    "Operasyonel Senaryo (Düşük Sızıntı)": {
        "sizinti_debisi": sizinti_debisi_input * 0.75, "su_maliyeti": su_maliyeti_input, "sensor_maliyeti": sensor_maliyeti_input,
        "yillik_sizinti_sayisi": yillik_sizinti_sayisi_input, "geleneksel_tespit_suresi": geleneksel_tespit_suresi_input
    }
}

# Tüm senaryolar için sonuçları hesapla
sonuc_listesi = []
for ad, params in senaryolar.items():
    sonuc = hesapla_fizibilite(**params)
    sonuc_listesi.append({"Senaryo": ad, "Geri Dönüş (Yıl)": sonuc['roi_yil'], **sonuc})
    
df_sonuclar = pd.DataFrame(sonuc_listesi)
temel_sonuc = df_sonuclar.iloc[0]

# --- ANA EKRAN - Sonuçların Sunumu ---
st.header("📊 Temel Senaryo Analizi")
st.markdown("Yandaki menüden seçtiğiniz parametrelere göre elde edilen temel sonuçlar:")

col1, col2, col3 = st.columns(3)
col1.metric("Yıllık Potansiyel Tasarruf", f"{temel_sonuc['tasarruf_tl']:,.2f} TL")
col2.metric("Toplam Yatırım Maliyeti", f"{temel_sonuc['yatirim_tl']:,.2f} TL")
col3.metric("Kurtarılan Su Miktarı", f"{temel_sonuc['kurtarilan_su_m3']:,.0f} m³")

# Geri Dönüş Süresi için Gauge Chart
fig_gauge = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = temel_sonuc['roi_yil'],
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "Yatırımın Geri Dönüş Süresi (Yıl)", 'font': {'size': 24}},
    gauge = {
        'axis': {'range': [0, 5], 'tickwidth': 1, 'tickcolor': "darkblue"},
        'bar': {'color': "darkblue"},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, 1.5], 'color': 'green'},
            {'range': [1.5, 3], 'color': 'yellow'}],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': 4.5}}))
fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
st.plotly_chart(fig_gauge, use_container_width=True)

st.header("📈 Duyarlılık Analizi: Senaryoların Karşılaştırılması")
st.markdown("Farklı senaryolar altında projenin yatırım geri dönüş süresinin nasıl değiştiğini gösteren karşılaştırmalı analiz:")

# Senaryo karşılaştırması için Bar Chart
fig_bar = px.bar(
    df_sonuclar, 
    x='Senaryo', 
    y='Geri Dönüş (Yıl)', 
    color='Senaryo',
    text_auto='.2f',
    title="Farklı Senaryolara Göre Yatırım Geri Dönüş Süreleri"
)
fig_bar.update_traces(textposition='outside')
st.plotly_chart(fig_bar, use_container_width=True)

st.info("""
**Grafik Yorumu:** Bu grafik, projenin en kötü ve en iyi durumlardaki performansını gösterir. Temel varsayımlardaki değişimlere rağmen geri dönüş süresinin kabul edilebilir aralıkta kalması, projenin **sağlamlığını (robustness)** ve finansal olarak uygulanabilirliğini desteklemektedir.
""")

# --- Metodoloji Açıklaması ---
with st.expander("📘 Model Metodolojisi ve Varsayımlar"):
    st.markdown("""
    Bu simülatör, aşağıdaki formülasyona dayalı bir maliyet-fayda analizi yapar:

    1.  **Yıllık Su Kaybı (Litre)** = `(Sızıntı Debisi (L/dk) * 60 * 24 * Ortalama Tespit Süresi (Gün)) * Yıllık Sızıntı Sayısı`
    2.  **Yıllık Maliyet (TL)** = `(Yıllık Su Kaybı / 1000) * Su Fiyatı (TL/m³)`
    3.  **Yıllık Tasarruf (TL)** = `Geleneksel Yöntem Yıllık Maliyeti - IndaQua Yıllık Maliyeti`
    4.  **Toplam Yatırım (TL)** = `Sensör Sayısı * Tek Sensör Maliyeti`
    5.  **Geri Dönüş Süresi (Yıl)** = `Toplam Yatırım / Yıllık Tasarruf`

    **Temel Varsayımlar:**
    - Pilot bölge **100 km'lik** bir şebeke hattını temsil etmektedir.
    - Toplam **200 adet** sensörün stratejik olarak yerleştirileceği varsayılmıştır.
    - IndaQua sistemi ile tespit edilen bir sızıntıya **1 gün (24 saat)** içinde müdahale edileceği öngörülmüştür.
    - Analiz, kurulum işçiliği, bakım ve sunucu gibi operasyonel maliyetleri içermemektedir.
    """)
