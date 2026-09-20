"""Pure rendering of validated terminology into the existing Markdown format."""

from .models import Glossary, Term, TermStatus

STATUS_LABELS: dict[TermStatus, str] = {
    "candidate": "кандидат",
    "accepted": "принято",
    "deprecated": "не используется",
}
INTRODUCTION = (
    "Все соответствия со статусом «кандидат» требуют рецензирования. "
    "Эта страница генерируется из `glossary/terminology.yml`."
)


def escape_cell(value: str) -> str:
    return value.replace("|", r"\|").replace("\n", " ")


def render_term(term: Term) -> str:
    note = term.note
    if term.alternatives:
        note += " Варианты: " + ", ".join(term.alternatives) + "."
    cells = [term.en, term.ru, note, STATUS_LABELS[term.status]]
    return "| " + " | ".join(escape_cell(cell) for cell in cells) + " |"


def render(glossary: Glossary) -> str:
    lines = [
        "# Рабочий глоссарий",
        "",
        INTRODUCTION,
        "",
        "| English | Русский термин | Примечание | Статус |",
        "|---|---|---|---|",
    ]
    for term in sorted(glossary.terms, key=lambda term: term.en.lower()):
        lines.append(render_term(term))
    return "\n".join(lines) + "\n"
