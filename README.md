# LLM Grading Dashboard – Dokumentáció

Ez a repository egy kézzel írt diszkrét matematikai feladatok automatikus felismerését és értékelését vizsgáló projekt dokumentációját és kísérleti anyagait tartalmazza.

A cél különböző multimodális és nyelvi modellek tesztelése kézzel írt megoldások felismerésére, valamint annak vizsgálata, hogy az így kapott szöveg alapján mennyire megbízhatóan értékelhető egy hallgatói megoldás.

> Ez a repository jelenleg főként kutatási anyagokat, tesztadatokat és modellkimeneteket tartalmaz.  
> A végleges alkalmazás, amelyben a kutatás eredményeit felhasználjuk külön repositoryban fog készülni.

## 📁 Tartalom

A repository többek között az alábbiakat tartalmazza:

- hallgatói megoldásokról készült képek
- különböző OCR / vision modellek kimenetei
- különböző értékelő modellek eredményei
- modell-összehasonlítások
- teszteléshez használt Python scriptek
- kísérleti dashboard / vizualizáció
- promptok és egyéb fejlesztési jegyzetek

A jelenlegi mappaszerkezet például:

```text
img/        → bemeneti képek
ocr/        → OCR / képfelismerési eredmények
res/        → értékelő modellek eredményei
app.py      → kísérleti dashboard
model.py    → modellek futtatásához használt script
