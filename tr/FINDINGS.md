[English](../FINDINGS.md) | **Türkçe**

# Bulgular — Jev gerçekte nedir, hakkında söylenenlerin ne kadarı doğrulanıyor?

Son gözden geçirme: 2026-09-19 · Gözlenen model sürümü: `jev-1.13.0` · Her satır kaynağına bağlanır. Güven sırası ve yöntem: [`METHODOLOGY.md`](METHODOLOGY.md). Tam kaynak listesi: [`SOURCES.md`](SOURCES.md).

Hüküm etiketleri: **DOĞRULANDI** (birincil kaynak ya da herkesin belgelenmiş API'ye karşı tekrarlayabileceği bir çağrı) · **ÜRETİCİ İDDİASI** (üreticinin söylediği doğru; bağımsız doğrulanmadı) · **TARTIŞMALI** (bağımsız kanıt çelişiyor ya da nitelik ekliyor) · **BULUNAMADI** (birincil kaynağını bulamadık). Bu dördünün uymadığı yerde iki işaret daha geçer: **ANEKDOT** (bağlantı veremediğimiz ya da tekrarlayamadığımız herkese açık bir rapor — asla kanıt olarak kullanılmaz) ve **BİZİM ÇIKARIMIMIZ** (üstündeki bağlantılı satırlardan kendi çıkarımımız; bir kaynaktan alınmış olgu değil).

## 1. Ne olduğu

| Bulgu | Hüküm | Kaynak |
|---|---|---|
| Jev bir karar modelidir, metin üreteci değil. Bir `state` (durum) ve tipli sorular gönderirsiniz; olasılık döner. Üç soru tipi: **choice** (255 seçeneğe kadar), **score** (sıralı basamaklar), **noul** (evet/hayır). Düz yazı yazmaz, gerekçe vermez. | DOĞRULANDI | [TypeSafe dokümanı](https://docs.typesafe.ai/llms.txt); kendi çağrılarımız — `POST https://api.typesafe.ai/v1/systemone` (uç nokta ve istek biçimi belgeli, kendi API anahtarı olan herkes bu çağrıyı tekrarlayabilir) |
| Aynı durum üzerinden tek istekte pek çok soru sorulabilir; sorular eklendikçe gecikme kabaca sabit kalır. | DOĞRULANDI | [TypeSafe dokümanı](https://docs.typesafe.ai/llms.txt); kendi çağrılarımız (3 soru ≈ Türkiye'den uçtan uca 0,6–1,0 sn; belgelenmiş uç noktaya karşı tekrarlanabilir) |
| Bağlam sınırlıdır: toplam 64k token, state artı en uzun soru için 32k. | DOĞRULANDI | [Model jaggedness: jev-1.13](https://docs.typesafe.ai/model-jaggedness/jev-1.13) |
| Fiyat: 1M girdi token başına 0,042 $, çıktı token'ı faturalanmıyor. | DOĞRULANDI | [Vercel AI Gateway model sayfası](https://vercel.com/ai-gateway/models/jev) (üreticinin kendi fiyatlandırma sayfası kontrol ettiğimizde 404 döndü) |
| Aynı model hem üretici API'sinden hem Vercel AI Gateway üzerinden erişilebilir, ama istek biçimleri farklı (evet/hayır birinde `noul`, ötekinde `boolean`; güven birinde cevabın içinde, ötekinde sağlayıcı üstverisinde). | DOĞRULANDI | Kendi çağrılarımız; [vercel/ai gateway kaynağı](https://github.com/vercel/ai/blob/main/packages/gateway/src/gateway-evaluation-model.ts) |
| Şirket: TypeSafe AI; DCVC liderliğinde 40M$ seed; kurucular Diogo Almeida (eski OpenAI), Erik Gafni, Sasha Sheng. | DOĞRULANDI | Birden çok bağımsız haber kaynağında ve hukuk firmasının kendi duyurusunda tutarlı — bağlantılar [`SOURCES.md`](SOURCES.md) içinde "funding" altında |

## 2. "Halüsinasyon göremez" gerçekte ne demek

| Bulgu | Hüküm | Kaynak |
|---|---|---|
| Garanti **biçimle** ilgilidir: Jev yalnızca verdiğiniz seçenekler içinde cevap verebilir, bu yüzden bozuk biçimli çıktı olmaz. Yine de yanlış seçeneği kendinden emin şekilde seçebilir. | DOĞRULANDI | [TypeSafe dokümanı](https://docs.typesafe.ai/llms.txt); [`SOURCES.md`](SOURCES.md) içinde listelenen bağımsız video demoları |
| Üretici kendi zayıflık listesini yayımlıyor: literal okuma, matematik ve sayılar ("Jev bir hesap makinesi değildir"), tarih/saat karşılaştırması, dolaylı anlatım (indirection), ilgisiz ayrıntıyla dolu büyük state, düşmanca içerik, çelişkili talimat ve ölçütler, üretim (generation). | DOĞRULANDI | [Model jaggedness: jev-1.13](https://docs.typesafe.ai/model-jaggedness/jev-1.13) |
| Jev çağrıdan çağrıya **deterministik değildir**: aynı sorunun olasılığı çağrılar arasında hafifçe kayar, bu yüzden eşiğe yakın bir değer eşiklenmiş cevabı ters çevirebilir. (Bir geliştirici üreticinin topluluk Discord'unda tek bir soru için 0,50, 0,48 ve 0,45 raporladı — herkese açık URL yok, bu yüzden yalnız anekdot olarak listeliyoruz.) | Aşağıdaki repo için DOĞRULANDI; Discord raporu ANEKDOT | [yodablocks/commitjev](https://github.com/yodablocks/commitjev) bunu ölçtüğünü bildiriyor; desen ve azaltımlar [`PATTERNS.md`](PATTERNS.md) içinde |
| State içine gömülü metin cevabı kaydırabilir (sahte otorite, gömülü talimat). | DOĞRULANDI | [Model jaggedness: adversarial content](https://docs.typesafe.ai/model-jaggedness/jev-1.13) |

## 3. Hız, maliyet ve isabet iddiaları

| İddia | Hüküm | Kaynak gerçekte ne diyor |
|---|---|---|
| "193,6× daha hızlı, 444,6× daha ucuz" | ÜRETİCİ İDDİASI | Rakamlar [TypeSafe'in lansman yazısında](https://typesafe.ai/blog/introducing-system-one-models-and-jev) (Diogo Almeida, 2026-09-15). Aynı yazı bu rakamların üreticinin seçtiği iş akışı örneklerinden geldiğini ve gerçek dünya kazanımlarının **üst ucunda** olmasının beklendiğini söylüyor; kendi çekincelerini listeliyor (demo seçimi, hakem model seçimi, eğitim dağılımı). Üreticinin verdiği genel aralık 20–200× daha hızlı, 40–400× daha ucuz. |
| Üreticinin "isabet" rakamları | ÜRETİCİ İDDİASI | Lansman yazısındaki isabet, gerçek zeminle uyum değil, **hakem modellerle uyum** anlamına geliyor (GPT-6 Astra ve Fable 5.1 ortalaması). [OrcaRouter'ın yazısı](https://www.orcarouter.ai/blog/jev-typesafe-system-one-what-we-know) üretici rakamlarını bağımsız olanlardan ayırıyor. |
| "%67,8 isabet, Sonnet 5 ile aynı seviyede" | BULUNAMADI | Birkaç videoda tekrarlanıyor; OrcaRouter %67,8 rakamını üreticinin iç benchmark'ına dayandırıyor, ama bu cümleyi üreticinin sayfasında bulamadık. İlgisiz bir %67,8 rakamı, [bağımsız bir kalibrasyon çalışmasında](https://github.com/Adilmp/does-jev-confidence-mean-anything) "her zaman hayır de" temel çizgisinin skoru olarak geçiyor. Bu ikisini karıştırmayın. |
| Bağımsız hız/maliyet kontrolü | DOĞRULANDI | [Every'nin testi](https://every.to/also-true-for-humans/mini-vibe-check-typesafe-s-jev-judged-everything-i-ve-written-in-0-7-seconds): Jev 7 yerleştirilmiş hatadan 6'sını yakaladı, Fable 5.1 7'sini de yakaladı; Jev geçiş başına yaklaşık 25× daha hızlı, maliyetin kabaca 1/580'i kadardı. İyi, kusursuz değil. |
| "Daha ucuz" otomatik değil | TARTIŞMALI | [rtrvr.ai'nin tarayıcı-ajan benchmark'ı](https://rtrvr.ai/blog/jev-browser-agent-benchmark) (Bhavani Kalisetty, 2026-09-16): bağlamı puanlamak için Jev kullanmak görevleri %31–43 hızlandırdı ama toplam maliyeti **artırdı** — LinkedIn görevinde %38, Amazon görevinde %51; bağlam puanlaması Jev harcamasının %78,7'siydi. Çok sayıda ucuz çağrı toplamda büyüyor. |
| Kodlama modelinden karar devretmek | TARTIŞMALI | [dnikolayev/typesafe-offload-bench](https://github.com/dnikolayev/typesafe-offload-bench): 100 sentetik örnekte bir kademeli (cascade) düzen süreyi %32–58, token'ı %52–62 kesti; yazarlar bunun fatura tasarrufu olmadığını ve kademeli modda dört modelin referans etiketlerle uyumu kaybettiğini belirtiyor. |

## 4. Kalibrasyon — 0,9 gerçekten %90 mı demek?

| Bulgu | Hüküm | Kaynak |
|---|---|---|
| Üretici, RLCD ("Reinforcement Learning for Calibrated Decisions") adlı bir eğitim yöntemi tanımlıyor; **hedefi** belirtilen %70'in gerçekte %70 oranında doğru olması. Üretici hiçbir kalibrasyon ölçümü yayımlamıyor (ECE, Brier skoru ya da güvenilirlik eğrisi yok). | ÜRETİCİ İDDİASI (tasarım hedefi, ölçülmüş sonuç değil) | [Lansman yazısı](https://typesafe.ai/blog/introducing-system-one-models-and-jev) |
| Bağımsız ölçüm 1: insan etiketlerine karşı 8.000 yargı. Olasılıklar sistematik olarak "evet"e kaymıştı — belirtilen ~%75'te, gerçek oran ~%10'du. Ham ECE 0,156–0,209; iki parametreli yeniden kalibrasyon bunun ~%96'sını giderdi. Sıralama kalitesi iyiydi (AUC 0,90–0,91). Yazarın çerçevelemesi: sıralama doğru, birim yanlış. | TARTIŞMALI | [Adilmp/does-jev-confidence-mean-anything](https://github.com/Adilmp/does-jev-confidence-mean-anything) |
| Bağımsız ölçüm 2: 662 prompt-injection mesajı — %96,5 isabet, ROC-AUC 0,9927, ECE 0,0588; model **düşük** güvenliydi (0,85 üstü her bant %100 doğruydu). | DOĞRULANDI (bağımsız, herkese açık külliyat) | [Gaurav-Gosain/jev-sec-bench](https://github.com/Gaurav-Gosain/jev-sec-bench) |
| Bağımsız ölçüm 3: araç-çağrısı injection tespiti, 0,061 $'a 1.942 istek — AUC 0,976 (InjecAgent), 1,000 (BIPIA e-posta), 0,993 (elle etiketlenmiş çağrılar). Yazarlar, Jev için kalibre edilmiş bir eşiğin aynı gateway arkasındaki genel modellere aktarılamayacağı konusunda uyarıyor. | DOĞRULANDI | [agent-chaperone/agent-chaperone](https://github.com/agent-chaperone/agent-chaperone) |
| Çıkarım: kalibrasyonun **yönü göreve bağlı**. Olasılığı iyi sıralanmış bir skor olarak ele alın ve eşikleri kendi etiketli verinizle kalibre edin. | BİZİM ÇIKARIMIMIZ | [Adilmp'ın çalışmasından](https://github.com/Adilmp/does-jev-confidence-mean-anything) ("evet"e doğru aşırı güvenli), [jev-sec-bench'ten](https://github.com/Gaurav-Gosain/jev-sec-bench) (düşük güvenli) ve [agent-chaperone'dan](https://github.com/agent-chaperone/agent-chaperone) (eşikler aktarılamıyor) çıkarıldı |
| API'deki "confidence" (güven), kazanan seçeneğin olasılığı değil, dağılımın ne kadar yoğunlaştığıdır. Bir score sorusunda, mükemmel anlamlı 1,9 skorunun yanında confidence 0,00 gördük (kütle iki bitişik basamağa bölünmüştü). Sabit bir confidence eşiği, score soruları için yanlış araçtır. | DOĞRULANDI | [TypeSafe dokümanı](https://docs.typesafe.ai/llms.txt); bunu kendi çağrımızda gördük, aynı soru tipini belgelenmiş API'ye karşı çağırarak tekrarlanabilir |

## 5. Üretici dışında kimsenin bilmediği

Model boyutu, mimarisi ve eğitim verisi açıklanmamıştır: ne [lansman yazısı](https://typesafe.ai/blog/introducing-system-one-models-and-jev) ne de [dokümantasyon](https://docs.typesafe.ai/llms.txt) bunları belirtiyor. "O(1)", "KV-cache darboğazını kaldırıyor" ya da belirli parametre sayıları gibi ifadeler yorum videolarında geçiyor ([`SOURCES.md`](SOURCES.md) içinde "video" altında listeli) ama bulabildiğimiz **hiçbir birincil kaynakta yok** — BULUNAMADI.

## 6. Kamuoyu tepkisi, iki yönlü

- Coşku: birkaç gün içinde yüzlerce herkese açık repo ([`REPOS.md`](REPOS.md)) ve en az sekiz derlenmiş liste ([`SOURCES.md`](SOURCES.md)).
- Şüphecilik: "Bir JSON sınıflandırıcı için 12 milyon görüntülenme mi? Evet, bir balonun içindeyiz" — [X'te Niels Rogge](https://x.com/NielsRogge/status/2100114968460820986) (gönderiyi doğrudan açamadık; alıntı arama sonuçları üzerinden doğrulandı).
- Birkaç grup, açık modellerden seçenek olasılıklarını okuyarak "yerel bir Jev" yeniden kurdu; ikisi gerçek modele karşı benchmark yaptı — bkz. `text-generation-experiment` ve `eval-benchmark` [kategorileri](categories/).

## Sonuç

Bu paragraf yukarıdaki 1–4. bölümlerin sentezimizdir; içindeki her olgu orada kaynaklanır. Jev; tipli seçimler olarak ifade edebileceğiniz, sınırlı bir state üzerindeki sorular için hızlı, ucuz, iyi sıralanmış bir **skorlayıcı**dır. Doğrulanan ([§1](#1-ne-olduğu), [§2](#2-halüsinasyon-göremez-gerçekte-ne-demek)): arayüz, fiyat, hız sınıfı, şema garantisi, üreticinin kendi zayıflık listesi. Doğrulanmayan ([§3](#3-hız-maliyet-ve-isabet-iddiaları), [§4](#4-kalibrasyon--09-gerçekten-90-mı-demek)): olasılıklarının sizin göreviniz için kalibre olduğu, sizin hattınızda uçtan uca daha ucuz olduğu ve herhangi bir manşet çarpanı. Karar makinesini onun etrafında kurun — eşikler, bir "belirsiz" bandı, eşiğe yakınken ortalama alma, bir yedek (fallback), bir günlük — ve kendi etiketli verinizle ölçün.
