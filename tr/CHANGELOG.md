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
- **Denetim**: denetim bekleyen 54 A sınıfı satırın tamamı (42'si bugün ilk kez puanlandı, 12'si 2026-09-19'da puanlanmış ve ölçek kuralıyla A sınıfına geçmişti), tek bir denetçi tarafından README açılarak, değişmeyen ölçeğe göre yeniden okundu. 31'inde puan değişti; 11'i A sınıfından düştü (43'ü kaldı, 7'si B, 4'ü C oldu). Bu kez en sık şişirme **yenilik** puanındaydı — temel deseni tekrarlayan portlar ve yeniden üretimler — ardından olgunluk geldi. Sekiz deponun kanıt puanı *yükseltildi*, çünkü kendi yayımladıkları ölçümler eksik sayılmıştı. Denetlenmiş satır sayısı 337 oldu; bekleyen yok.
- **Aynı gün, daha sonra** — yeni depolar çıkmaya devam ettikçe iki paket daha: önce 24, sonra 14 (ikincisi topluluk kanalında paylaşılan son bağlantıları da içeriyor); toplam 38 depo (toplam sayılan 947). Bunlardan A sınıfı çıkan 16 satır tek bir denetçi tarafından yeniden okundu: 13'ü A sınıfında kaldı, 3'ü B'ye geçti. Paylaşılan iki bağlantı silinmişti, atlandı.
- **Bulgular**: muhakemesi açık modellere karşı bağımsız bir birebir karşılaştırma ([depo](https://github.com/manjunathshiva/jev-frontier-bench)) README'siyle sayı sayı karşılaştırıldı ve iki yere eklendi — hız, maliyet ve isabet altına (DOĞRULANDI: 200 kararda Jev'i açıkça geçen yalnız iki amiral gemisi model; bu örneklemde yaklaşık on puanın altındaki farklar gürültüdür) ve kalibrasyon altına (TARTIŞMALI: kalibrasyon hatası en güçlü modelden kötü, 100 etiketleyicili insan dağılımına kör bir tahminden daha uzak). Yazarın duyurusundaki bir rakam README'de bulunamadı ve dışarıda bırakıldı.
- **Kaynaklar**: toplam 90. Bugün daha önce girilen üç güven değeri ölçeği ters kullanmıştı (en güvenilir 5'tir, 1 değil); düzeltildi.
- **Üretim hattı**: aynı gün gelen ve aynı depoya dokunan iki puanlama dosyası artık eskisinin kazanmasına izin vermek yerine koşumu durduruyor; bir denetim, okuduğu puanlama paketini adıyla belirtmek zorunda, böylece bayat bir denetim daha yeni bir puanı onaylayamıyor; sayı beklenen yerde `true` artık kabul edilmiyor; ağ paylaşımı yolları, ev dizinleri ve dosya adresleri gizlilik desenlerine eklendi.

## 2026-09-19

- İlk veri seti: 785 depo (387'si topluluk kanalında paylaşılan, 398'i etiket aramasından), sabit ölçekle puanlandı; beş mükerrer çift işaretlendi.
- İlk puanlamada A sınıfı çıkan 288 satırın tamamı tek bir denetçi tarafından yeniden okundu; 261'i değişti, A sınıfı 288'den 217'ye indi ([`METHODOLOGY.md`](METHODOLOGY.md), 4. bölüm).
- 60 kaynak; bulgular, yöntem ve tekrar eden on iki desen İngilizce ve Türkçe yazıldı.
