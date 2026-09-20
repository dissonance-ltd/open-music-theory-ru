# Open Music Theory RU

[![GitHub Pages](https://github.com/dissonance-ltd/open-music-theory-ru/actions/workflows/deploy.yml/badge.svg?branch=main)](https://dissonance-ltd.github.io/open-music-theory-ru/)
[![Tests](https://github.com/dissonance-ltd/open-music-theory-ru/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/dissonance-ltd/open-music-theory-ru/actions/workflows/test.yml)

Неофициальный русский перевод и адаптация [Open Music Theory, Version 2](https://viva.pressbooks.pub/openmusictheory/).

## Текущий пилот

Доступны черновики введения и первых пяти глав Fundamentals: введение в западную
музыкальную нотацию; запись нот, ключей и добавочных линеек; чтение ключей;
клавиатура и объединённый нотный стан; полутоны, тоны и знаки альтерации.
В книге 41 локальная иллюстрация и три внешних видеопримера. Рабочие листы пока
на английском. В главе о клавиатуре восстановлен рисунок 8, повреждённый в
разметке исходника; исправление документировано в тексте и реестре ресурсов.

**Источник пилота — Nebraska, Fall 2023**, датированная адаптация OMT2.
Текущий сайт VIVA возвращал HTTP 403 при попытках загрузки. Полный официальный XML
не получен; соответствие актуальной редакции VIVA не проверено. Сохранено полное
оглавление Nebraska и английские снимки шести переводимых страниц плюс благодарности.
Остальные главы ещё не импортированы. Подробности: [upstream/README.md](upstream/README.md).

Переводы подготовлены с помощью ИИ и требуют независимой терминологической и
содержательной рецензии. В `upstream/translations.json` у всех шести страниц статус
`draft` и нет отметки о рецензенте.

## Участие в переводе

Начните с [порядка работы](CONTRIBUTING.md), [политики перевода](docs/translation-policy.md)
и [трекера глав](docs/chapter-tracker.md). Для каждого нового перевода используйте
[шаблон проверки главы](docs/chapter-checklist.md); решения и результаты остаются
в репозитории. Полный черновик, технические проверки, сверка ИИ, человеческая
рецензия и локализация материалов учитываются отдельно.

## Локальная работа

```bash
cargo install mdbook --version 0.4.52 --locked
python -m pip install -r scripts/requirements.txt
python -m unittest discover -s tests -v
python scripts/render_glossary.py --check
python scripts/check_book.py
mdbook build
python scripts/check_book.py --built
mdbook serve --open
```

Для изменения терминологии редактируйте `glossary/terminology.yml`, затем выполните
`python scripts/render_glossary.py`. Новые соответствия сначала помечаются `candidate`.

## Обновления источника

```bash
python scripts/import_upstream.py --output /tmp/omt-candidate
python scripts/diff_upstream.py upstream/manifest.json /tmp/omt-candidate/manifest.json
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
- Провести независимое рецензирование шести черновиков и глоссария.
- Проверить работу внешних упражнений и видео, затем локализовать рабочие листы.
- Продолжить перевод: научная нумерация высот (ASPN), другие аспекты нотации, длительности нот и пауз.

## Лицензия

Русский текст и адаптация — [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
Исходные материалы сохраняют атрибуцию и индивидуальные исключения. См.
[LICENSE.md](LICENSE.md), [ATTRIBUTION.md](ATTRIBUTION.md) и реестр `upstream/assets.json`.
Оригинальные логотип и обложка OMT не включены.
