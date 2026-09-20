[English](../CONTRIBUTING.md) | **Türkçe**

# Katkıda bulunma

Bu depo yeni malzemeden çok düzeltmeye bağımlıdır — buradaki her iddia ancak arkasındaki kaynak kadar sağlamdır. Bir şey yanlışsa, kaynağıyla birlikte söyleyin.

## Repo eklemek

Ölçüt: **herkese açık**, **çalışıyor** (boş bir iskelet değil), ve ya gerçekten Jev/System-1 API'sini çağırıyor ya da Jev'i gerçekten araştırıyor/ölçüyor (bir benchmark, bir kalibrasyon çalışması, bir eleştiri — API'yi kendisi çağırmak zorunda değil). Yalnızca `jev` GitHub etiketini taşıyan ama TypeSafe'in modeliyle ilgisi olmayan bir repo bu ölçütü karşılamaz; bkz. `data/SCHEMA.md` içindeki `calls_jev`.

Eklemenin iki yolu:

1. **Issue ya da pull request** — repo URL'si ve ne yaptığına dair tek cümle. Güncel [`data/rubric.md`](../data/rubric.md)'ye göre puanlanır ve `tools/build.py` tarafından birleştirilir.
2. **`data/manual.txt`** — dosyada zaten olan biçimde, satır başına bir `owner/name` ekleyin. `tools/update.py` bunu etiket aramasıyla aynı şekilde alır, üstveri ve README'sini indirir, puanlama için `data/pending.txt`'e kuyruğa ekler.

`REPOS.md`, herhangi bir `categories/*.md` sayfası, `TOP.md` ya da `SOURCES.md`'yi doğrudan düzenleyen bir PR açmayın — bunlar üretilir (ilk satır: `<!-- GENERATED — do not edit; run tools/build.py -->`) ve elle yapılan her değişiklik bir sonraki build'de silinir.

## Puana itiraz etmek

Reponun adını ve satırın `total`/`class` değerini belirten, resmi değiştiren bir kanıta bağlantı veren bir issue açın — örneğin puanlayıcının kaçırdığı bir README bölümü, "evidence" puanının yansıtması gereken bir benchmark, ya da `relevance`/`novelty`'nin [`data/rubric.md`](../data/rubric.md)'ye göre neden fazla ya da az verildiği. Bir puan yalnızca ölçeğe bağlı, belirtilmiş bir gerekçeyle değişir, sayı "yanlış hissettiriyor" diye değil — hangi eksen ve neden, onu söyleyin.

## Kaynak eklemek

`data/sources.jsonl`'e zorunlu bir `url` (`http://` ya da `https://` ile başlamalı) artı `type`, `title`, `author`, `date`, `trust` (1–5) ve kısa bir not içeren bir satır ekleyin. Alan listesi ve güven düzeyi rehberi için [`data/SCHEMA.md`](../data/SCHEMA.md#sourcesjsonl)'ye bakın. Çalışan bağlantısı olmayan bir kaynak kabul edilmez — bu depo, okuyucunun gidip açamayacağı hiçbir şeye kaynak göstermez.

## Bulguya itiraz etmek

[`FINDINGS.md`](FINDINGS.md) içindeki satırı alıntılayan ve ona çelişen ya da nitelik ekleyen birincil kaynağa bağlantı veren bir issue açın. Kaynaksız "bence bu doğru değil" bir hüküm etiketini değiştirmez; rakip bir birincil kaynak değiştirir.

## Üretilen sayfaları düzenlemek

Asla elle değil. `REPOS.md`, `TOP.md`, `SOURCES.md`, `categories/` altındaki her dosya ve bunların `tr/` karşılıkları `data/repos.jsonl` ve `data/sources.jsonl`'den `tools/build.py` tarafından üretilir. Üretilen bir sayfa yanlış görünüyorsa, düzeltme ya bir veri düzeltmesidir (yukarıya bakın) ya da `tools/build.py`'nin kendisindeki bir hatadır — ikincisini normal bir kod issue'su olarak açın.

## Testleri çalıştırmak

`tools/`, `data/` ya da şemaya bir değişiklik göndermeden önce:

```
python tools/build.py --check          # üretilen sayfalar veriyle zaten eşleşmeli
python -X utf8 -m unittest discover -s tests
```

İkisi de geçmeli. `--check` hiçbir şey yazmaz, üretilen bir sayfa `data/`'ya göre eskiyse sıfırdan farklı çıkışla biter; test paketi şema doğrulamayı, eski (legacy) içe aktarım kurallarını, determinizmi (aynı girdi → bayt-bayt aynı çıktı) ve İngilizce/Türkçe sayfa kümelerinin birebir eşleştiğini kapsar.
