# S05A. Добавить предметный status Rental и не перепутать его с Workflow/docstatus

После S04 у нас уже существует рабочая связанная модель:

```text
Rental
├── customer   → Link → Customer
├── start_date → Date
├── end_date   → Date
└── items      → Table MultiSelect → Rental Item
                                     └── equipment → Link → Equipment
```

Но пока система не умеет ответить на простой предметный вопрос:

> Этот Rental только запланирован, оборудование уже выдано или прокат уже завершён?

Это **новая ответственность** — хранить текущее бизнес-состояние Rental.

Для неё в CORE достаточно обычного поля:

```text
status : Select
```

со значениями:

```text
Planned
Active
Returned
```

На этом этапе мы намеренно **не** используем:

```text
Workflow
Is Submittable
docstatus как бизнес-статус
отдельный Rental Status DocType
Python-логику переходов
```

Связанные документы:

- [`S04_RENTAL_COMPOSITION.md`](S04_RENTAL_COMPOSITION.md);
- [`../CORE_STAGE_SPECIFICATION.md`](../CORE_STAGE_SPECIFICATION.md);
- [`../REQUIREMENTS_MATRIX.md`](../REQUIREMENTS_MATRIX.md);
- [`../PRACTICUM_ROADMAP.md`](../PRACTICUM_ROADMAP.md);
- [`../../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md`](../../frappe-architecture-standard/03_DOCUMENT_LIFECYCLE.md).

---

# 1. Входная проверка

Перейдите в Bench:

```bash
cd ~/frappe/rental-training-bench
```

Проверьте Site:

```bash
bench --site rental.localhost list-apps -f text
```

Ожидается:

```text
frappe
rental_training
```

Проверьте, что Rental уже существует как App-owned Standard DocType:

```bash
test -f \
  apps/rental_training/rental_training/rental_training/doctype/rental/rental.json \
  && echo 'Rental metadata: OK'
```

Проверьте Git:

```bash
git -C apps/rental_training status --short
```

После принятого S04 рабочее дерево должно быть чистым.

---

# 2. Сначала сформулировать смысл состояния

Нам нужны три предметных состояния.

## `Planned`

Rental создан, но оборудование ещё не считается фактически выданным.

В дальнейшем CORE будет считать `Planned` неблокирующим состоянием для проверки занятости Equipment.

## `Active`

Прокат фактически идёт.

Именно `Active` позднее будет участвовать в междокументном правиле:

```text
одно Equipment
не может находиться
в двух пересекающихся Active Rentals
```

## `Returned`

Прокат завершён, Equipment возвращено.

### Что это пока НЕ означает

`Returned` не означает автоматически:

```text
docstatus = 1
Submitted
запрет редактирования
обязательный маршрут согласования
```

На S05A это просто предметное состояние.

---

# 3. Развести три понятия

Это центральная проверка этапа.

## Бизнес-статус

Отвечает:

> Что сейчас происходит с Rental?

Наш ответ:

```text
Planned
Active
Returned
```

Первый штатный механизм — обычный `Select`.

## Workflow

Отвечает на другой вопрос:

> Кто, из какого состояния, в какое состояние и при каких условиях имеет право перейти?

На S05A такого требования нет.

Мы пока **не говорим**:

```text
только Manager может Active → Returned
Operator не может Planned → Active
Returned нельзя вернуть в Planned
```

Следовательно, Workflow пока не нужен.

## docstatus

Отвечает на системный транзакционный lifecycle:

```text
0 = Draft
1 = Submitted
2 = Cancelled
```

Rental в CORE пока не является Submittable Document.

Поэтому даже Rental с:

```text
status = Returned
```

остаётся обычным Draft Document в системном смысле:

```text
docstatus = 0
```

Главная формула этапа:

```text
business status ≠ Workflow ≠ docstatus
```

Эти механизмы могут взаимодействовать в других приложениях, но не заменяют друг друга.

---

# 4. Почему не отдельный `Rental Status` DocType

Наш набор сейчас:

```text
Planned
Active
Returned
```

У элементов нет собственных:

```text
permissions
описаний, которыми управляют пользователи
SLA
цветов как бизнес-данных
правил эскалации
внешних идентификаторов
жизненного цикла
```

Поэтому отдельный справочник дал бы новую сущность без новой ответственности.

Текущее решение:

```text
малый стабильный набор
→ Select
```

Если требования изменятся, модель можно пересмотреть позже.

---

# 5. Открыть существующий Standard DocType Rental

Если dev server не запущен:

```bash
cd ~/frappe/rental-training-bench
bench start
```

Откройте Desk:

```text
http://rental.localhost:8000/app
```

Через поиск Desk откройте:

```text
DocType
```

Найдите и откройте:

```text
Rental
```

Не создавайте новый Custom Field через Customize Form.

Мы изменяем **Standard DocType собственного App**, поэтому его metadata должна измениться в source `rental_training`.

---

# 6. Добавить поле Status

В `Rental` добавьте поле после `End Date` и перед `Equipment`.

Используйте:

```text
Label        : Status
Fieldname    : status
Type         : Select
Mandatory    : yes
In List View : yes
Default      : Planned
```

Options — по одному значению на строку:

```text
Planned
Active
Returned
```

Итоговый порядок основной части Rental:

```text
Customer
Start Date
End Date
Status
Equipment
```

Нажмите **Save**.

---

# 7. Проверить metadata в App source

Вернитесь в терминал:

```bash
cd ~/frappe/rental-training-bench
```

Поскольку `rental.json` уже существовал и был tracked Git, изменение должно быть видно обычным diff:

```bash
git -C apps/rental_training status --short
```

Ожидайте изменение существующего файла Rental metadata.

Посмотрите diff:

```bash
git -C apps/rental_training diff -- \
  rental_training/rental_training/doctype/rental/rental.json
```

Найдите добавленное поле с семантикой:

```text
fieldname = status
fieldtype = Select
options   = Planned / Active / Returned
default   = Planned
reqd      = 1
in_list_view = 1
```

Точный порядок JSON-ключей не является контрактом практикума.

Контракт:

```text
изменение Standard DocType
→ изменение App-owned metadata
→ Git видит изменение
```

---

# 8. Не предполагать, что default переписал старые Documents

На S04 уже мог быть создан Rental до появления поля `status`.

Не делайте вывод:

> Раз у нового поля `Default = Planned`, значит все старые записи гарантированно уже стали Planned.

Default определяет значение по умолчанию для обычного нового ввода. Миграция существующих бизнес-данных — отдельный вопрос, который всегда нужно проверять по фактическому состоянию данных и характеру изменения схемы.

Для нашего учебного Site просто проверьте существующие Rentals.

Откройте Rental List и существующую запись S04.

Если `Status` пустой, задайте:

```text
Planned
```

и сохраните запись.

Не пишите patch ради одной учебной записи dev-site.

Позже, когда практикум дойдёт до миграций, мы отдельно разберём разницу между:

```text
новая metadata/schema
и
преобразование существующих данных
```

---

# 9. Создать три наблюдаемых состояния

Нам пока не нужно создавать сложный набор ошибок. На S05A проверяется только модель состояния.

Создайте или используйте Rentals так, чтобы в List были представлены:

```text
Planned
Active
Returned
```

Можно использовать разные Customers и Equipment.

На этом этапе **нет** проверки пересечения Active Rentals. Она появится позже, после серверных инвариантов.

Поэтому не делайте вывод, что сохранение двух конфликтующих Active Rentals уже является правильным production-поведением — соответствующее правило просто ещё не реализовано.

---

# 10. Проверить List View

Откройте Rental List.

Проверьте, что `Status` виден как колонка, если стандартный List layout его показывает в доступной ширине.

Главная проверка — фильтры.

Добавьте фильтр:

```text
Status = Active
```

Убедитесь, что остаются только Active Rentals.

Затем:

```text
Status = Returned
```

Так мы подтверждаем, что status является обычным полем модели и участвует в стандартных возможностях List без собственного UI.

---

# 11. Проверить `status` и `docstatus` рядом

Это самая важная техническая проверка этапа.

Откройте Bench console:

```bash
cd ~/frappe/rental-training-bench
bench --site rental.localhost console
```

Выполните:

```python
frappe.get_all(
    "Rental",
    fields=["name", "status", "docstatus"],
    order_by="creation asc",
)
```

Для обычных Rentals вы должны увидеть смысл примерно такой:

```text
RENT-...  Planned   0
RENT-...  Active    0
RENT-...  Returned  0
```

Ключевая часть:

```text
status меняется
но docstatus остаётся 0
```

Выйдите:

```python
exit()
```

Это наглядное доказательство, что два состояния существуют на разных уровнях модели.

---

# 12. Проверить свободу переходов — и правильно её интерпретировать

Откройте один Rental и измените:

```text
Planned → Active
```

Сохраните.

Затем:

```text
Active → Returned
```

Сохраните.

Если хотите, попробуйте вернуть:

```text
Returned → Planned
```

На S05A Framework не обязан это запрещать.

Почему?

Потому что мы пока сформулировали только требование:

> хранить текущее состояние.

Мы ещё **не сформулировали** требование:

> ограничивать допустимые переходы и роли переходов.

Это принципиальная разница между:

```text
поле состояния
```

и:

```text
политика переходов
```

Если позднее появится реальное требование согласования/ограничения переходов, тогда будет проверяться Workflow или серверная предметная логика по её семантике.

---

# 13. Почему не `Is Submittable`

Откройте DocType `Rental` и убедитесь:

```text
Is Submittable : OFF
```

На этом этапе Rental остаётся редактируемым рабочим объектом.

Нам ещё не сказано:

```text
выдача после подтверждения становится зафиксированным фактом;
ключевые поля после фиксации менять нельзя;
ошибочный факт нужно отменять через Cancel/Amend.
```

Без такой семантики `docstatus` был бы выбран только из-за внешнего сходства:

```text
Returned ≈ Done
```

а это неправильный мотив.

---

# 14. Зафиксировать изменение в Git

Проверьте diff ещё раз:

```bash
cd ~/frappe/rental-training-bench/apps/rental_training

git diff -- \
  rental_training/rental_training/doctype/rental/rental.json
```

Добавьте metadata:

```bash
git add rental_training/rental_training/doctype/rental/rental.json
```

Проверьте staged diff:

```bash
git diff --cached -- \
  rental_training/rental_training/doctype/rental/rental.json
```

Сделайте checkpoint:

```bash
git commit -m "feat: add rental business status"
```

Проверьте:

```bash
git status --short
```

Ожидается чистое рабочее дерево.

---

# 15. Типовые неправильные решения

## Ошибка 1. Создать Workflow просто потому, что статусов три

```text
Planned → Active → Returned
```

само по себе не доказывает необходимость Workflow.

Нужны отдельные требования к переходам, ролям или условиям.

## Ошибка 2. Сделать Rental Submittable ради `Returned`

```text
Returned ≠ Submitted
```

Бизнес-состояние и транзакционный lifecycle отвечают на разные вопросы.

## Ошибка 3. Использовать `docstatus` вместо status

Системные значения:

```text
Draft / Submitted / Cancelled
```

не являются названием стадий нашего проката.

## Ошибка 4. Создать `Rental Status` DocType

Три стабильных значения без собственной модели не требуют нового самостоятельного Document.

## Ошибка 5. Хранить status только визуально

Цвет карточки, индикатор или положение в UI не заменяют поле модели, если состояние является бизнес-данными.

## Ошибка 6. Сразу писать Python-переходы

На S05A нет ни одного правила перехода, которое нужно гарантировать сервером.

Собственный код без новой ответственности будет преждевременным.

---

# 16. Что должно быть понятно после S05A

Ученик должен уметь объяснить без формулировки «потому что так написано в инструкции»:

```text
Почему status = Select?
→ нужен малый стабильный набор предметных состояний.

Почему не Workflow?
→ пока нет требований к разрешённым переходам, ролям и условиям.

Почему не docstatus?
→ Rental пока не моделируется как submittable транзакционный факт.

Почему не Rental Status DocType?
→ значения пока не имеют самостоятельной модели.

Почему Returned остаётся docstatus = 0?
→ бизнес-состояние и системный transactional lifecycle различны.
```

---

# 17. ГОТОВО

S05A принят, если одновременно выполнено всё:

- в Standard DocType `Rental` есть `status : Select`;
- значения ровно `Planned / Active / Returned`;
- `Default = Planned`;
- поле mandatory;
- поле доступно для стандартной фильтрации/List-сценария;
- `Workflow` для Rental не создан;
- `Is Submittable = OFF`;
- ученик показал рядом `status` и `docstatus` через серверный API/console;
- Rental с `status = Returned` всё ещё имеет `docstatus = 0`;
- изменение metadata находится в Git App;
- Git checkpoint сделан;
- ученик может объяснить различие `status / Workflow / docstatus`.

---

# 18. НЕ ГОТОВО

Этап не принят, если:

- Workflow появился только ради демонстрации Workflow;
- `Returned` реализован через Submitted;
- `status` хранится только как UI-состояние;
- создан отдельный `Rental Status` без самостоятельного смысла;
- для обычного изменения status уже написан собственный движок переходов без требования;
- обязательное поле создано как локальный Custom Field и не попало в App metadata;
- существующие записи молча считаются мигрированными без фактической проверки;
- ученик не может объяснить, почему `status = Returned` и `docstatus = 0` не противоречат друг другу.

---

# 19. Контрольная точка

После S05A модель выглядит так:

```text
Rental
├── customer   → Link → Customer
├── start_date → Date
├── end_date   → Date
├── status     → Select
│                ├── Planned
│                ├── Active
│                └── Returned
└── items      → Table MultiSelect → Rental Item
                                     └── equipment → Link → Equipment
```

И отдельно:

```text
Rental.status    = предметное состояние
Rental.docstatus = 0 Draft для обычного несабмиттируемого Document
Workflow         = отсутствует
```

На этой точке модель уже знает **что происходит с Rental**, но ещё не содержит собственных серверных инвариантов и permission model.

После P04 ветки остаются независимыми. Поэтому дальше можно писать S05B, S05C и S05D как отдельные результаты, не изображая между ними выдуманную архитектурную зависимость.