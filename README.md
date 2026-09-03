# VEQTA

**VEQTA — независимая open-source инженерная и продуктовая экосистема, построенная на Frappe Framework.**

VEQTA работает как architecture-first product studio: мы исследуем, как естественно и надёжно проектировать приложения на Frappe, превращаем подтверждённые инженерные решения в обучение и reference implementations, а зрелые решения — в самостоятельные open-source продукты.

> **Understand Frappe. Prove the design. Ship useful software.**

VEQTA не заменяет и не форкает Frappe Framework и не является официальным проектом Frappe Technologies. Frappe остаётся технологическим фундаментом.

## Как устроена VEQTA

```text
Frappe Framework
       │
       ▼
VEQTA Engineering
       │
       ├──────────────┐
       ▼              ▼
VEQTA Learn       VEQTA Labs
       │              │
       └──────┬───────┘
              ▼
       VEQTA Products
              │
              ▼
users · contributors · services · community
```

### Engineering

Инженерная база VEQTA: архитектурные стандарты, доказательства, паттерны, ограничения и правила принятия решений на Frappe.

Текущий основной материал — [`docs/frappe-architecture-standard/`](docs/frappe-architecture-standard/README.md). В ходе реорганизации он будет перенесён в `engineering/frappe/` без изменения своей роли как evidence-based архитектурного стандарта.

### Learn

Структурированное обучение проектированию на Frappe: learning paths, практические курсы и упражнения.

Мы не строим курс как каталог функций Framework. Учебная последовательность должна объяснять, **какая ответственность появилась, какой механизм Frappe ей уже владеет и почему выбранное решение соответствует архитектуре Framework**.

Текущий baseline нового практикума находится в [`docs/frappe-training/`](docs/frappe-training/).

### Labs

Изолированные эксперименты для проверки спорных архитектурных, продуктовых и UX-гипотез.

Lab может завершиться неудачей, стать reference implementation, дать материал для Learn или перейти в product incubation. Эксперимент не считается продуктом только потому, что в нём уже есть рабочий код.

Существующий prototype `Work Type` / `Work Item` теперь классифицируется как будущий **VEQTA Labs / Work Management / v0.1**. Его текущие материалы пока остаются в `docs/` до физической миграции структуры репозитория.

### Products

Самостоятельные production-продукты, решающие реальные пользовательские задачи.

Для обычного Frappe-продукта default software boundary — самостоятельно устанавливаемый Frappe App со своим scope, релизным циклом, документацией и продуктовой идентичностью. Дополнительный frontend, сервис или App допустимы только при реальной продуктовой ответственности и явном архитектурном решении.

VEQTA сама не является обязательным runtime App и не вводит `veqta_core` поверх Frappe заранее.

## Инженерный принцип

Для каждого требования сначала определяется ответственность, затем проверяется штатный механизм Frappe:

```text
требование
    ↓
какая ответственность нужна?
    ↓
какой механизм Frappe уже ей владеет?
    ↓
совпадает ли его семантика?
    ├── да → используем штатный механизм
    └── нет → ищем официальную точку расширения
                    ↓
          собственный механизм только при необходимости
```

Собственный код не является проблемой. Проблема — без причины дублировать ответственность, которой уже владеет Framework.

## Foundation baseline

Направление VEQTA фиксируется пятью документами:

1. [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) — что такое VEQTA, её миссия, границы и неизменяемые без явного решения правила.
2. [`BRAND_ARCHITECTURE.md`](BRAND_ARCHITECTURE.md) — архитектура бренда, аудитории, naming и визуальные принципы.
3. [`ENGINEERING_PRINCIPLES.md`](ENGINEERING_PRINCIPLES.md) — общая инженерная дисциплина для Engineering, Learn, Labs и Products.
4. [`PRODUCT_LIFECYCLE.md`](PRODUCT_LIFECYCLE.md) — путь `Problem → Lab → Reference → Incubating Product → Product`.
5. [`REPOSITORY_STRUCTURE.md`](REPOSITORY_STRUCTURE.md) — целевая структура Git и правила выделения самостоятельных продуктов.

При конфликте foundation-документов приоритет имеет `PROJECT_CHARTER.md` до явного исправления противоречия.

## Текущий статус

VEQTA проходит переход от концепции одного prototype-приложения к architecture-first open-source product studio.

Сейчас уже существуют три реальные группы активов:

```text
Engineering → Frappe Architecture Standard
Learn       → новый архитектурный практикум Frappe
Labs        → Work Management prototype v0.1
Products    → production-продуктов пока нет
```

Отсутствие production-продукта на текущем этапе является явным статусом, а не пробелом, который нужно закрыть искусственно. Кандидат должен пройти продуктовую и инженерную валидацию.

## Целевая структура репозитория

```text
veqta/
├── foundation documents
├── engineering/
├── learn/
├── labs/
├── products/
└── brand/
```

Текущий `docs/` будет разобран по этим ответственностям после принятия foundation baseline. Полная карта миграции находится в [`REPOSITORY_STRUCTURE.md`](REPOSITORY_STRUCTURE.md).

## Для кого VEQTA

Umbrella-бренд VEQTA ориентирован прежде всего на builders:

- Frappe developers;
- будущих разработчиков Frappe;
- software / solution architects;
- technical leads;
- implementation teams;
- independent builders;
- open-source contributors.

У каждого будущего Product будет собственная end-user аудитория и собственное ценностное предложение.

## Open source

VEQTA развивается как open-source-first инициатива. Базовая стратегическая модель не предполагает искусственного open-core, в котором существенные продуктовые возможности намеренно остаются только в закрытой редакции.

Точный режим лицензирования будет разделён по типам артефактов: software, engineering/documentation, learning content и trademarks требуют разных правил. До принятия отдельной лицензионной политики действует существующий файл [`LICENSE`](LICENSE).

Frappe Framework является отдельным upstream-проектом и зависимостью VEQTA.

## Статус названия

`VEQTA` используется как рабочее имя экосистемы. До масштабного публичного и коммерческого использования бренд требует отдельной проверки naming/trademark availability; лицензия исходного кода не предоставляет автоматически права на чужие товарные знаки и наоборот.