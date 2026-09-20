<!-- GENERATED — do not edit; run tools/build.py -->
[English](../../categories/search-rerank.md) | Türkçe

# Arama ve yeniden sıralama

Bu kategoride 20 repo; önce sınıf, sonra puan sırasıyla.

[Bütün repolar](../REPOS.md)

| Repo | Sınıf | Toplam | Jev çağırıyor | Ne yapıyor | Kanıt |
|---|---|---|---|---|---|
| [tonyzdev/PiJ](https://github.com/tonyzdev/PiJ) | A | 14 | yes | Pi tabanlı terminal kodlama ajanı; Jev skill seçimi/kod sıralama/hata triyajı yapar, SWE-bench+kontrollü deneylerle \(BM25 kontrol kolu\) ölçülmüş | [kanıt](https://github.com/tonyzdev/PiJ#readme) |
| [WiktorB2004/llama-index-jev](https://github.com/WiktorB2004/llama-index-jev) | A | 13 | yes | LlamaIndex için Jev tabanlı reranker \(fail-open\) ve router selector \(fail-closed\); BEIR nfcorpus/scifact üzerinde ölçülmüş nDCG@5 iyileşmesi | [kanıt](https://github.com/WiktorB2004/llama-index-jev#readme) |
| [bartlomein/oko](https://github.com/bartlomein/oko) | A | 12 | yes | Bir kodlama ajaninin sorgusu icin aday kod parcalarini Jev ile siralayan yerel MCP/CLI araci; ucfarkli kodlama araciyla 108 oturumluk bir pilotta olculmus. | [kanıt](https://github.com/bartlomein/oko#readme) |
| [sufianetaouil/every](https://github.com/sufianetaouil/every) | A | 12 | yes | Bir kod tabanındaki her fonksiyona aynı evet/hayır sorusunu sorup olasılığa göre sıralayan, 'sorusu soru olan grep' aracı | [kanıt](https://github.com/sufianetaouil/every#readme) |
| [uehaj/jev-semgrep](https://github.com/uehaj/jev-semgrep) | A | 12 | yes | Satirlari diller arasi anlama gore eslestiren bagimliliksiz bir grep: Jev her satiri belirtilen bir anlama gore puanlar, sonuclar VE/VEYA/DEGIL ile birlesir; istek basina 30 satir, 8 es zamanli istek. | [kanıt](https://github.com/uehaj/jev-semgrep#readme) |
| [404priyanshu/zsh-jev-suggest](https://github.com/404priyanshu/zsh-jev-suggest) | A | 11 | yes | Zsh geçmiş önerilerini Jev ile sıralar; anlık öneri için önceden ısıtılmış yerel cache, Ctrl-Space'te canlı Jev sorgusu kullanır. | [kanıt](https://github.com/404priyanshu/zsh-jev-suggest) |
| [tpellet/grevi](https://github.com/tpellet/grevi) | A | 10 | yes | Alti Unix-tarzi fiil \(why, pick, is, run, add, sort\) araciligiyla anlama gore grep yapan, hicbir zaman metin uretmeyip yalnizca mevcut girdiden secen bir Rust CLI'si. | [kanıt](https://github.com/tpellet/grevi#readme) |
| [Peu77/JevFind](https://github.com/Peu77/JevFind) | A | 9 | yes | İki aşamalı eşikli semantik kod arama: önce dosya-yolu alaka skoru, sonra pencere skorlaması | [kanıt](https://github.com/Peu77/JevFind#readme) |
| [sijiaoh/jevgrep](https://github.com/sijiaoh/jevgrep) | A | 9 | yes | Bir dosyanin her satirini kalip eslestirme yerine anlamina gore puanlayan, diller arasi calisan ve mevcut grep-tabanli herhangi bir is akisina boru hattiyla baglanabilen bir komut satiri araci. | [kanıt](https://github.com/sijiaoh/jevgrep#readme) |
| [AkashPriyadarshii/jev-scout](https://github.com/AkashPriyadarshii/jev-scout) | A | 8 | yes | Doğal dil isteğine göre gerçek, aktif bakımlı repo/crate bulan Rust CLI+MCP; Jev ile tek spekülatif fan-out skorlaması | [kanıt](https://github.com/AkashPriyadarshii/jev-scout#readme) |
| [pax-k/p-ax](https://github.com/pax-k/p-ax) | A | 7 | no | Ajanlar için salt-okunur kod tabanı zeka katmanı; deterministik arama/aggregate, AI yalnız kesin kanıt sonrası sentez için opsiyonel | [kanıt](https://github.com/pax-k/p-ax#readme) |
| [ellipsis-dev/blink](https://github.com/ellipsis-dev/blink) | B | 10 | yes | Jev ile dosya/klasör adlarını skorlayıp olasılığa göre 'walker' oylaması dağıtan kod tabanı arama aracı | [kanıt](https://github.com/ellipsis-dev/blink#readme) |
| [thevibeworks/pagepilot](https://github.com/thevibeworks/pagepilot) | B | 10 | yes | Jev'in sayfa bloklarını paralel noul ile değerlendirip küçük deterministik bir 'okuma spesifikasyonu' yazdığı, sonraki aynı-site sayfalarında 0 token ile tekrar oynatılan tarayıcı eklentisi | [kanıt](https://github.com/thevibeworks/pagepilot#readme) |
| [choxos/jev-reviewer](https://github.com/choxos/jev-reviewer) | B | 9 | yes | Tarayıcı-içi sistematik derleme veri-çıkarma aracı; Jev aday satırları işaretliyor \(Choice\), sonra doğruluyor \(Noul\), alıntı asla üretilmiyor sadece kopyalanıyor | [kanıt](https://github.com/choxos/jev-reviewer) |
| [jexp/neo4jev](https://github.com/jexp/neo4jev) | B | 9 | yes | Neo4j grafını tek system_one çağrısında Choice+Noul ile hop hop gezen, beam search ile en iyi yolu bulan demo | [kanıt](https://github.com/jexp/neo4jev#readme) |
| [MayberryDT/chartroom](https://github.com/MayberryDT/chartroom) | B | 9 | yes | Jev'in getirilen pasajlari yeniden siraladigi ve sayfa baglantilari onerdigi, kucuk sentetik 30-notluk bir karsilastirmada olculmus GBrain uzerine kurulu yerel bir ikinci beyin. | [kanıt](https://github.com/MayberryDT/chartroom#readme) |
| [rmwahid/jev-cordhub](https://github.com/rmwahid/jev-cordhub) | B | 8 | yes | Jev'in etiketsiz 371 depoyu degerlendirdigi ve katalogu her sorgu icin alaka ve guvenle siraladigi, ozel bir Discord yer imi kanali uzerinde arama. | [kanıt](https://github.com/rmwahid/jev-cordhub#readme) |
| [ant4g0nist/joxide](https://github.com/ant4g0nist/joxide) | B | 7 | yes | zoxide + Jev ile açıklamaya göre proje dizinine atlayan araç; toplu noul skorlama, eşik+marjla otomatik/aday listesi kararı | [kanıt](https://github.com/ant4g0nist/joxide#readme) |
| [AlbionaHoti/refgarden](https://github.com/AlbionaHoti/refgarden) | C | 6 | yes | Müze/NASA görsel arşivlerinde arama ifadesi seçip metadata'dan \(görseli görmeden\) öne çıkan sonucu seçen 3D galeri aracı | [kanıt](https://github.com/AlbionaHoti/refgarden) |
| [DeepBlueDynamics/typesafe-arena](https://github.com/DeepBlueDynamics/typesafe-arena) | C | 5 | no | docs.typesafe.ai'nin yerel markdown aynası + BM25+bilgi-grafiği tabanlı 'Lume' arama aracı; Jev'e doğrudan çağrı yapmıyor, dokümantasyon arşivi/arama katmanı | [kanıt](https://github.com/DeepBlueDynamics/typesafe-arena) |
