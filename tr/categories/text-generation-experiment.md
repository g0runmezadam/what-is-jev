<!-- GENERATED — do not edit; run tools/build.py -->
[English](../../categories/text-generation-experiment.md) | Türkçe

# Metin üretimi denemeleri

Bu kategoride 16 repo; önce sınıf, sonra puan sırasıyla.

[Bütün repolar](../REPOS.md)

| Repo | Sınıf | Toplam | Jev çağırıyor | Ne yapıyor | Kanıt |
|---|---|---|---|---|---|
| [rhighs/jev-code](https://github.com/rhighs/jev-code) | A | 10 | yes | LLM anlamlı alt-problemleri/kod seçeneklerini öneriyor, Jev onaylıyor/seçiyor/inceliyor; LLM asla plan onaylayamaz, araç seçemez, dosya yazamaz | [kanıt](https://github.com/rhighs/jev-code#readme) |
| [BunsDev/typesafe-ai-playground](https://github.com/BunsDev/typesafe-ai-playground) | A | 9 | yes | Topluluk Jev playground'u: extraction, ask-gate triage, tool-router, reranker, PR-review, AST governance gibi çok sayıda gerçek Jev demosu | [kanıt](https://github.com/BunsDev/typesafe-ai-playground) |
| [kyle-pena-nlp/jevchat](https://github.com/kyle-pena-nlp/jevchat) | B | 10 | yes | Jev'i, alfabeden bir sonraki karakterin ne oldugunu tekrar tekrar sorarak karakter karakter bir sohbet botuna donusturur; birden fazla ornekleme stratejisi \(ikiye bolme, kova, isin arama\) icerir ve maliyetini kendisi 'pratik degil' diye tanimlar. | [kanıt](https://github.com/kyle-pena-nlp/jevchat#readme) |
| [MM-sheng/jevspeak](https://github.com/MM-sheng/jevspeak) | B | 10 | yes | Uretici LLM kullanmadan, ~13 paralel Jev karariyla semantik IR uretip deterministik dilbilgisi derleyicisiyle cumleye ceviren konusma motoru. | [kanıt](https://github.com/MM-sheng/jevspeak#readme) |
| [pcarrier/skibidu](https://github.com/pcarrier/skibidu) | B | 9 | yes | Jev'i düğüm düğüm AST kurdurup her alt-ağaca onay isteyen Scheme kod-üretim deneyi; paylaşan kişi 'tamamen elverişsiz' bulgusunu paylaştı | [kanıt](https://github.com/pcarrier/skibidu#readme) |
| [rivianpratama/JevPixelArt](https://github.com/rivianpratama/JevPixelArt) | B | 9 | yes | Jev her piksel kanalını Score sorusuyla belirliyor; düz dağılımı 'sharpen' ile keskinleştirip, tek seferlik kompozisyon sorularını her isteğe enjekte ederek paylaşılan bağlam eksikliğini telafi ediyor | [kanıt](https://github.com/rivianpratama/JevPixelArt#readme) |
| [wei-b0/gram-render](https://github.com/wei-b0/gram-render) | B | 9 | yes | Telegram botları için üretici arayüz: Jev asla metin yazmaz, yalnız veriden türetilen aday yapılar arasından seçim yapar \(hangi görünüm, hangi sıra\). | [kanıt](https://github.com/wei-b0/gram-render) |
| [dani1005/book-aurora](https://github.com/dani1005/book-aurora) | B | 8 | yes | Romanı Jev ile pasaj başına 10 paralel duygu skoru ile 'okuyup' renk şeridi çizen görselleştirme; hedge-retry ve OpenRouter/native ikili sağlayıcı desteği var | [kanıt](https://github.com/dani1005/book-aurora) |
| [finetuningsingh/jev-chatbot](https://github.com/finetuningsingh/jev-chatbot) | B | 8 | yes | Yalnız choice sorusu yanıtlayan Jev'i kelime kelime metin üretimine dönüştüren 7 farklı yöntemi \(word tree, scoring, letter-first vb.\) karşılaştıran deney | [kanıt](https://github.com/finetuningsingh/jev-chatbot#readme) |
| [chrismoseley/jev-extraction-marker-recovery](https://github.com/chrismoseley/jev-extraction-marker-recovery) | B | 7 | yes | OCR'da düzleşmiş dipnot/üstsimge işaretlerini regex-bulucu + Jev \(Noul+Choice\) ile kurtaran script | [kanıt](https://github.com/chrismoseley/jev-extraction-marker-recovery) |
| [replynodes/jev-web-analyzer](https://github.com/replynodes/jev-web-analyzer) | B | 7 | yes | Bir SaaS web sitesini ilk-ziyaretçi gözünden 10 soruyla Jev ile değerlendiren demo; SSRF'e karşı sıkı URL/DNS filtreleme, sayfa içeriği 'güvenilmez veri, talimat değil' ilkesiyle işleniyor | [kanıt](https://github.com/replynodes/jev-web-analyzer#readme) |
| [florian-hoenicke/jev-gpt](https://github.com/florian-hoenicke/jev-gpt) | C | 6 | yes | Kelime türü→WordNet kategorisi→embedding grubu→kelime→sıralama zincirli choice sorularıyla metin üreten deney \(~400 çağrı/prompt\) | [kanıt](https://github.com/florian-hoenicke/jev-gpt#readme) |
| [tylerjharden/harden-jev-decides](https://github.com/tylerjharden/harden-jev-decides) | C | 6 | yes | Bir yayın için hangi proje fikrinin canlı MVP olacağına Jev'in tek istekte ağırlıklı puanlarla karar verdiği eğlence panosu | [kanıt](https://github.com/tylerjharden/harden-jev-decides#readme) |
| [carlaiau/readwithjev](https://github.com/carlaiau/readwithjev) | C | 5 | yes | Roman okurken Jev ile cümle bazlı sekiz duygu skorlaması ve karakter minimap'i gösteren araştırma prototipi | [kanıt](https://github.com/carlaiau/readwithjev#readme) |
| [pekth/draftpulse](https://github.com/pekth/draftpulse) | C | 4 | yes | X gönderisi yazarken canlı viral skor tahmini; Jev birkaç dar soruyu yanıtlar, kodda ağırlıklı birleştirilir; anahtar yoksa sahte sezgisel devreye girer. | [kanıt](https://github.com/pekth/draftpulse) |
| [dabit3/jev-experiments](https://github.com/dabit3/jev-experiments) | C | 2 | yes | Devin tarafından yapılmış TypeSafe/Jev gecikme odaklı demo koleksiyonu; üst README yetersiz, ayrıntı alt dizin README'lerinde | [kanıt](https://github.com/dabit3/jev-experiments) |
