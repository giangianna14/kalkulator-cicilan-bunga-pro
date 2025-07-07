# Test Cases untuk Kalkulator Cicilan & Bunga

## Test Case 1: Kredit Bank (Anuitas)
**Input:**
- Pinjaman: Rp 100.000.000
- Bunga: 12% per tahun
- Jangka waktu: 5 tahun

**Expected Output:**
- Cicilan bulanan: Rp 2.224.444
- Total pembayaran: Rp 133.466.640
- Total bunga: Rp 33.466.640

## Test Case 2: Bunga Majemuk
**Input:**
- Modal awal: Rp 10.000.000
- Bunga: 10% per tahun
- Jangka waktu: 10 tahun
- Frekuensi: Bulanan

**Expected Output:**
- Nilai akhir: Rp 27.070.416
- Total bunga: Rp 17.070.416

## Test Case 3: Deposito
**Input:**
- Jumlah deposito: Rp 50.000.000
- Bunga: 6% per tahun
- Jangka waktu: 12 bulan
- Pajak: 20%

**Expected Output:**
- Bunga kotor: Rp 3.000.000
- Pajak: Rp 600.000
- Bunga bersih: Rp 2.400.000
- Total akhir: Rp 52.400.000

## Test Case 4: Kredit Kendaraan
**Input:**
- Harga kendaraan: Rp 200.000.000
- Uang muka: 20% (Rp 40.000.000)
- Bunga: 8% per tahun
- Jangka waktu: 3 tahun

**Expected Output:**
- Pinjaman: Rp 160.000.000
- Cicilan bulanan: Rp 5.013.748
- Total bunga: Rp 20.494.928

## Test Case 5: KPR
**Input:**
- Harga properti: Rp 500.000.000
- Uang muka: 20% (Rp 100.000.000)
- Bunga: 10% per tahun
- Jangka waktu: 15 tahun

**Expected Output:**
- Pinjaman: Rp 400.000.000
- Cicilan bulanan: Rp 4.304.157
- Total bunga: Rp 377.748.260

## Validation Steps

1. **Functional Testing**
   - Semua input field dapat diisi
   - Perhitungan otomatis saat input berubah
   - Grafik ter-render dengan benar
   - Export functionality bekerja

2. **UI/UX Testing**
   - Responsive design di berbagai ukuran layar
   - Navigation antar kalkulator smooth
   - Loading time acceptable
   - Error handling yang baik

3. **Mathematical Accuracy**
   - Validasi rumus dengan kalkulator finansial standard
   - Cross-check dengan Excel financial functions
   - Test edge cases (bunga 0%, nilai ekstrim)

4. **Performance Testing**
   - Test dengan data besar
   - Memory usage monitoring
   - Browser compatibility

## Manual Testing Checklist

- [ ] Install aplikasi berhasil
- [ ] Aplikasi berjalan tanpa error
- [ ] Semua kalkulator dapat diakses
- [ ] Input validation bekerja
- [ ] Perhitungan mathematically correct
- [ ] Grafik ditampilkan dengan benar
- [ ] Export functionality
- [ ] Mobile responsive
- [ ] Error handling
- [ ] Performance acceptable
