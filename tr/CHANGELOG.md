[English](../CHANGELOG.md) | **Türkçe**

# Değişiklik günlüğü

Verinin ve bulguların her güncellemesinde neyin değiştiği. En yeni en üstte. Ana sayfadaki sayılar veriden üretilir; bu sayfa o sayıların nereden geldiğini söyler.

## 2026-09-20

- **129 depo eklendi** (toplam sayılan 909): 90'ı günlük `github.com/topics/jev` aramasından, 39'u topluluk kanalında herkese açık paylaşılanlardan. Paylaşılan iki bağlantı çoktan silinmişti, atlandı. Paylaşılan depoların on ikisinin Jev'le hiçbir bağı çıkmadı (genel ajan çatıları, altı haneli yıldız sayısına sahip bir liste, bir graf veritabanı, bir alım-satım botu); bunlar silinmedi, `calls_jev: no` ve sıfır puanla işaretlendi — yıldız sayısı hiçbir puana girmez.
- Bilinen her deponun **üstverisi tazelendi**; ortadan kalkan depolar silinmez, `gone` olarak işaretlenir.
- **28 kaynak eklendi** (toplam 88): yeni yayımlanmış 16 video ve Jev üzerine kurulu ya da Jev hakkında 12 web sitesi; her biri listeye girmeden önce Jev'le bağı, bağımsızlığı ve doğrulanabilirliği açısından puanlandı.
- **Bulgular**, her biri girmeden önce birincil sayfasından kontrol edildi ([`FINDINGS.md`](FINDINGS.md)):
  - üreticinin kendi lansman yazısı, wiki-race demosundaki karşılaştırma modellerinin muhakemesiz çalıştırıldığını söylüyor — DOĞRULANDI olarak eklendi;
  - türünün ilk bağımsız benchmark'ına dayanan yeni bir **önyargı ve adalet** bölümü (yalnız yöntem; yeniden çıkarmadığımız hiçbir sayıyı alıntılamıyoruz);
  - kalibrasyonun yaygın bir yanlış okuması ("%90 emin olmak on seferde dokuz doğru demektir") — TARTIŞMALI olarak eklendi;
  - bir iddia **reddedildi**: deterministik olmama üzerine bir söz üretici çalışanına atfedilmişti, ama transkript bunu konuk ayrıldıktan sonra programın sunucularının söylediğini gösteriyor.
- **Desenler**: API anahtarınızı kendi sunucusu üzerinden aktaran üçüncü taraf siteler hakkında bir uyarı ([`PATTERNS.md`](PATTERNS.md)).
- **Üretim hattı**: Markdown bağlantısı içeren bir açıklama build'i durdurduktan sonra, üçüncü taraf metni (depo açıklamaları, konu etiketleri) artık veriye dönüşmeden önce temizleniyor; denetim sonuçları artık tarihli paketler halinde içe aktarılabiliyor.
- **Denetim**: bugün ilk kez A sınıfı puanlanan satırlar, [`TOP.md`](TOP.md) sayfasına çıkabilmeden önce tek bir denetçi tarafından yeniden okunur; o zamana kadar denetlenmemiş olarak listelenir.

## 2026-09-19

- İlk veri seti: 785 depo (387'si topluluk kanalında paylaşılan, 398'i etiket aramasından), sabit ölçekle puanlandı; beş mükerrer çift işaretlendi.
- İlk puanlamada A sınıfı çıkan 288 satırın tamamı tek bir denetçi tarafından yeniden okundu; 261'i değişti, A sınıfı 288'den 217'ye indi ([`METHODOLOGY.md`](METHODOLOGY.md), 4. bölüm).
- 60 kaynak; bulgular, yöntem ve tekrar eden on iki desen İngilizce ve Türkçe yazıldı.
