# VEQTA

VEQTA — проект приложения на **Frappe Framework**.

Текущая стадия: **prototype v0.1**. На первом стенде проверяется минимальная модель работы и пригодность штатных механизмов Frappe.

## Что проверяем в v0.1

- `Work Type`;
- `Work Item`;
- Frappe Workflow / Workflow State;
- Assign To / `ToDo`;
- Version / Timeline / Workflow comments;
- List / Kanban;
- воспроизводимость конфигурации из Git.

До результатов prototype перечисленное является проверяемой моделью, а не стабильным API.

## Документация

| Документ | Назначение |
|---|---|
| [DECISIONS.md](docs/DECISIONS.md) | принятые решения текущей стадии |
| [DEVELOPMENT.md](docs/DEVELOPMENT.md) | правила разработки и Git-цикл |
| [MODEL_V0_1.md](docs/MODEL_V0_1.md) | модель, проверяемая на стенде |
| [PROTOTYPE_V0_1.md](docs/PROTOTYPE_V0_1.md) | программа испытаний |
| [START_HERE_WSL2.md](docs/START_HERE_WSL2.md) | запуск первого стенда |

Рабочий checklist prototype: Issue #2.

## Источник истины

`lazuale/veqta` — источник истины продукта. Принятая конфигурация dev-site должна быть представлена файлами приложения или штатно экспортированной конфигурацией.

## Лицензия

VEQTA распространяется по **GNU Affero General Public License v3.0 or later** (`AGPL-3.0-or-later`). Полный текст — [LICENSE](LICENSE).

Frappe Framework является отдельной зависимостью под лицензией MIT.
