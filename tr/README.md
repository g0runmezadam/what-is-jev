[English](../README.md) | **Türkçe**

# Jev nedir?

TypeSafe AI'nin "System One" karar modeli **Jev** hakkında kaynaklı ve eleştirel bir araştırma dosyası; yanında da insanların onunla gerçekte ne kurduğunu gösteren, sabit bir ölçekle puanlanmış ekosistem haritası.

Jev metin yazmaz. Ona bir durum (state) ve tipli sorular verirsiniz (**choice** = seçim, **score** = skor, **noul** = evet/hayır); karşılığında olasılık döner. Bu onu ucuz, hızlı ve yazılıma bağlaması kolay bir araç yapar — abartılması da bir o kadar kolaydır. Bu depo üç soruyu heyecanla değil kanıtla cevaplamaya çalışır:

1. **Jev gerçekte nedir?** Hangi iddia doğrulanmış, hangisi üreticinin pazarlama rakamının tekrarı, hangileri birbiriyle çelişiyor → [`FINDINGS.md`](FINDINGS.md)
2. **İnsanlar onunla ne kuruyor?** 785 herkese açık GitHub deposu, hepsi aynı sabit ölçekle puanlandı → [`REPOS.md`](REPOS.md), en iyiler [`TOP.md`](TOP.md), [kategoriye göre](categories/) gezilebilir
3. **Hangi tasarım desenleri tekrar ediyor, hangileri ölçümle destekli?** → [`PATTERNS.md`](PATTERNS.md)

> **Buradaki her şey herkese açık kaynaklardan derlendi** — resmi doküman, herkese açık GitHub depoları, herkese açık videolar, yazılar ve gönderiler — ve tekrarlayabilmeniz için nasıl yaptığımızı anlattığımız kendi API çağrılarımız. **Her iddia ve her kayıt kaynağına bağlantı verir.** Özel ya da ücretli hiçbir malzeme kullanılmadı; üçüncü tarafların içeriğini yeniden yayımlamıyoruz: kopyasını değil, bağlantısını ve bizim değerlendirmemizi bulursunuz. Tüm kaynakların URL'leri ve güven düzeyleriyle tam listesi: [`SOURCES.md`](SOURCES.md).

TypeSafe AI ile bir bağımız yoktur. Bu bağımsız bir araştırmadır.

**Bu depo sürekli güncellenir.** Her gün yeni Jev depoları çıkıyor; bunları topluyor, aynı ölçekle puanlıyor, en üst sınıfı yeniden denetliyor ve doğrulandıkça yeni kaynakları ve bulguları ekliyoruz. Aşağıdaki "Veri tarihi" sayıların ne kadar taze olduğunu gösterir; her güncellemede neyin değiştiği [`CHANGELOG.md`](CHANGELOG.md) dosyasında listelenir.

<!-- STATS:START -->
| Sayı | Değer |
|---|---|
| Repo | 909 |
| Jev çağırıyor | yes 606 · no 270 · unclear 33 |
| Sınıflar | A 271 · B 281 · C 357 |
| Denetlenmiş | 283 |
| Kaynak | 88 |
| Veri tarihi | 2026-09-20 |

**En çok kategori**

- [Diğer](categories/other.md) — 183
- [Sınıflandırma ve triyaj](categories/classification-triage.md) — 101
- [SDK'lar ve istemciler](categories/sdk-client.md) — 82
- [Değerlendirme ve benchmark](categories/eval-benchmark.md) — 78
- [Ajan kapıları](categories/agent-gate.md) — 58
- [Kod inceleme hook'ları](categories/code-review-hook.md) — 53
- [Listeler ve dizinler](categories/list-directory.md) — 52
- [Oyunlar ve demolar](categories/game-demo.md) — 51
<!-- STATS:END -->

## Bu depo nasıl okunur

| Aradığınız… | Bakacağınız yer |
|---|---|
| "Jev nedir?" sorusunun kısa, kaynaklı cevabı | [`FINDINGS.md`](FINDINGS.md) |
| Kullandığımız her kaynak, bağlantısı ve güven düzeyiyle | [`SOURCES.md`](SOURCES.md) |
| Depoları nasıl puanladık, yöntemin sınırları neler | [`METHODOLOGY.md`](METHODOLOGY.md), [`data/rubric.md`](data/rubric.md) |
| Kategoriye göre en güçlü projeler | [`TOP.md`](TOP.md) |
| Bir kategorideki tüm depolar (ajan kapıları, yönlendiriciler, compaction, …) | [`categories/`](categories/) |
| Kanıtlı, tekrar eden tasarım desenleri | [`PATTERNS.md`](PATTERNS.md) |
| Makine-okur veri | [`data/repos.jsonl`](../data/repos.jsonl), [`data/sources.jsonl`](../data/sources.jsonl), şema [`data/SCHEMA.md`](../data/SCHEMA.md) |
| Bu depoyu kendi yapay zekâ asistanınıza vermek | [`llms.txt`](../llms.txt) ve [`AGENTS.md`](../AGENTS.md) |
| Depo eklemek ya da bir kaydı düzeltmek | [`CONTRIBUTING.md`](../CONTRIBUTING.md) |

## Kaynak güven sırası

Kaynaklar çeliştiğinde şu sırayı izliyoruz — ve bunu her bulgunun yanında belirtiyoruz:

1. TypeSafe'in resmi dokümanı ve kendi gerçek API çağrılarımız
2. Sayılarını ve yöntemini yayımlayan bağımsız testler
3. Topluluk depoları ve herkese açık mesajlar
4. Lansman ve tanıtım videoları (çoğu üreticinin rakamlarını tekrar eder)
5. İkincil özetler (yapay zekâ üretimi olanlar dahil) — **asla kanıt olarak kullanılmaz**

## Dürüst sınırlar

- Depo puanları, **yazılı bir ölçeğe göre bir dil modelinin yargısıdır**; en üst sınıf ikinci bir denetimden geçirildi. Projelerin kendisinin benchmark'ı değildir.
- Depoların çoğunda açıklamayı, üstveriyi ve **README'nin ilk 12.000 karakterini** okuduk — kodu değil. Bir proje README'sinden daha iyi ya da daha kötü olabilir.
- "Jev'i çağırıyor" demek, README ya da kodda Jev / System One API'sine gerçek bir çağrı görüldü demektir. `jev` serbest bir GitHub etiketidir; bu etiketi taşıyan pek çok deponun TypeSafe'in modeliyle ilgisi yoktur — onları silmek yerine öyle işaretledik.
- **Yıldız sayısı hiçbir puanı etkilemez.**
- Jev çağrıdan çağrıya deterministik değildir; üreticinin doğruluk rakamları gerçek doğruluğu değil hakem modellerle uyumu ölçer. Ayrıntı ve bağlantılar [`FINDINGS.md`](FINDINGS.md) içinde.
- Ekosistem her gün değişiyor. Her kayıt, puanlandığı tarihi ve kullanılan ölçek sürümünü taşır.

## Güncel kalmak

Her gün yeni Jev depoları çıkıyor. `tools/update.py` bunları (GitHub etiket araması + elle gönderilen bağlantılar) hiçbir model çağırmadan bulur; yeni kayıtlar aynı ölçekle puanlanır ve `tools/build.py` tarafından birleştirilir — bu betik iki dildeki bütün liste sayfalarını `data/repos.jsonl` dosyasından yeniden üretir. Üretilen sayfalar elle düzenlenmez. Silinen depoların kaydı tutulur ve `gone` diye işaretlenir.

## Diller

Varsayılan dil İngilizcedir. Tam Türkçe sürüm [`tr/`](README.md) altındadır. İkisi de aynı veriden üretildiği için birbirinden kopamaz.
