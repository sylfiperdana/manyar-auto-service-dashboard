# Manyar Auto Service — Business Intelligence Dashboard

Dashboard Streamlit untuk proyek Statistika Terapan MIF1607, studi kasus CV. Manyar Auto Service.

> **Penting:** dataset proyek adalah data sintetis/simulasi, bukan transaksi aktual bengkel. Insight dan rekomendasi harus divalidasi sebelum digunakan sebagai keputusan operasional.

## Isi folder

```text
manyar_streamlit_dashboard/
├── app.py
├── requirements.txt
├── README.md
├── run_dashboard.bat
├── .streamlit/
│   └── config.toml
└── data/
    └── (letakkan 3 file CSV hasil notebook di sini)
```

## 1. Siapkan data dari Google Colab

Jalankan notebook revisi sampai cell **G. Dashboard BI** selesai. Notebook akan menghasilkan file:

- `dashboard_service.csv`
- `dashboard_inventory.csv`
- `dashboard_usage.csv`

Salin atau unduh ketiga file tersebut dari folder Google Drive:

`MyDrive/Statiska_Terapan/`

Kemudian letakkan ketiganya ke dalam folder `data/` di samping `app.py`.

Struktur akhir harus seperti ini:

```text
manyar_streamlit_dashboard/
├── app.py
├── requirements.txt
└── data/
    ├── dashboard_service.csv
    ├── dashboard_inventory.csv
    └── dashboard_usage.csv
```

File `dashboard_kpi.csv` dan `dashboard_bulanan.csv` tidak wajib untuk aplikasi karena KPI dan agregasi dihitung ulang dari data terfilter agar interaktif.

## 2. Jalankan di Windows

Pastikan Python 3.10 atau lebih baru sudah terpasang.

Buka terminal/CMD pada folder proyek, kemudian jalankan:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Cara alternatif: klik dua kali `run_dashboard.bat`.

Setelah berhasil, Streamlit akan membuka dashboard di browser. Jika tidak terbuka otomatis, akses alamat lokal yang ditampilkan di terminal, biasanya:

`http://localhost:8501`

## 3. Jalankan di macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 4. Fitur dashboard

### Filter global
- Rentang tanggal servis.
- Kategori pekerjaan/kerusakan.
- Tingkat keparahan.

Filter diterapkan pada KPI operasional, tren servis, biaya sparepart, dan analisis penggunaan sparepart.

### Enam KPI
1. Total servis.
2. ACC rate.
3. Rata-rata durasi servis ACC.
4. MAPE estimasi.
5. Jumlah item stok kritis.
6. Total biaya sparepart.

KPI inventori merupakan snapshot akhir periode sehingga tidak berubah mengikuti filter tanggal servis.

### Visualisasi dan insight
- Tren jumlah servis per bulan.
- Komposisi persetujuan servis.
- Rata-rata durasi per kategori pekerjaan/kerusakan.
- Rata-rata durasi per tingkat keparahan.
- Tren biaya sparepart.
- Sepuluh sparepart dengan penggunaan tertinggi.
- Tabel inventori kritis dan kesenjangan stok terhadap minimum.
- Insight numerik dan rekomendasi tindakan.

## 5. Catatan metodologis

- ACC rate dihitung dari seluruh servis yang lolos filter.
- Durasi rata-rata dan MAPE dihitung hanya dari servis ACC dengan nilai durasi valid.
- MAPE dihitung dari rata-rata persentase kesalahan absolut antara estimasi dan durasi aktual, dengan durasi aktual lebih besar dari nol.
- Total biaya sparepart dihitung dari kolom `biaya_sparepart` per servis yang telah dibuat pada tahap ETL.
- Item stok kritis didefinisikan sebagai `stok_akhir <= stok_minimum`.
- Data inventori merupakan snapshot akhir periode sehingga tidak berubah oleh filter tanggal.
- Tabel penggunaan sparepart mengikuti servis yang lolos seluruh filter.
- Nilai MAPE pada data sintetis bukan bukti akurasi prediksi pada transaksi nyata.
- Proporsi stok kritis bukan probabilitas stock-out di masa depan.

## 6. Deploy ke Streamlit Community Cloud (opsional)

1. Buat repository GitHub dan unggah `app.py`, `requirements.txt`, folder `.streamlit/`, serta folder `data/` berisi tiga CSV.
2. Pastikan data yang diunggah memang boleh dibagikan. Untuk proyek ini, dataset adalah simulasi.
3. Buka Streamlit Community Cloud dan hubungkan repository.
4. Pilih file utama `app.py` saat membuat aplikasi.
5. Deploy dan uji semua filter serta tabel.

Untuk tugas kuliah, aplikasi lokal yang berjalan dan dapat didemonstrasikan juga dapat menjadi bukti dashboard, selama dosen dapat mengaksesnya saat penilaian.
