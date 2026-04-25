# sidebar-notes

**YouTube:** https://youtube.com/@mertdmg  
**Kick:** https://kick.com/mertdmg

Favori dizi ve film oyuncularını takip eden haftalık haber özeti sistemi.

## İçerik

- `people/names.md` — takip listesi: dizi/film başlıklarıyla birlikte oyuncu isimleri
- `weekly/` — her hafta otomatik oluşturulan oyuncu haberleri (Google News RSS)
- `scripts/weekly_rss.py` — RSS çekme ve markdown oluşturma betiği
- `.github/workflows/weekly.yml` — GitHub Actions ile haftalık otomatik çalıştırma

## Nasıl Çalışır

`people/names.md` dosyasındaki oyuncu isimleri her hafta Google News RSS üzerinden taranır ve `weekly/` klasörüne tarih bazlı markdown dosyası olarak kaydedilir.
