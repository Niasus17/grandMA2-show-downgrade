# grandMA2 Show Downgrade

Open a grandMA2 **3.9.x** show file in an **older 3.9 version** — for example, a show saved in 3.9.63.11 on a console or
onPC that runs 3.9.60.45. MA Lighting does not offer this; a newer version opens older shows, but not the other way round.

**[Download the .exe](../../releases/latest)** — Windows, no installation, no Python needed.

## How to use
1. Run `grandMA2 Show Downgrade.exe`.
2. **Choose show…** — pick a `.show.gz` (onPC keeps shows in `C:\ProgramData\MA Lighting Technologies\grandma\gma2_V_<version>\shows`).
3. The program shows the file's version and offers only **lower** 3.9 versions (installed onPC versions are marked).
   You can also type any version like `3.9.60.45`.
4. **Convert.** A new file `name (3.9.60.45).show.gz` is saved into that version's onPC shows folder if it is installed,
   otherwise next to the original. **The original show is never changed.**

Command line: `"grandMA2 Show Downgrade.exe" "my show.show.gz" 3.9.60.45 [output.show.gz]`

## What it does
A `.show.gz` is gzip with the binary stream `MA DATA`. Bytes 8–11 of the stream hold the MA version (little-endian:
build, release, minor, major). Between 3.9.60, 3.9.61 and 3.9.63 the object layout of a show is the same, so the program
writes the target version into those 4 bytes and repacks the file the way MA does (plain 10-byte gzip header).
Bytes 16–19 are a pointer and are left untouched.

## Tested
| From | To | Result |
|---|---|---|
| 3.9.61.5 | 3.9.60.45 | opens; groups, effects, sequences, patch, layouts intact |
| 3.9.63.11 | 3.9.60.45 | opens; groups, effects, sequences, patch, layouts intact |

Not tested: shows that use features existing only in the newer version, other 3.9 builds. **Keep the original** and check the
converted show before a gig. Please report results in Issues.

---

## По-русски
Программа переводит шоу grandMA2 **3.9.x** под **более старую версию 3.9** — например, шоу из 3.9.63.11 для пульта или onPC
на 3.9.60.45. Сама MA так не умеет: новая версия открывает старые шоу, а наоборот — нет.

1. Запустите `grandMA2 Show Downgrade.exe` (установка и Python не нужны).
2. **Выбрать шоу…** — файл `.show.gz` (у onPC: `C:\ProgramData\MA Lighting Technologies\grandma\gma2_V_<версия>\shows`).
3. Программа покажет версию шоу и предложит только версии **младше**; установленные onPC отмечены. Можно ввести свою.
4. **Перевести.** Новый файл «имя (3.9.60.45).show.gz» ляжет в папку шоу этой версии onPC (если она установлена) или рядом
   с исходным. **Исходное шоу не меняется.**

Проверено: 3.9.61.5 и 3.9.63.11 → 3.9.60.45. Шоу с функциями только новой версии не проверялись — сохраняйте оригинал и
проверяйте переведённое шоу до площадки.

## License
MIT — see [LICENSE](LICENSE). Not affiliated with MA Lighting. grandMA2 is a trademark of MA Lighting Technology GmbH.
