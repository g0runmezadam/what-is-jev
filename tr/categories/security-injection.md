<!-- GENERATED — do not edit; run tools/build.py -->
[English](../../categories/security-injection.md) | Türkçe

# Güvenlik ve injection

Bu kategoride 9 repo; önce sınıf, sonra puan sırasıyla.

[Bütün repolar](../REPOS.md)

| Repo | Sınıf | Toplam | Jev çağırıyor | Ne yapıyor | Kanıt | Denetlendi |
|---|---|---|---|---|---|---|
| [agent-chaperone/agent-chaperone](https://github.com/agent-chaperone/agent-chaperone) | A | 14 | yes | MCP proxy + hook güvenlik duvarı; araç çağrısı öncesi ve sonucu okumadan önce tarar, tek-kullanımlık tam-argüman onay jetonları, araç listesi sapması tespiti; InjecAgent/BIPIA gibi kamu veri setlerinde AUC 0.976-1.0 ile ölçülmüş | [kanıt](https://github.com/agent-chaperone/agent-chaperone#readme) | yes |
| [leepokai/jev-guard](https://github.com/leepokai/jev-guard) | A | 11 | yes | 8 farklı kodlama ajanı/host'unda çalışan güvenlik hook'u; risk/approval/user_requested/from_untrusted dört tipli soruyla deny/ask/allow kararı veriyor, talimat dosyalarını \(skill/CLAUDE.md\) sızıntı/gizli-yürütme için tarıyor | [kanıt](https://github.com/leepokai/jev-guard) | yes |
| [rodriveiga01/second-thought](https://github.com/rodriveiga01/second-thought) | B | 10 | yes | Terminal kemeri: her shell komutunu çalışmadan önce çoktan-seçmeli kalibre yargıyla \(tehlikeli mi? hangi tür? ne kadar emin?\) allow/warn/block ediyor | [kanıt](https://github.com/rodriveiga01/second-thought#readme) | yes |
| [cobusgreyling/Jev](https://github.com/cobusgreyling/Jev) | B | 8 | yes | Resmi olmayan Jev tanıtım laboratuvarı + TS harness CLI; 'jev route --goal' ve 'jev guard --text "Ignore previous instructions"' komutları var | [kanıt](https://github.com/cobusgreyling/Jev#readme) | no |
| [newuser7171/antivirus](https://github.com/newuser7171/antivirus) | B | 7 | yes | Dosya/URL/canli-process EDR taramasi yapan masaustu antivirus; yapisal ozellikleri cikarip Jev'e \(choice/score/noul\) siddet/aksiyon karari verdiriyor, ayarlanabilir hassasiyet katmanlari var. | [kanıt](https://github.com/newuser7171/antivirus#readme) | no |
| [newuser7171/jev-ndr](https://github.com/newuser7171/jev-ndr) | B | 7 | yes | Canli ag soketi/DNS trafigini Jev/classifier.dev ile toplu \(1000 alan adi/~650ms\) siniflandirip C2/DGA/exfiltrasyon tespiti yapan NDR platformu. | [kanıt](https://github.com/newuser7171/jev-ndr#readme) | no |
| [adrianpeticila/gorgona](https://github.com/adrianpeticila/gorgona) | C | 6 | no | Sıfır bağımlılıklı, deterministik \(regex/graph tabanlı\) ajan guardrail motoru; bilinçli olarak LLM-judge kullanmıyor | [kanıt](https://github.com/adrianpeticila/gorgona#readme) | no |
| [EpicEric/safe-sh](https://github.com/EpicEric/safe-sh) | C | 6 | yes | 'sh'/'bash' yerine geçen, curl\|bash betiklerini çalıştırmadan önce Jev ile statik analiz edip warn/error eşiğine göre engelleyen sarmalayıcı | [kanıt](https://github.com/EpicEric/safe-sh#readme) | yes |
| [newuser7171/jev-vpn](https://github.com/newuser7171/jev-vpn) | C | 5 | yes | Statik reklam/izleyici listeleriyle Jev tabanli sifir-gun reklam siniflandirmasini birlestiren yerel VPN/proxy reklam engelleyici. | [kanıt](https://github.com/newuser7171/jev-vpn#readme) | no |
