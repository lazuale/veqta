# Практикумы Frappe Framework 16

Этот курс изучает Frappe через **одно цельное учебное приложение**, которое развивается от пустого app до переносимой рабочей системы.

Учебный продукт — небольшая **система службы эксплуатации**. Она ведёт места и оборудование, принимает обращения, назначает исполнителей, проводит перемещения и проверки, создаёт регламентные работы, строит отчёты и принимает обращения через Web Form.

Мы используем штатные механизмы Frappe так, как они устроены в платформе: Developer Mode, Standard DocType, роли и permissions, Assign To, Workflow, Reports, Workspace, Automation, Web Form, fixtures и перенос на чистый site.

Собственную бизнес-логику на Python или JavaScript в базовой программе не пишем. Если штатный механизм Frappe сам использует простое выражение, например `PythonExpression` в Assignment Rule, разбираем только необходимый минимум.

## Учебное приложение

Рабочее имя приложения:

```text
Bench:  facility-ops-bench
App:    facility_ops
Site:   facility-ops.localhost
Module: Facility Operations
```

Это один app на весь курс. P1–P8 не создают новые приложения: каждый этап добавляет новый законченный слой в `facility_ops`.

## Предметная модель

Основные DocType курса:

```text
Facility Location (Tree)
        │
        ├──────────────┐
        ▼              ▼
 Equipment Type    Service Request
        │              │
        ▼              ├── Assign To / ToDo
    Equipment           └── Workflow
        │
        ├────────► Equipment Movement
        │                 └── Equipment Movement Item (Child)
        │
        ├────────► Inspection
        │
        └────────► Maintenance Work
```

Модель намеренно небольшая. Мы не строим ERP или полноценную CMMS. Новая сущность появляется только тогда, когда без неё нельзя естественно показать нужный механизм Frappe.

## Версия курса

Практикумы проверяются на **Frappe Framework v16.32.0**.

Для каждого спорного места приоритет такой:

1. фактический стенд на v16.32.0;
2. исходники тега `v16.32.0` в `frappe/frappe`;
3. официальная документация Frappe;
4. ветка `version-16` — только для отслеживания будущих изменений.

## Как устроено обучение

Каждый этап должен дать два результата одновременно:

1. приложение стало функциональнее;
2. ученик понял новый строительный блок Frappe и увидел, где он хранится.

Рабочий цикл каждого этапа:

```text
задача
  ↓
модель до кликов
  ↓
сборка штатными средствами Frappe
  ↓
проверка нормального и отрицательного сценария
  ↓
Git / metadata / database
  ↓
следующий слой приложения
```

Редкие возможности, которым нет естественного места в основной модели, остаются короткими лабораториями. Модель приложения не искажается ради формального покрытия матрицы.

## Программа

| Код | Стадия приложения | Что появляется | Главные механизмы Frappe |
|---|---|---|---|
| [P0](projects/00-lab/README.md) | Основа | `facility_ops`, site и первый пробный DocType | Bench, app, site, Module, Developer Mode, Desk, Git |
| P1 | Реестр эксплуатации | места, типы оборудования, оборудование, перемещения | DocType, Fields, Link, Tree, Child Table, Naming, Data Import |
| P2 | Формы и переносимые изменения | site-specific изменение Equipment и альтернативный layout | Customize Form, Custom Field, Property Setter, DocType Layout, Export Customizations |
| P3 | Обращения и совместная работа | Service Request и реальные пользователи | Users, Roles, Permissions, User Permission, Share, Assign To, ToDo, Kanban |
| P4 | Управляемый жизненный цикл | подтверждённые перемещения и Workflow обращений | DocStatus, Submit/Cancel/Amend, Workflow, Audit Trail, fixtures, первый clean-site test |
| P5 | Контроль и рабочий стол | Inspection, аналитика и печать | Calendar, Report Builder, Number Card, Dashboard Chart, Workspace, Print, PDF |
| P6 | Автоматизация | Maintenance Work и автоматическое распределение обращений | Auto Repeat, Assignment Rule, Notification, scheduler |
| P7 | Внешний вход | создание Service Request через сайт | Web Form, Guest, Website User, permissions, attachments, Standard Web Form |
| P8 | Выпуск приложения | финальная конфигурация на новом чистом site | install-app, migrate, fixtures/customizations, приёмочные сценарии |

Подробная последовательность находится в [ROADMAP.md](ROADMAP.md). Архитектура учебного приложения — в [ARCHITECTURE.md](ARCHITECTURE.md). Матрица покрытия Frappe — в [MATRIX.md](MATRIX.md).

## Что должно получиться в конце

После P8 ученик должен уметь без пошаговой инструкции:

- объяснить Bench, app, site, Module, DocType, DocField, Document и `name`;
- спроектировать связанную модель данных до создания форм;
- выбрать между обычным, Tree, Child, Single и Custom DocType;
- понимать Standard объект, site customization и fixture как разные способы поставки конфигурации;
- настроить Naming, формы, списки, импорт и поиск;
- разделить пользователей по ролям и данным;
- отличать permissions от Assignment;
- отличать обычный статус, Workflow State и системный DocStatus;
- использовать Submit/Cancel/Amend там, где документ действительно фиксирует факт;
- собрать Workflow для управляемого процесса;
- построить Workspace, отчёты, показатели, календарь и печатную форму;
- применять штатную автоматизацию без собственного backend-кода;
- открыть безопасный внешний ввод через Web Form;
- установить приложение на чистый site и доказать, что принятая конфигурация переносится без повторного ручного накликивания.

## Документы

- [SCOPE.md](SCOPE.md) — границы базовой программы;
- [ARCHITECTURE.md](ARCHITECTURE.md) — архитектура `facility_ops` и логика обучения;
- [MATRIX.md](MATRIX.md) — где впервые изучается каждый механизм;
- [ROADMAP.md](ROADMAP.md) — последовательность P0–P8 и критерии перехода;
- [REFERENCES.md](REFERENCES.md) — официальная документация и исходники для проверки курса.

Первый этап: **[P0 — Основа приложения](projects/00-lab/README.md)**.
