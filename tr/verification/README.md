[English](../../verification/README.md) | Türkçe

# Başkalarının sayılarını yeniden koşmak

Bu klasör, topluluk depolarının Jev hakkında yayımladığı **metinsel** testleri
kendi API anahtarımızla, testin **orijinal dilinde** ve **orijinal girdileriyle**
yeniden koşar; sonra yayımlanan sayının geri gelip gelmediğini açıkça söyler.

Var olma nedeni basit: bu depo, okurun doğrulayamayacağı bir sayıyı yayımlamayı
reddediyor. "%96,5 isabet" cümlesini bir README öyle diyor diye aktarmak, tam da
bu deponun yapmamak için kurulduğu şey.

## Ne iddia edilir, ne edilmez

- **Tekrar üretilebilirlik testi.** Kaynak kendi verisini kendi elleriyle
  etiketlemiş; biz aynı maddeleri aynı uç noktaya aynı sorularla gönderiyoruz.
  Tutması, hattın tekrar ürettiğini gösterir — etiketlerin doğru olduğunu değil.
- **Bağımsız doğrulama.** Etiketler kaynağın üretmediği açık bir veri setinden
  geliyor. Tutması daha değerlidir, çünkü iki ayrı şeyin uyuşması gerekti.

Her iş tanımı hangisi olduğunu `kind` alanında söyler, rapor da tekrarlar. Bu
ayrım başlıkta bile bulanıklaştırılmaz.

- Metin dışı testler — oyun, robotik, tarayıcı kontrolü — yeniden **koşulmaz**;
  kaynağı gösterilerek, kaynağın kendi sayısı olarak aktarılır.
- Hiçbir şey çevrilmez. Çevrilmiş bir istem başka bir istemdir, çevrilmiş bir
  cevap başka bir ölçümdür. Türkçe sayfalar testi Türkçe anlatır, testin kendisini
  yazıldığı dilde gösterir.

## Bir iş nasıl işler

1. `jobs/` altındaki iş tanımı kaynak depoyu bir **commit'e** sabitler (dala
   değil); veri setini ve nasıl erişildiğini yazar; kaynağın kendi soru metnini
   harfi harfine, geldiği dosya ve satır aralığıyla kopyalar; ve **sayının
   yeniden üretilmiş sayılması için ne gerektiğini** önceden sabitler.
2. Bu dosya commit'lenir. Kabul ölçütünün sonuca göre yazılmadığının kanıtı git
   geçmişidir.
3. `run.py` maddeleri kurar, madde başına tek istek gönderir (soru bataryasının
   tamamı tek çağrıda — kaynaklar da öyle gönderiyor) ve her cevabı
   `results/<is>/raw.jsonl` dosyasına satır satır ekler.
4. `summary.json` sayıları, güven aralıklarını, uç noktanın bildirdiği model
   sürümünü, çağrı sayısını ve hükmü taşır. `REPORT.md` aynı şeyi düzyazıyla,
   ters giden her şey dahil anlatır.

Hükümler: `reproduced`, `partially reproduced`, `not reproduced`, `not run`.
Koşulmamış bir ölçüt asla geçmiş sayılmaz; bir işin hükmü, parçalarının en zayıf
hükmüdür.

## Bu klasörün kuralları

- **Anahtar hiçbir yerde görünmez.** Ortamdan okunur, tek bir başlığa konur, geri
  kalan her metinden maskelenir.
- **Üçüncü taraf metni saklanmaz.** Ham satır maddenin kimliğini, metninin
  özetini (sha256) ve isteğin özetini taşır; veri setinin kendisini değil. Lisans
  izin verse bile: araştırma dosyası bir ayna değildir.
- **Hiçbir kaynak depo klonlanmaz, kodu çalıştırılmaz.** Soru metni ve
  commit'lenmiş çıktılar, commit'e sabitlenmiş adreslerden dosya olarak indirilir.
- **Çağrı bütçesi tahmin edilmez, sayılır.** Bkz. `BUDGET.md`.

## Koşmak

```
python -X utf8 verification/run.py --job sec-injection --dry-run
python -X utf8 verification/run.py --job sec-injection
```

Anahtar `TYPESAFE_API_KEY` değişkeninden okunur. Koşum yarıda kesilip yeniden
başlatılabilir; cevabı olan maddeler atlanır, aynı şeye iki kez ödenmez.

Birim testleri ağa hiç çıkmaz ve anahtarı olmayan bir makinede de geçer.
