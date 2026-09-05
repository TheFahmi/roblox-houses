# Luxury Houses — Roblox City

40 rumah dalam 8 kompleks, lengkap ekonomi: beli rumah, kerja kurir, kunci pintu, gerbang otomatis. Buka di Roblox Studio, publish, main.

## Isi
- `houses.rbxlx` — place file
- `generate_houses.py` — generator dunia (stdlib only): 40 rumah, jalan, plaza, furnitur
- `HouseLogic.lua` — semua gameplay script (tertanam otomatis saat regen)
- `audit_houses.py` — audit geometri (SAT): furnitur vs tembok, tangga, pintu

## Rumah (8 jenis × 5 unit, nama folder `Jenis#1` … `Jenis#5`)
| Jenis | Harga | Ciri |
|---|---|---|
| TinyHouse | $500 | kabin starter, beranda |
| ZenHouse | $800 | paviliun Jepang, kolam koi |
| AFrame | $1.200 | chalet kayu, fireplace |
| ModernCube | $2.000 | kaca + emas, mezzanine |
| Dome | $2.500 | kubah kaca, ranjang bundar |
| VillaL | $3.000 | kolam renang, 2 lantai |
| Castle | $5.000 | tahta emas, menara 3 lantai |
| Mansion | $8.000 | ballroom, 3 suite, air mancur |

## Gameplay
- **Beli rumah** — klik papan kayu di samping pintu. Uang (leaderstats Cash) mulai $200.
- **Uang** — pasif $5/10 detik; **kerja kurir**: klik depot di plaza → antar ke 8 kompleks berurutan → $15/antaran + $50 bonus rute.
- **Kunci pintu** — pemilik klik pintu: merah = terkunci, orang lain tidak bisa masuk.
- **Gerbang otomatis** — pagar depan membuka sendiri saat didekati.
- **Pintu** — membuka saat didekati, menutup 3 detik kemudian. Bel pintu emas bunyi + papan "ada tamu".
- **Duduk** — kursi/sofa/lounger semuanya bisa diduduki.
- **Day/night** — 24 jam game per 4 menit.
- **Save** — Cash tersimpan via DataStore (autosave 60s + saat keluar). Di Studio: aktifkan *Enable Studio Access to API Services*.

## Layout dunia
- Plaza pusat: air pancur, spawn, depot kurir, jalan kota
- 8 kompleks (baris 5 unit sejenis) di sisi barat, jalan induk + jalan akses per kompleks
- Pagar + gerbang mengelilingi tiap lot

## Pakai
Roblox Studio → File → Open from File → `houses.rbxlx` → Publish.

Regen: `python3 generate_houses.py`. Audit: `python3 audit_houses.py` (harus `0 issues`).
