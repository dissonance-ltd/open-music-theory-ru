# Open Music Theory RU

[![GitHub Pages](https://github.com/dissonance-ltd/open-music-theory-ru/actions/workflows/deploy.yml/badge.svg?branch=main)](https://dissonance-ltd.github.io/open-music-theory-ru/)
[![Tests](https://github.com/dissonance-ltd/open-music-theory-ru/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/dissonance-ltd/open-music-theory-ru/actions/workflows/test.yml)

Неофициальный русский перевод и адаптация [Open Music Theory, Version 2](https://viva.pressbooks.pub/openmusictheory/).

## Текущее состояние

Доступны черновики введения и первых четырнадцати глав Fundamentals: введение в западную
музыкальную нотацию; запись нот, ключей и добавочных линеек; чтение ключей;
клавиатура и объединённый нотный стан; полутоны, тоны и знаки альтерации;
научная нумерация высот (ASPN); другие аспекты нотации; длительности нот и пауз;
метр с двухчастным и трёхчастным делением доли; другие основы ритма;
мажорные и минорные гаммы, ступени и ключевые знаки; диатонические лады
и хроматическая гамма.
В книге 80 локальных иллюстраций. Внешние видео, партитуры и рабочие листы пока
на английском. В главе о клавиатуре восстановлен рисунок 8, повреждённый в
разметке исходника; исправление документировано в тексте и реестре ресурсов.

**Источник пилота — Nebraska, Fall 2023**, датированная адаптация OMT2.
Текущий сайт VIVA возвращал HTTP 403 при попытках загрузки. Полный официальный XML
не получен; соответствие актуальной редакции VIVA не проверено. Сохранено полное
оглавление Nebraska и 16 английских снимков: пятнадцать переводимых страниц и благодарности.
Пакеты 04 (главы 9–11) и 05 (главы 12–14) подготовлены параллельно;
пакет 05 основан на пакете 04, поэтому объединять их следует в этом порядке. Подробности: [upstream/README.md](upstream/README.md).

Переводы подготовлены с помощью ИИ и требуют независимой терминологической и
содержательной рецензии. В `upstream/translations.json` у всех пятнадцати страниц статус
`draft` и нет отметки о рецензенте. Для глав 9–14 выполнена отдельная сверка ИИ;
её замечания и результаты технических проверок фиксируются в записях глав и PR.
Человеческая рецензия, локализация внешних материалов и просмотр собранных страниц
остаются отдельными незавершёнными задачами.

## Участие в переводе

Начните с [порядка работы](CONTRIBUTING.md), [политики перевода](docs/translation-policy.md)
и [трекера глав](docs/chapter-tracker.md). Параллельная работа описана в
[пакетном процессе](docs/batch-translation.md). Для каждого нового перевода используйте
[шаблон проверки главы](docs/chapter-checklist.md); решения и результаты остаются
в репозитории. Полный черновик, технические проверки, сверка ИИ, человеческая
рецензия и локализация материалов учитываются отдельно.

## Локальная работа

Установите [uv](https://docs.astral.sh/uv/getting-started/installation/).
Python 3.12 выбран в `.python-version`; uv управляет зависимостями в `.venv`.

```bash
cargo install mdbook --version 0.4.52 --locked
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
uv run --locked python scripts/render_glossary.py --check
uv run --locked python scripts/check_book.py
mdbook build
uv run --locked python scripts/check_book.py --built
mdbook serve --open
```

Для изменения терминологии редактируйте `glossary/terminology.yml`, затем выполните
`uv run --locked python scripts/render_glossary.py`. Новые соответствия сначала помечаются `candidate`.

Для изменения Python-скриптов см. [устройство инструментов и зависимости](scripts/README.md).
Выполните `uv sync --locked` (включая группу `dev`); форматирование Ruff и строгая проверка
типов mypy входят в CI наряду с тестами.

## Обновления источника

```bash
uv run --locked python scripts/import_upstream.py --output /tmp/omt-candidate
uv run --locked python scripts/diff_upstream.py upstream/manifest.json /tmp/omt-candidate/manifest.json
```

Импортёр сохраняет английские тексты отдельно. Русские главы и их хеши привязки
к исходнику не перезаписываются. После изменения оригинала CI требует повторной
сверки перевода с источником.

## GitHub Pages

В **Settings → Pages → Build and deployment** выберите **Source: GitHub Actions**.
Workflow публикации запускается при изменении `main` или вручную. Pull request
проходит проверку происхождения текстов, локальных ссылок, изображений, глоссария
и полную сборку mdBook; результат доступен как артефакт `book-preview`.

## Следующие задачи

- Сверить пилот с текущим OMT2 при получении официального источника.
- Провести независимое рецензирование пятнадцати черновиков и глоссария.
- Проверить работу внешних упражнений и видео, затем локализовать рабочие листы.
- Рассмотреть и объединить пакет 04, затем пакет 05; после этого выбрать следующий объём по [трекеру](docs/chapter-tracker.md).

## Лицензия

Русский текст и адаптация — [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
Исходные материалы сохраняют атрибуцию и индивидуальные исключения. См.
[LICENSE.md](LICENSE.md), [ATTRIBUTION.md](ATTRIBUTION.md) и реестр `upstream/assets.json`.
Оригинальные логотип и обложка OMT не включены.
