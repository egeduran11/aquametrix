import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# --- 1. SİMÜLASYON PARAMETRELERİNİ AYARLA ---
sample_rate = 44100  # Saniyedeki örnek sayısı (CD kalitesi)
duration = 2  # Simülasyon süresi (saniye)
t = np.linspace(0., duration, int(sample_rate * duration), endpoint=False)

# --- 2. SİNYALLERİ OLUŞTUR ---
# a) Şehir Gürültüsü
city_noise = 0.6 * np.random.randn(len(t))

# b) Su Sızıntısı (400 Hz)
leak_frequency = 400
leak_sound = 0.7 * np.sin(2. * np.pi * leak_frequency * t)

# c) Toplam Sinyal
total_signal = city_noise + leak_sound

# --- 3. FREKANS ANALİZİ (FFT) ---
# Güç spektrumu yoğunluğu hesaplama
freqs, psd_total = signal.welch(total_signal, sample_rate, nperseg=2048)
freqs_leak, psd_leak = signal.welch(leak_sound, sample_rate, nperseg=2048)

# --- 4. GÖRSELLEŞTİRME ---
try:
    plt.style.use('seaborn-v0_8-whitegrid')
except:
    plt.style.use('seaborn-whitegrid')  # Eski sürümler için

fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(4, 2, hspace=0.3, wspace=0.3)

# Zaman domeninde sinyaller (sol kolon)
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(t[:2000], total_signal[:2000], color='red', alpha=0.8, linewidth=0.8)
ax1.set_title('A: Ham Mikrofon Sinyali (İlk 0.045s)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Genlik', fontsize=10)
ax1.grid(True, alpha=0.3)

ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(t[:2000], city_noise[:2000], color='gray', alpha=0.7, linewidth=0.8)
ax2.set_title('B: Arkaplan Gürültüsü', fontsize=12, fontweight='bold')
ax2.set_ylabel('Genlik', fontsize=10)
ax2.grid(True, alpha=0.3)

ax3 = fig.add_subplot(gs[2, 0])
ax3.plot(t[:2000], leak_sound[:2000], color='blue', linewidth=1.2)
ax3.set_title('C: İzole Sızıntı Sinyali (400 Hz)', fontsize=12, fontweight='bold')
ax3.set_xlabel('Zaman (saniye)', fontsize=10)
ax3.set_ylabel('Genlik', fontsize=10)
ax3.grid(True, alpha=0.3)

# Frekans domeninde analiz (sağ kolon)
ax4 = fig.add_subplot(gs[0:2, 1])
ax4.semilogy(freqs, psd_total, color='red', alpha=0.8, label='Toplam Sinyal')
ax4.axvline(leak_frequency, color='blue', linestyle='--', linewidth=2, label=f'Sızıntı Frekansı ({leak_frequency} Hz)')
ax4.set_xlim([0, 1000])
ax4.set_title('D: Frekans Spektrumu (Güç Spektral Yoğunluğu)', fontsize=12, fontweight='bold')
ax4.set_xlabel('Frekans (Hz)', fontsize=10)
ax4.set_ylabel('Güç/Frekans (dB/Hz)', fontsize=10)
ax4.legend(fontsize=9)
ax4.grid(True, alpha=0.3)

# Temiz sızıntı spektrumu
ax5 = fig.add_subplot(gs[2:4, 1])
ax5.semilogy(freqs_leak, psd_leak, color='blue', linewidth=1.5)
ax5.axvline(leak_frequency, color='darkblue', linestyle='--', linewidth=2, alpha=0.7)
ax5.set_xlim([0, 1000])
ax5.set_title('E: Sızıntı Sinyali Spektrumu (Filtrelenmiş)', fontsize=12, fontweight='bold')
ax5.set_xlabel('Frekans (Hz)', fontsize=10)
ax5.set_ylabel('Güç/Frekans (dB/Hz)', fontsize=10)
ax5.grid(True, alpha=0.3)

# İstatistikler
ax6 = fig.add_subplot(gs[3, 0])
ax6.axis('off')
stats_text = f"""
AKUSTIK SİMÜLASYON RAPORU
{'='*40}
Örnekleme Frekansı: {sample_rate} Hz
Süre: {duration} saniye
Toplam Örnek: {len(t):,}

Sızıntı Sinyali:
  • Frekans: {leak_frequency} Hz
  • Genlik: 0.7
  • SNR: {10*np.log10(np.var(leak_sound)/np.var(city_noise)):.2f} dB

Gürültü Seviyesi:
  • Standart Sapma: {np.std(city_noise):.3f}
  • Maksimum: {np.max(np.abs(city_noise)):.3f}
"""
ax6.text(0.1, 0.5, stats_text, fontsize=9, family='monospace',
         verticalalignment='center', bbox=dict(boxstyle='round', 
         facecolor='wheat', alpha=0.3))

plt.savefig('akustik_simulasyon_gelismis.png', dpi=300, bbox_inches='tight')
print("✓ Grafik başarıyla kaydedildi: akustik_simulasyon_gelismis.png")
plt.show()
