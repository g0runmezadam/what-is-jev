[English](../METHODOLOGY.md) | **Türkçe**

# Yöntem

Gerçekte ne yaptığımız, yaptığımız sırayla. Bu sayfada hiçbir adım "yapılacak" diye yazılmaz — bir adım henüz koşmadıysa, sayfa bunu söyler.

## 1. Kapsam: yalnız herkese açık kaynaklar

Bu depodaki her şey herkesin açabileceği malzemeden geliyor: resmi doküman, herkese açık GitHub depoları, herkese açık videolar, yazılar ve gönderiler, artı tekrarlayabilmeniz için nasıl yaptığımızı anlattığımız kendi API çağrılarımız. Üçüncü taraf içeriğini bu depoya kopyalamıyoruz — bir bulgu ya da repo kaydı kaynağına bağlanır ve bizim değerlendirmemizi taşır, kaynağın metnini asla yeniden üretmez. Buradaki hiçbir şey özel ya da ücretli malzemeye dayanmıyor. Okurun doğrulayamayacağı rakamları yayımlamıyoruz. Kendi ölçtüğümüz her şey ya belgelenmiş herkese açık API'ye karşı tekrarlanabilir ya da dışarıda bırakılır.

## 2. Repo keşfi

2026-09-19'da toplanan, birbirinden bağımsız iki GitHub repo kümesi:

- **A kümesi — topluluk kanalı.** Bir topluluk kanalında herkese açık paylaşılan 387 repo bağlantısı (ham mesaj dökümü yerel bir çalışma dosyası olarak tutulur, yayımlanmaz; elimizde kalan şey bağlantı ve paylaşanın yorumudur).
- **B kümesi — etiket araması.** `github.com/topics/jev` 433 repo döndürdü; bunların 35'i zaten A kümesindeydi, geriye 398 yeni repo kaldı.
- Toplam: 785 repo.

Her biri için GitHub API'sinden üstveri çektik (yıldız, fork, dil, lisans, tarihler, arşiv/fork durumu, etiketler) ve README'nin ilk 12.000 karakterini. A kümesindeki 11 repo 404 döndürdü (silinmiş ya da özel yapılmış) — bunlar veriden silinmez, `status: gone` ile işaretlenerek tutulur, çünkü var olup kaldırılmış bir repo kendi başına bir veri noktasıdır.

`jev` serbest bir GitHub etiketidir. Bu etiketi taşıyan pek çok deponun TypeSafe'in modeliyle ilgisi yoktur; bunları `calls_jev: no`, kategori `other` diye puanlıyoruz ve sessizce elemek yerine tutuyoruz.

## 3. Puanlama

Her repo aynı sabit ölçekle puanlanır ([`data/rubric.md`](../data/rubric.md), `version: 1`): beş eksen (depth, relevance, novelty, maturity, evidence), her biri 0–3, toplam 0–15, A/B/C sınıfına eşlenir. Puanlar bir dil modeli ajanının yazılı ölçeğe göre yargısıdır, kodun benchmark'ı değildir — çoğu repo için README ve üstveri dışına bakılmadı.

785 repo parçalara bölündü ve aynı ölçeği kullanan ayrı ajan oturumları tarafından puanlandı. Yıldız sayısı hiçbir puanı etkilemez — ölçek bunu açıkça söylüyor, aşağıdaki denetim geçişinde de kontrol ediliyor. Bir reponun README'si puanlayıcı ajana talimat değil veri olarak ele alınır; README okuyucuya bir ajanmış gibi hitap ediyorsa bu bir risk olarak kaydedilir (gömülü talimat), asla uygulanmaz.

## 4. Tutarlılık: A sınıfı denetimi

Aynı ölçeğin bağımsız oturumlarda puanlanması tutarlı sonuç vermedi: A sınıfı oranı oturumdan oturuma %25 ile %60 arasında değişti. A sınıfı aynı zamanda ekosistemin gerçekten yönlendirildiği listedir (`TOP.md`), bu yüzden bu tutarsızlığın yaşayabileceği en kötü yer orasıdır.

Tasarladığımız çözüm tek gözlü bir denetim: bir ajan oturumu her A sınıfı satırı, değişmeyen ölçeğe göre yeniden okur; en çok kötüye kullanılan kurala odaklanır — toplamı 11'in altında olsa bile bir satırı `relevance = 3` ve `novelty ≥ 2` ile A sınıfına kabul eden kısayol — ve tipik şişirme kalıplarına bakar (oyun ya da genel bir SDK'ya relevance=3 verilmiş, temel desene yüksek novelty verilmiş, README'de hiçbir sayı yokken yüksek evidence verilmiş). Gözden geçirilen satır `audited: true` ve neyin neden değiştiğini/korunduğunu açıklayan, iki dilde bir denetim notu alır; denetlenen bir satırda sınıf çelişkisi denetçinin lehine çözülür.

**Denetimin bulduğu (2026-09-19).** İlk puanlamada A sınıfı çıkan 288 satırın tamamı tek bir denetçi tarafından, README açılarak yeniden okundu. 261'inde en az bir puan değişti. Açık ara en sık şişirme **olgunluk** puanındaydı (176 satırda düşürüldü: bu depoların çoğu birkaç günlüktü; "test, sürüm ve aktif bakım" bir günlük bir depoyu tarif edemez), ardından **yenilik** (103: birbirinin portu olup temel deseni tekrarlayanlar), **kanıt** (79: alıntılanan fiyat ya da gecikme ölçüm değildir), **ilgililik** (64) ve **derinlik** (41: Jev'i hiç çağırmayan yeniden üretimler). A sınıfından düşen satırların oranı, satırı hangi puanlama oturumunun ürettiğine göre %9 ile %47 arasında değişti. Beş mükerrer çift (yeniden adlandırılmış depolar, birebir aynı README'ler) işaretlendi ve sayımlara girmiyor.

Sonucu okurken iki şeyi bilmek gerekir. Birincisi, A sınıfı hâlâ geniştir, çünkü ölçek bir satırı iki kapıdan birinden içeri alır — toplam 11 ve üzeri, ya da `relevance = 3` ile `novelty ≥ 2` — ve ajan kapıları, yönlendiriciler ve compaction araçlarının ağır bastığı bir derlemde ikinci kapı dürüstçe geniştir. Ölçeği sonradan değiştirmedik; bunun yerine [`TOP.md`](TOP.md) ayrı bir **ölçümle desteklenen çekirdek** (denetlenmiş, A sınıfı, toplam 13 ve üzeri) bölümünü geri kalanın üstünde tutar. İkincisi, dört satırda denetçi, proje yalnızca kendisinde olmayan bir donanımda çalıştığı için ilgililik puanını düşürmüştü; bu projenin bir özelliği değildir, bu yüzden o dört ilgililik puanı geri alındı ve satırlar ölçeğe göre yeniden sınıflandı. `TOP.md`'de yalnızca denetlenmiş satırlar görünür. İlk puanlamada B ya da C çıkan satırlar denetlenmedi. Sonraki her güncelleme, yeni A sınıfı puanlanan satırlar için bu denetimi tekrarlar: tek bir denetçi README'yi okur ve satır ancak ondan sonra `TOP.md` sayfasına girebilir; her denetim ve sonucu [`CHANGELOG.md`](CHANGELOG.md) dosyasına kaydedilir.

## 5. Videolar

Herkese açık, 33 kaynaklık tek bir video listesinden başladık. Transkripti olanların otomatik transkriptleri okundu; transkriptlerin kendisi burada yeniden yayımlanmaz, yalnızca onlardan çıkardığımız bilgi ve kaynağa geri dönen bir bağlantı yer alır. 33'ünden: 7'si Jev'le ilgisiz çıktı, 2'sinin transkripti boştu, 2'si hiç çekilemedi. Bu videoların ikincil, yapay-zekâ üretimi bir özeti vardı (bir defter aracından) ve üreticinin dilini eleştirmeden tekrarlıyordu ("deterministik", "%90 emin olmak %90 doğru olmak demektir", "doğrulama katmanına gerek yok") — bu özeti hiçbir şey için kanıt saymıyoruz; bir video bir iddia içeriyorsa, transkriptin kendisine döndük.

## 6. Web doğrulaması

Videolarda ya da ikincil yazılarda geçen iddialar, doğrulanmış diye işaretlenmeden önce birincil sayfalarından kontrol edildi. Bu depo boyunca kullanılan hüküm etiketleri — **DOĞRULANDI**, **ÜRETİCİ İDDİASI**, **TARTIŞMALI**, **BULUNAMADI** — iddianın ne kadar inandırıcı geldiğini değil, bu kontrolün ne kadar ileri gittiğini anlatır.

## 7. Dürüst sınırlar

Bu liste README'dekinden bilinçli olarak daha uzun, çünkü bu sayfa belirli bir satıra ya da iddiaya ne kadar güveneceğine karar veren kişi için yazıldı:

- Her repo puanı, yazılı bir ölçeğe göre bir dil modelinin yargısıdır — projenin bir ölçümü değildir, ve yukarıdaki A sınıfı denetimi dışında bağımsız olarak yeniden türetilmiş değildir.
- Çoğu repo için açıklamayı, üstveriyi ve README'nin ilk 12.000 karakterini okuduk. Kodu okumadık. Bir proje README'sinin gösterdiğinden anlamlı ölçüde daha iyi ya da daha kötü olabilir.
- Bütün bu çalışma tek günlük bir kesittir (2026-09-19). GitHub repoları, üretici dokümanı ve fiyatlandırma bu tarihten sonra değişir; `data/repos.jsonl`'deki her satır puanlandığı tarihi ve kullanılan ölçek sürümünü taşır, tam olarak okuyucunun ne kadar eskimiş olabileceğini anlaması için.
- İngilizce ve Türkçe özetler/çıkarımlar birlikte üretilir ve anlam bakımından gözden geçirilir, kelimesi kelimesine çevrilmez — ikisi birbirinden ayrışırsa bunu bir hata sayın ve issue açın (bkz. [`CONTRIBUTING.md`](CONTRIBUTING.md)).
- Yıldız sayısı, takipçi sayısı ve izlenme sayısı bu depoda hiçbir yerde hiçbir puana girmez.

## 8. Güncel kalmak

`tools/update.py` yeni repoları bulur (etiket araması + `data/manual.txt`) ve bilinenlerin üstverisini tazeler. Hiçbir model çağırmaz, hiçbir şey puanlamaz — yeni repolar `data/pending.txt`'e düşer, bir ajan tarafından güncel `data/rubric.md`'ye göre puanlanır, `tools/build.py` tarafından birleştirilir; bu betik iki dildeki bütün üretilen sayfaları `data/repos.jsonl`'den yeniden üretir. 404 vermeye başlayan bir repo `status: gone` diye işaretlenir, asla silinmez, böylece geçmiş görünür kalır.

Ölçeğin kendisi sürümlüdür (her satırdaki `rubric_version`). Ölçek değişirse, mevcut satırlar yeniden puanlanana kadar puanlandıkları sürümü taşımaya devam eder — bir satır asla sessizce daha yeni bir ölçeğe göre yeniden yorumlanmaz.

## 9. Düzeltme istemek

Bir bulgu, bir puan ya da bir özet yanlış görünüyorsa: ona karşı çıkan birincil kaynağa bağlantı vererek bir issue ya da pull request açın. Kesin süreç için [`CONTRIBUTING.md`](CONTRIBUTING.md)'ye bakın — düzeltmeler bu deponun en çok ihtiyaç duyduğu katkı türüdür, çünkü buradaki her iddia ancak arkasındaki kaynak kadar sağlamdır.
