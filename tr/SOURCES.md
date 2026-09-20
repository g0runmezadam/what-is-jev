<!-- GENERATED — do not edit; run tools/build.py -->
[English](../SOURCES.md) | Türkçe

# Kaynaklar

Bu depodaki her iddia bunlardan birine dayanır. Her satır bir bağlantı taşır; bağlantısız satır yazılmaz.

## Resmî belgeler

| Kaynak | Yazar | Tarih | Güven | Durum | Not |
|---|---|---|---|---|---|
| [Introducing System One Models and Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) | Diogo Almeida / TypeSafe | 2026-09-15 | 5 | read | TypeSafe'in System One modelleri ve Jev için kendi lansman yazısı: hız/maliyet iddiaları, workflow eval'leri ve satıcı yanlılığını kabul eden kendi nüans notları. |
| [TypeSafe documentation bundle \(llms.txt\)](https://docs.typesafe.ai/llms.txt) | TypeSafe | 2026-09-19 | 5 | read | Sağlayıcının kendi belgesi: API, soru tipleri, güvenin tanımı, bilinen zayıflıklar, cookbook. 2026-09-19'da okundu. |
| [Model jaggedness — jev-1.13](https://docs.typesafe.ai/model-jaggedness/jev-1.13) | TypeSafe |  | 5 | read | TypeSafe'in kendi 'bilinen zayıflıklar' sayfası: literal okuma, matematik, tarih, dolaylı ifade, düşmanca içerik, bağlam sınırları — 'Jev bir hesap makinesi değildir.' |
| [Jev — Vercel AI Gateway model page](https://vercel.com/ai-gateway/models/jev) | Vercel | 2026-09-19 | 5 | read | Vercel'in kendi Jev model sayfası: fiyat $0,042/1M girdi token, çıktı 0 token'a sabit, 32k bağlam penceresi, AI Gateway kataloğunda. |
| [gateway-evaluation-model.ts \(vercel/ai SDK source\)](https://github.com/vercel/ai/blob/main/packages/gateway/src/gateway-evaluation-model.ts) | Vercel |  | 5 | read | vercel/ai SDK'sında Gateway'in evaluation-model istemcisini uygulayan kaynak dosya: Jev'i çağırmak için kullanılan istek biçimi, başlıklar ve uç nokta. |

## Kendi ölçümlerimiz

| Kaynak | Yazar | Tarih | Güven | Durum | Not |
|---|---|---|---|---|---|
| [Our own System-1 API calls](https://api.typesafe.ai/v1/systemone) | this repository | 2026-09-10 | 5 | read | System-1 uç noktasına kendi çağrılarımız: gecikme, yanıt biçimi, olasılığın nasıl oynadığı. Bize söylenen değil, ölçtüğümüz sayılar. |

## Bağımsız testler

| Kaynak | Yazar | Tarih | Güven | Durum | Not |
|---|---|---|---|---|---|
| [does-jev-confidence-mean-anything](https://github.com/Adilmp/does-jev-confidence-mean-anything) | Adilmp |  | 4 | read | 8.000 yargı üzerinde bağımsız kalibrasyon testi: Jev'in beyan ettiği güven kalibre değil \(ECE 0,16-0,21\) ama sıralama başarısı \(AUC ~0,90\) iyi. |
| [agent-chaperone](https://github.com/agent-chaperone/agent-chaperone) | agent-chaperone | 2026-09-19 | 4 | read | Jev'i ajan güvenlik katmanı olarak test eden bağımsız çalışma: 1.942 istekte prompt-injection ve riskli araç çağrısı tespitinde yüksek AUC \(0,976-1,000\). |
| [typesafe-offload-bench](https://github.com/dnikolayev/typesafe-offload-bench) | dnikolayev | 2026-09-17 | 4 | read | Bağımsız cascade ölçümü: görevleri büyük kodlama modellerinden önce Jev'den geçirmek süreyi %32-58, token'ı %52-62 azalttı; yazarlar sınırlamaları açıkça belirtiyor. |
| [Mini vibe check: TypeSafe's Jev judged everything I've written in 0.7 seconds](https://every.to/also-true-for-humans/mini-vibe-check-typesafe-s-jev-judged-everything-i-ve-written-in-0-7-seconds) | Every | 2026-09-16 | 4 | read | Every'nin bağımsız testi: Jev 12 pasajdaki 7 kasıtlı hatanın 6'sını 0,7 sn medyan sürede yakaladı; Claude Fable 7/7'sini ama daha yavaş yakaladı. |
| [jev-sec-bench](https://github.com/Gaurav-Gosain/jev-sec-bench) | Gaurav Gosain | 2026-09-16 | 4 | read | Bağımsız güvenlik ölçümü: Jev prompt-injection tespitinde %96,5 doğruluk \(ROC-AUC 0,99\) gösteriyor ve aşırı güvenli değil, düşük güvenli çıkıyor. |
| [Jev browser-agent benchmark](https://www.rtrvr.ai/blog/jev-browser-agent-benchmark) | Bhavani Kalisetty / rtrvr.ai | 2026-09-16 | 4 | read | rtrvr.ai'nin kendi tarayıcı-ajan ölçümü: Jev görevleri %31-43 hızlandırdı ama bağlam-skorlama çağrıları pahalı olduğu için toplam maliyeti %38-51 artırdı. |

## Yazılar

| Kaynak | Yazar | Tarih | Güven | Durum | Not |
|---|---|---|---|---|---|
| [TypeSafe AI Emerges From Stealth With $40M in Funding With New Model for Composable AI](https://www.hpcwire.com/aiwire/2026/09/16/typesafe-ai-emerges-from-stealth-with-40m-in-funding-with-new-model-for-composable-ai/) | AIwire | 2026-09-16 | 3 | read | Finansman: DCVC liderliğindeki 40 milyon dolarlık tohum turu ve kurucu ekip haberi. Yalnız şirket bilgisi için kullanıldı, model iddiaları için değil. |
| [TypeSafe AI Raises $40M in Seed Funding](https://www.finsmes.com/2026/09/typesafe-ai-raises-40m-in-seed-funding.html) | FinSMEs | 2026-09-16 | 3 | read | Finansman: aynı 40 milyon dolarlık turu bildiren ikinci bağımsız yayın; rakamın yayınlar arasında tutarlı olduğunu göstermek için listelendi. |
| [Jev : Reviews, Price, Info &amp; 30 Alternatives AI Tools \| 2026 - AIxploria](https://www.aixploria.com/en/jev-typesafe-ai/) | AIxploria |  | 2 | read | AIxploria dizin sayfası, Jev'in primitiflerini ve fiyatını TypeSafe sitesinden özetliyor; eksiler: bekleme listesi, yalnız metin girdisi, şimdilik yalnız satıcı ölçütleri. |
| [What is Jev AI](https://medium.com/data-science-in-your-pocket/what-is-jev-ai-b8294d980001) |  |  | 2 | unavailable | Kaynak listesindeki Jev hakkında bir Medium yazısı; inceleme sırasında sayfa çekilemedi, içeriği doğrulanamadı. |
| [Jev: TypeSafe's Decision Model, Speed and Cost Explained](https://www.orcarouter.ai/blog/jev-typesafe-system-one-what-we-know) | Magnus Corvin / OrcaRouter | 2026-09-16 | 2 | read | OrcaRouter blogu, Jev'in hız/maliyet/doğruluk rakamlarında TypeSafe'in satıcı iddialarını Every'nin bağımsız sayılarından ayırıyor; kanıtlanmamış kalibrasyon iddiasını işaretliyor. |

## Videolar

| Kaynak | Yazar | Tarih | Güven | Durum | Not |
|---|---|---|---|---|---|
| [Avenox — Jev video](https://www.youtube.com/watch?v=0f4TJMg7jLA) | Avenox |  | 4 | read | Jev üzerine Türkçe bir açıklama/kullanım alanları videosu, güven 4 olarak değerlendirildi \(tanıtım/açıklama videosu düzeyinde\): Jev'in yeri, ekonomisi, kullanım alanları ve nasıl kandırılabileceğini anlatıyor. |
| [🟢 Learn to Build a Airtable Clone with AI! \| Beginner Series Ep #16 \(B2B, Billing, AI Agents, MCP\)](https://www.youtube.com/watch?v=rz5y7nfmvis) |  |  | 2 | irrelevant | Alakasız Airtable klonu eğitim videosu; anahtar kelime taramasında Jev, TypeSafe veya System One hiç geçmiyor. |
| [ChatGPT Co-Founder Launches 200x Faster AI: Matches Top Models](https://www.youtube.com/watch?v=EOzu25Mb0H8) |  |  | 2 | read | Bağımsız haber kanalı TypeSafe'in kendi rakamlarını \(4 iç iş akışında 193,6x hızlı, 444,6x ucuz\) tekrarlıyor; 'halüsinasyon yok' iddiasının yalnız şema garantisi olduğunu belirtiyor. |
| [ChatGPT Co-Inventor Launches Jev, A Frontier Model That Never Generates Text](https://www.youtube.com/watch?v=Qz9gVzqcRhU) |  |  | 2 | read | Kısa bağımsız haber özeti, Jev'i hiç metin üretmeyen, yalnız tipli kararlar veren bir model olarak tanımlıyor; TypeSafe'in kendi hız/fiyat rakamlarını tekrarlıyor. |
| [ChatGPT Images 2.5 Is INSANE: OpenAI Just Changed AI Image Generation](https://www.youtube.com/watch?v=xNSX8ZHpTpM) |  |  | 2 | irrelevant | OpenAI görüntü üretimiyle ilgili alakasız video; Jev, TypeSafe veya System One hiç geçmiyor. |
| [Coding a Cure for Cancer using AI with Dr Leon Chlon \(ex-Facebook, Harvard, Cambridge &amp; MIT\) EP.9](https://www.youtube.com/watch?v=emJq8JNRzd4) | Dr Leon Chlon |  | 2 | irrelevant | Kanser araştırmasında yapay zeka üzerine alakasız röportaj; tek yanlış eşleşme 'Geoffrey Hinton', Jev veya TypeSafe değil. |
| [Gemini 3.8 Flash Analysis](https://www.youtube.com/watch?v=jV4po1B7Bwo) |  |  | 2 | irrelevant | Google'ın Gemini 3.8 Flash model kartını inceleyen alakasız video; Jev, TypeSafe veya System One hiç geçmiyor. |
| [Gemini 3.8 Live and Jev Are Shaking Things Up](https://www.youtube.com/watch?v=4SqD_o-EAi8) | Daily AI Show \(Brian, Andy, Gareth\) |  | 2 | read | AI podcast'i TypeSafe'in kendi duyurusunu ve demolarını \(Doom, wiki-race\) okuyor; sunucular Jev'i henüz kendileri denemediklerini belirtip temkinli kalıyor. |
| [Gestión del liderazgo con tecnología \| #ForoUNIR](https://www.youtube.com/watch?v=FHOd9yILXXQ) |  |  | 2 | irrelevant | Alakasız İspanyolca liderlik/teknoloji konferansı konuşması; Jev, TypeSafe veya System One hiç geçmiyor. |
| [How I'd Learn AI Engineering From Zero in 2026 \(1 hour masterclass\)](https://www.youtube.com/watch?v=uSkm-2eb4Xk) |  |  | 2 | irrelevant | Alakasız AI mühendisliği öğrenme yol haritası videosu; anahtar kelime taramasında Jev, TypeSafe veya System One hiç geçmiyor. |
| [I tried TypeSafe's System One Model: Jev](https://www.youtube.com/watch?v=CcmqPS6q9Gw) | Joe Maddalone |  | 2 | read | Bağımsız geliştiricinin kendi testi: video transkriptlerini 3 soru tipiyle Jev'e verdi; bir soruda sıfır güvenle cevap veremedi, açık bir başarısızlık örneği. |
| [Jev AI Is INSANE… 193× Faster Than LLMs?!](https://www.youtube.com/watch?v=JZknBu3u8C0) |  |  | 2 | read | TypeSafe'in kendi demo/grafiklerine nispeten eleştirel bağımsız bakış; '%0 yapılandırılmış çıktı hatası' rakamının hiç ölçülmediğini işaretliyor. |
| [Jev AI: Build &amp; Automate ANYTHING!](https://www.youtube.com/watch?v=INB6OeGaqps) | Julian Goldie |  | 2 | read | Tanıtım kanalı başka geliştiricilerin Jev demolarını \(sınıflandırma, lead skorlama, tarayıcı otomasyonu\) ve doğrulanmamış bir Claude Code bağlam sıkıştırma iddiasını aktarıyor. |
| [Jev AI Just Changed AI Agents Forever](https://www.youtube.com/watch?v=UbMdpR8Jlhc) |  |  | 2 | read | Reklam ağırlıklı kanal, doğrulanmamış üçüncü taraf demo rakamlarını \(e-posta/lead sınıflandırma, tarayıcı otomasyonu\) aktarıyor; Jev'in alan adını değil yalnız soru metnini gördüğünü belirtiyor. |
| [Jev AI: How it works for SEO?](https://www.youtube.com/watch?v=OX7WZN5snIs) |  |  | 2 | read | Bağımsız bir SEO uygulayıcısının iç bağlantı ve niyet sınıflandırma için Jev denemesi; sonuçların kanıtlanmış doğru olmadığını tekrar tekrar vurguluyor. |
| [I built a Jev Computer Use Agent, Its INSANE](https://www.youtube.com/watch?v=vSzde5be5XE) |  |  | 2 | unavailable | Transkript teknik detay içermeyen tek cümlelik bir duyuru; Jev'in davranışına dair gerçek bir kaynak olarak değerlendirilemeyecek kadar kısa. |
| [Jev-Durchbruch: Die Architektur, die kein LLM mehr ist](https://www.youtube.com/watch?v=YsWvFYqouFY) |  |  | 2 | read | Jev'in kısa bir bölüm olduğu Almanca AI haber özeti; teknik detay az, kaynağı belirtilmeyen '200 kata kadar' hız iddiasını tekrarlıyor. |
| [Jev explained in 7min..](https://www.youtube.com/watch?v=vj7hysh0mOI) |  |  | 2 | read | Bağımsız analist, Jev'in asıl farkının gecikme olduğunu, ham yeteneğin olmadığını savunuyor; benzer bir şey yaptığı iddia edilen kaynak gösterilmemiş bir açık model bahsediyor. |
| [Jev for AI Agents: I Tested it with rtrvr.ai for browser automation](https://www.youtube.com/watch?v=JsNQwFB9N1Q) | rtrvr.ai \(Retriever\) team |  | 2 | read | rtrvr.ai ekibinin videodaki kendi A/B testi: Jev tarayıcı-ajan görevlerini hızlandırdı ama toplam maliyeti artırdı, olağandışı dürüst olumsuz bir bulgu. |
| [Jev is HERE. How to use it](https://www.youtube.com/watch?v=4mTLpuQpB80) | Ryan Vogel; Greg |  | 2 | read | Bağımsız erken kullanıcı röportajı: canlı e-posta sınıflandırma demosu \(1.700 e-posta\); Jev'in bir Bitcoin alım-satım sinyali testinde iyi performans göstermediğini açıkça söylüyor. |
| [Jev From TypeSafe is a New Class of AI Model that is FAST and CHEAP - But There is a Caveat!](https://www.youtube.com/watch?v=qdji39XXgEY) | Tech Nibble |  | 2 | read | Bağımsız CLI demosu somut Jev hatalarını gösteriyor: yüksek beyan edilen güvene rağmen bir asallık testinde ve bir mantık bilmecesinde yanlış cevap. |
| [Jev - The Ultimate Classification Model?](https://www.youtube.com/watch?v=X117w2Rark8) |  |  | 2 | read | OpenRouter üzerinden sınıflandırma, duygu analizi, injection ve araç seçimi görevlerini kapsayan bağımsız demo; mimari makale veya diyagram olmadığını açıkça belirtiyor. |
| [Jev by TypeSafe AI: Jev vs LLMs - Parallel Sampling, Lower Latency, and Typed Outputs](https://www.youtube.com/watch?v=JQFNpX1w6vY) |  |  | 2 | read | TypeSafe'in kendi RLCD çerçevesini ve rakamlarını tekrarlayan kurumsal tonlu açıklama videosu; '%0 halüsinasyon'un yalnız şema geçerliliği anlamına geldiğini açıkça belirtiyor. |
| [Master 95% of JEV AI in 7 Minutes](https://www.youtube.com/watch?v=RzCHlj95Ons) | Kev |  | 2 | read | Tanıtım amaçlı no-code kanal, lead skorlama ve bir bilgisayar-kullanım aracı gösteriyor; tamamen olumlu ton, hiçbir zayıflık tartışılmıyor. |
| [MCP for Performance Testing - Day 1: Introduction &amp; Fundamentals](https://www.youtube.com/watch?v=O8pFJFc21Eo) |  |  | 2 | irrelevant | Alakasız MCP performans testi eğitim videosu; anahtar kelime taramasında Jev, TypeSafe veya System One hiç geçmiyor. |
| [System One模型Jev​ \| Diogo Almeida \| TypeSafe AI \| RLCD \| RLHF \| 结构化输出 \| 不会聊天的模型 \| 丹尼尔卡尼曼 \| 杰文斯悖论](https://www.youtube.com/watch?v=xJ1GrKDpgm4) | 大飞/最佳拍档 |  | 2 | read | Adı verilen şüphecileri \(Niels Rogge, Harsha Gundala\) ve TypeSafe'in 40M$'lık finansman turunu aktaran eleştirel Çince haber videosu; incelenen en kaynak-şeffaf video. |
| [System 1 Models Jev Explained: 200ms AI Decisions, Zero Token Streaming](https://www.youtube.com/watch?v=6RdpGVfqd4A) |  |  | 2 | read | Dengeli bağımsız açıklama videosu, TypeSafe'in kendi lansman notlarının ölçüt sınırlamalarını itiraf etmesinin bir lansman yazısı için nadir olduğunu vurguluyor. |
| [What Is Jev, the New Model From TypeSafe AI? \| Tech Brew Ride Home Podcast](https://www.youtube.com/watch?v=Ipom6c1fcP0) | Tech Brew Ride Home Podcast |  | 2 | read | Teknoloji haber podcast'i, bir Register makalesini Jev hakkında birebir okuyor; Diogo Almeida'dan doğrudan alıntı ve 40M$ finansman rakamı içeriyor. |
| [wtf is jev?](https://www.youtube.com/watch?v=QbYBRjOaGOo) | CJ \(Syntax.fm\) |  | 2 | read | Syntax.fm sunucusu ve Sentry mühendisinin kendi somut demoları: Jev üzerine kurulu LLM'siz bir sesli asistan ve bir Slack botu model yönlendiricisi. |

## Topluluk listeleri

| Kaynak | Yazar | Tarih | Güven | Durum | Not |
|---|---|---|---|---|---|
| [awesome-jev](https://github.com/AnotiaWang/awesome-jev) | AnotiaWang |  | 3 | read | Jev kullandığı etiketlenen projelerin topluluk dizini; keşif listesi, model hakkında bir iddiaya kanıt değil. |
| [awesome-jev-by-typesafe](https://github.com/Anil-matcha/awesome-jev-by-typesafe) | Anil-matcha |  | 3 | read | Jev kullandığı etiketlenen projelerin topluluk dizini; keşif listesi, model hakkında bir iddiaya kanıt değil. |
| [awesome-jev directory](https://awesomejev.vercel.app/) | valentynkit | 2026-09-19 | 3 | read | Jev üzerine kurulu projelerin topluluk dizini. Keşif listesi olarak işe yarar; model hakkındaki bir iddiaya kanıt değildir. |
| [awesome-jev](https://github.com/fatwang2/awesome-jev) | fatwang2 |  | 3 | read | Jev kullandığı etiketlenen projelerin topluluk dizini; keşif listesi, model hakkında bir iddiaya kanıt değil. |
| [awesome-jev-projects](https://github.com/logicrw/awesome-jev-projects) | logicrw |  | 3 | read | Jev kullandığı etiketlenen projelerin topluluk dizini; keşif listesi, model hakkında bir iddiaya kanıt değil. |
| [awesome-jev-typesafe](https://github.com/valentynkit/awesome-jev-typesafe) | valentynkit |  | 3 | read | Jev/TypeSafe kullandığı etiketlenen projelerin topluluk dizini; keşif listesi, model hakkında bir iddiaya kanıt değil. |
| [Awesome-jev-use](https://github.com/AiPersonacademy/Awesome-jev-use) | AiPersonacademy |  | 3 | read | Jev kullandığı etiketlenen projelerin topluluk dizini; keşif listesi, model hakkında bir iddiaya kanıt değil. |
| [awesome-jev](https://github.com/yibie/awesome-jev) | yibie |  | 3 | read | Jev kullandığı etiketlenen projelerin topluluk dizini; keşif listesi, model hakkında bir iddiaya kanıt değil. |
| [awesome-typesafe](https://github.com/AbdelStark/awesome-typesafe) | AbdelStark |  | 3 | read | Jev/TypeSafe kullandığı etiketlenen projelerin topluluk dizini; keşif listesi, model hakkında bir iddiaya kanıt değil. |
| [GitHub topic: jev](https://github.com/topics/jev) | GitHub | 2026-09-19 | 3 | read | GitHub'ın 'jev' konu sayfası, repo keşif kaynağı olarak kullanıldı; etiket serbest olduğundan bazı repolar TypeSafe'in Jev'iyle ilgisiz olabilir. |

## Araçlar

| Kaynak | Yazar | Tarih | Güven | Durum | Not |
|---|---|---|---|---|---|
| [Nasrallah-AL/jev-cli](https://github.com/Nasrallah-AL/jev-cli) | Nasr Shaer \(Nasrallah-AL\) |  | 3 | read | jev-cli \(jevctl\) için GitHub kaynağı: MIT lisanslı, tek bir sıkıştırma hook'lu Claude Code eklentisi içeriyor, MCP sunucusu yok, belgelenmiş telemetri yok. |
| [Jev CLI \(jevctl\) product page](https://jevcli.vectorz.app/) | Nasr Shaer \(Nasrallah-AL\) |  | 3 | read | jevctl için üçüncü taraf CLI ürün sayfası, açıkça 'TypeSafe'e bağlı değil'; Jev API'sini classify, route, verify gibi komutlarla sarmalıyor. |
| [jevctl — npm](https://www.npmjs.com/package/jevctl) | Nasr Shaer \(Nasrallah-AL\) |  | 3 | read | Üçüncü taraf Jev CLI'ı jevctl'nin npm paket sayfası; npm i -g jevctl ile kurulur, Node.js 20.12+ gerektirir. |

## Topluluk mesajları

| Kaynak | Yazar | Tarih | Güven | Durum | Not |
|---|---|---|---|---|---|
| ["12 million views for a JSON classifier?" \(X post\)](https://x.com/NielsRogge/status/2100114968460820986) | Niels Rogge | 2026-09-15 | 3 | read | HuggingFace araştırmacısı Niels Rogge'un Jev lansmanına açık yanıtı; bir yapılandırılmış-çıktı sınıflandırıcının bu kadar ilgi görmesini sorguluyor. |
