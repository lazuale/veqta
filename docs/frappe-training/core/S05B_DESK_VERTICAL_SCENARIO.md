# S05B. Пройти полный сценарий Rental через стандартный Desk

К S05B модель уже собрана:

```text
Equipment
Customer

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

До этого мы проверяли части модели по отдельности.

Теперь нужен другой вопрос:

> Можно ли уже выполнить нормальную рабочую операцию от начала до конца, используя только штатный интерфейс Frappe?

S05B ничего нового не добавляет в предметную модель.

Мы проверяем уже существующую модель через:

```text
Desk
Form View
List View
Awesomebar / поиск
Link controls
Table MultiSelect
filters
```

На этом этапе **не создаются**:

```text
custom frontend
SPA
Workspace ради красивой стартовой страницы
Client Script
custom List JS
custom Form JS
Web Form
Portal
Report
```

Если обычный внутренний CRUD-сценарий уже нормально выражается стандартным Desk, собственного UI пока не требуется.

Связанные документы:

- [`S04_RENTAL_COMPOSITION.md`](S04_RENTAL_COMPOSITION.md);
- [`S05A_RENTAL_STATUS.md`](S05A_RENTAL_STATUS.md);
- [`../PRACTICUM_ROADMAP.md`](../PRACTICUM_ROADMAP.md);
- [`../../frappe-architecture-standard/08_UI_REPORTING.md`](../../frappe-architecture-standard/08_UI_REPORTING.md).

Первичные источники Frappe:

- https://docs.frappe.io/framework/user/en/desk
- https://docs.frappe.io/framework/user/en/api/list
- https://docs.frappe.io/framework/user/en/basics/doctypes

---

# 1. Что именно доказывает S05B

Frappe Desk читает metadata DocType и предоставляет стандартные представления для работы с Documents.

Нас интересует не факт существования экранов, а законченный пользовательский результат:

```text
создать Equipment
→ найти его в Equipment List
→ создать Customer
→ найти его в Customer List
→ создать Rental
→ выбрать созданные/существующие Documents через Links
→ сохранить Rental
→ найти его в List
→ отфильтровать список
→ открыть Rental повторно
→ изменить и снова сохранить
```

Если всё это работает, для текущего внутреннего сценария уже есть полноценный UI.

Архитектурная формула:

```text
business model
→ DocType metadata
→ стандартный Desk
```

а не:

```text
сначала рисуем экран
→ потом подгоняем под него модель
```

---

# 2. Входная проверка

Перейдите в Bench:

```bash
cd ~/frappe/rental-training-bench
```

Проверьте установленные Apps:

```bash
bench --site rental.localhost list-apps -f text
```

Ожидается:

```text
frappe
rental_training
```

Проверьте Git учебного App:

```bash
git -C apps/rental_training status --short
```

После принятого S05A рабочее дерево должно быть чистым.

Это важно для следующей проверки: обычная работа пользователя с бизнес-данными не должна менять source App.

Проверьте наличие metadata:

```bash
test -f apps/rental_training/rental_training/rental_training/doctype/equipment/equipment.json \
  && echo 'Equipment: OK'

test -f apps/rental_training/rental_training/rental_training/doctype/customer/customer.json \
  && echo 'Customer: OK'

test -f apps/rental_training/rental_training/rental_training/doctype/rental/rental.json \
  && echo 'Rental: OK'
```

Ожидается:

```text
Equipment: OK
Customer: OK
Rental: OK
```

---

# 3. Под каким пользователем проходит этап

S05B выполняется под:

```text
Administrator
```

или другим System User, которому уже гарантирован полный доступ к учебным DocTypes.

Это сделано намеренно.

На S05B проверяется **UI и связность модели**, а не permission model.

Поэтому нельзя делать вывод:

> Раз Administrator смог выполнить операцию, значит права приложения настроены правильно.

Реальные роли `Rental Operator` и `Rental Manager` появятся и будут проверяться отдельно на S05D.

То есть:

```text
S05B → пригодность стандартного Desk
S05D → серверные права разных пользователей
```

Это разные ответственности.

---

# 4. Запустить Desk

Если dev server не работает, в отдельном терминале:

```bash
cd ~/frappe/rental-training-bench
bench start
```

Откройте:

```text
http://rental.localhost:8000/app
```

Войдите под `Administrator`.

Для навигации используйте обычный поиск Desk / Awesomebar.

Нам не нужен Workspace только для того, чтобы найти три DocType.

Официальная документация Desk прямо относит Awesomebar к штатной навигации, а Form/List генерирует из metadata DocType.

---

# 5. Создать Equipment через стандартный Form

Через поиск Desk откройте:

```text
Equipment
```

Сначала вы попадёте в обычный Equipment List.

Проверьте, что доступны контрольные записи S02, например:

```text
Bosch GBH 2-26
Canon EOS R50
Lenovo ThinkPad E14
```

Фактические `name` могут отличаться по номеру, если до этого были эксперименты, но формат должен оставаться:

```text
EQ-#####
```

## 5.1. Проверить фильтр существующего реестра

Добавьте стандартный фильтр:

```text
Equipment Type = Camera
```

Ожидается, что в выборке останется оборудование типа Camera.

Снимите фильтр.

## 5.2. Создать новое Equipment специально для вертикального сценария

Нажмите создание нового Equipment.

Заполните:

```text
Equipment Name : Makita DDF487
Equipment Type : Tool
Serial Number  : S05B-MK-0001
```

Сохраните.

Ожидается новый `name` вида:

```text
EQ-#####
```

Запомните его фактический номер.

Вернитесь в Equipment List и найдите запись:

```text
Makita DDF487
```

### Если вы повторно проходите S05B

Не создавайте второй Document с тем же учебным смыслом вслепую. Можно удалить именно свою предыдущую runtime-запись S05B либо использовать явно другой тестовый серийный номер, например:

```text
S05B-MK-0002
```

Критерий этапа — пройти создание через стандартный Form, а не накопить дубли тестовых данных.

### Что здесь важно

Мы не создавали:

```text
Equipment Registry page
Equipment SPA
Equipment search service
```

Обычные Create / Form / List уже предоставлены Desk.

---

# 6. Создать Customer через стандартный Form

Через поиск Desk откройте:

```text
Customer
```

Проверьте наличие контрольных записей S03:

```text
Anna Petrova
Mark de Vries
```

Теперь создайте нового Customer для вертикального сценария:

```text
Customer Name : Sofia Jansen
Phone         : +31 6 10000003
Email         : sofia@example.test
```

Сохраните.

Ожидается `name` вида:

```text
CUST-#####
```

Вернитесь в Customer List и найдите:

```text
Sofia Jansen
```

Откройте её повторно.

На Form ученик должен уметь различить:

```text
системный name     → CUST-#####
отображаемый title → Sofia Jansen
```

Вернитесь в Customer List.

Здесь мы ещё раз видим:

```text
Customer существует сам по себе
Rental позже только ссылается на него
```

---

# 7. Создать Rental полностью через Form

Через поиск Desk откройте:

```text
Rental
```

Нажмите создание нового Document.

Создайте контрольный Rental S05B:

```text
Customer   : Sofia Jansen
Start Date : 2026-09-25
End Date   : 2026-09-27
Status     : Planned
Equipment  :
- Makita DDF487
- Canon EOS R50
```

Так один вертикальный сценарий использует:

```text
Customer, созданного прямо на S05B
Equipment, созданный прямо на S05B
ещё один ранее существующий Equipment
```

Это показывает, что Rental одинаково работает с любыми существующими Documents подходящего DocType.

## Customer

В поле Customer выбирайте `Sofia Jansen` через `Link`.

Пользователь видит человекочитаемый title:

```text
Sofia Jansen
```

но связь относится к настоящему Customer Document с `name` вида:

```text
CUST-#####
```

Не вводите имя клиента в отдельное текстовое поле — такого поля в Rental нет по архитектуре.

## Equipment

В `Equipment` через `Table MultiSelect` выберите:

```text
Makita DDF487
Canon EOS R50
```

Не создавайте текстовый список оборудования вручную.

## Status

Оставьте:

```text
Planned
```

S06 позже будет считать только `Active` блокирующим состоянием. Для вертикальной проверки нам не нужен искусственный конфликт оборудования.

---

# 8. Сохранить Rental

Нажмите **Save**.

Ожидается новый Document с `name` вида:

```text
RENT-#####
```

Запомните его фактический `name`.

Например, на чистом последовательном прохождении это может быть:

```text
RENT-00005
```

Но конкретный номер не является критерием S05B.

Критерий:

```text
name соответствует стратегии RENT-.#####
```

и Document сохраняется обычным Form-путём.

---

# 9. Что мы пока НЕ проверяем этим сохранением

На S05B сохранение Rental **не доказывает**, что уже реализованы все бизнес-инварианты.

Ещё впереди:

```text
S05C
- end_date >= start_date
- нельзя повторить Equipment внутри одного Rental

S06
- нельзя пересекать Active Rentals одного Equipment
```

Поэтому на S05B специально используем нормальные данные.

Не нужно сейчас искать баги, которые должны быть закрыты будущими этапами, и объявлять модель неправильной только потому, что соответствующее правило ещё не реализовано.

---

# 10. Вернуться в Rental List и найти созданную операцию

Откройте Rental List.

Найдите созданный `RENT-#####`.

Проверьте, что список позволяет увидеть рабочие поля, настроенные `In List View`, например:

```text
Customer
Start Date
End Date
Status
```

Фактическое количество видимых колонок зависит от доступной ширины интерфейса, поэтому критерием является не точный пиксельный layout, а то, что эти поля доступны стандартному List и фильтрам.

Официальный List View Frappe предоставляет в том числе:

```text
filters
sorting
paging
```

без отдельного frontend приложения.

---

# 11. Проверить фильтрацию Rental

Сначала фильтр:

```text
Status = Planned
```

Созданный Rental должен входить в результат.

Затем добавьте второй фильтр:

```text
Customer = Sofia Jansen
```

Если в control показывается title, всё равно выбирается настоящий Customer Link.

Получаем смысл:

```text
Rental List
WHERE status = Planned
AND customer = выбранный Customer Document
```

Не нужен отдельный `RentalSearchService` ради обычного поиска по стандартным полям.

Снимите фильтры после проверки.

---

# 12. Открыть Rental повторно из List

Из Rental List откройте только что созданный Document.

Это важная проверка жизненного цикла обычного CRUD:

```text
create
↓
save
↓
list
↓
find
↓
open existing Document
```

Убедитесь, что снова видны:

```text
Customer   : Sofia Jansen
Start Date : 2026-09-25
End Date   : 2026-09-27
Status     : Planned
Equipment  : Makita DDF487, Canon EOS R50
```

То есть Form показывает уже сохранённое состояние Document, а не одноразовую форму ввода.

---

# 13. Проверить обычное редактирование

Измените:

```text
End Date
2026-09-27
→
2026-09-28
```

Сохраните.

Вернитесь в List, затем снова откройте этот Rental.

Проверьте:

```text
End Date = 2026-09-28
```

После проверки верните:

```text
End Date = 2026-09-27
```

и снова сохраните, чтобы контрольный сценарий остался в исходном виде.

### Что мы проверили

```text
Form используется и для создания, и для редактирования Document
```

Для этого не понадобилась собственная edit-page.

---

# 14. Проверить изменение предметного status через тот же Form

Измените у контрольного Rental:

```text
Planned → Active
```

Сохраните.

Вернитесь в Rental List и примените:

```text
Status = Active
```

Rental должен появиться в выборке.

После проверки верните его в:

```text
Planned
```

и сохраните.

Зачем возвращать `Planned`:

- S05B проверяет UI, а не конфликт занятости;
- этот Rental не должен случайно мешать контрольным Active-сценариям S06.

На S05A уже доказано, что такое изменение status пока является обычным редактированием поля, а не Workflow transition.

---

# 15. Проверить, что Link показывает title, но связь не превращается в текст

Откройте контрольный Rental.

Пользователь должен работать с человекочитаемыми значениями:

```text
Sofia Jansen
Makita DDF487
Canon EOS R50
```

Но архитектурно это всё ещё ссылки:

```text
Rental.customer
→ Customer.name = CUST-#####

Rental Item.equipment
→ Equipment.name = EQ-#####
```

Это не новая техническая проверка — она уже была сделана на S04 через console.

На S05B важно другое наблюдение:

> штатный Desk позволяет человеку работать с title, не заставляя бизнес-модель отказаться от стабильных `name`.

То есть удобство UI не требует денормализовать связи в текст.

---

# 16. Проверить границу Child DocType в UI

Попробуйте через Awesomebar найти:

```text
Rental Item
```

У Child DocType нет обычного самостоятельного List View, как у Equipment, Customer или Rental. Frappe генерирует List View для обычных DocTypes, но не для Child Tables и Single DocTypes.

Нормальная пользовательская операция:

```text
открыть Rental
→ изменить набор Equipment внутри Rental
```

а не:

```text
открыть Rental Item registry
→ вести строки отдельно от Rental
```

Это UI-подтверждение решения S04:

```text
Rental Item = child ownership
```

а не независимая бизнес-карточка.

---

# 17. Проверить, что runtime-данные не изменили Git

Это одна из ключевых проверок S05B.

За время этапа мы:

- открывали списки;
- создали новое Equipment;
- создали нового Customer;
- создали Rental;
- меняли поля Rental;
- меняли status;
- работали с Customer и Equipment Links.

Вернитесь в терминал:

```bash
cd ~/frappe/rental-training-bench

git -C apps/rental_training status --short
```

Ожидается:

```text
<пусто>
```

То есть рабочее дерево App остаётся чистым.

Почему это важно:

```text
DocType metadata / controller / обязательная config
= состояние App
= Git

конкретный RENT-#####
конкретный CUST-#####
конкретный EQ-#####
= runtime / transaction data Site
= не source App
```

Обычная эксплуатация приложения не должна создавать source changes.

Это различие понадобится на S08 при аудите доставки состояния App.

---

# 18. Не путать Site data с fixtures

После S05B может возникнуть соблазн экспортировать созданные:

```text
Makita DDF487
Sofia Jansen
RENT-#####
```

как fixtures, чтобы на следующем Site «всё сразу было заполнено».

Не делайте этого.

Это учебные/операционные данные конкретного Site, а не обязательная конфигурация продукта.

Fixtures позже будут использоваться только там, где объект действительно является обязательной конфигурацией App — например для согласованных Role.

Формула:

```text
данные для работы пользователя
≠
обязательная конфигурация App
```

---

# 19. Почему не нужен Workspace на этом этапе

Workspace может быть полезен, если появляется требование:

> пользователю нужна собранная стартовая рабочая область с нужными ссылками, блоками и информацией.

Но S05B требует только пройти рабочий CRUD-путь.

Awesomebar и стандартная навигация уже позволяют открыть нужные DocTypes.

Поэтому сейчас:

```text
Workspace = не ошибка
Workspace = просто ещё не требуется
```

Он остаётся отдельной веткой `R17 / NEXT`.

---

# 20. Почему не нужен custom frontend

Мы уже можем:

```text
создать
прочитать
найти
отфильтровать
изменить
связать Documents
```

через стандартный Desk.

Следовательно, аргумент:

> «Нужно написать frontend, потому что приложению нужен интерфейс»

на текущем уровне неверен.

Собственный frontend станет оправдан, если появится требование, которое стандартный Desk семантически или UX-функционально не закрывает.

Например:

```text
публичный специализированный пользовательский путь
сильно специализированное рабочее место
особая визуализация
клиентское приложение вне Desk
```

Но это отдельные требования.

---

# 21. Чего S05B не доказывает

После успешного этапа нельзя утверждать, что приложение уже полностью готово.

S05B **не проверяет**:

```text
server invariants
permissions разных ролей
конкурентное бронирование
clean install
миграции
автоматические тесты
public UI
```

Он доказывает только конкретный контракт:

> Уже существующая CORE-модель пригодна для полного внутреннего пользовательского сценария через штатный Desk.

Это важно, потому что мы не смешиваем один успешный UI-сценарий с доказательством всех слоёв архитектуры.

---

# 22. Три типовые ошибки

## Ошибка 1. Сразу писать SPA

```text
требование: CRUD Equipment/Customer/Rental
решение: React/Vue frontend
```

Проблема: стандартный Desk ещё не был даже проверен.

Правильнее:

```text
обычная внутренняя работа
→ сначала Desk Form/List
```

## Ошибка 2. Делать отдельные страницы для каждого списка

```text
Equipment Registry page
Customer Registry page
Rental Registry page
```

только ради обычной фильтрации и открытия записей.

Frappe уже генерирует List View для обычных DocTypes.

## Ошибка 3. Считать UI безопасностью

Под Administrator всё работает — и ученик заключает, что роли настроены.

Нет.

UI usability проверяется на S05B.

Authorization проверяется отдельно на S05D.

---

# 23. Три правильных решения

## Правильно 1. Form для одного Document

Equipment, Customer и Rental — самостоятельные Documents, поэтому стандартный Form является естественным первым представлением каждого из них.

## Правильно 2. List для реестра Documents

Требование:

```text
найти и отфильтровать записи
```

сначала проверяется штатным List.

## Правильно 3. Title отдельно от identity

Пользователь видит:

```text
Sofia Jansen
```

но модель сохраняет Link на стабильный:

```text
CUST-#####
```

UI остаётся удобным без разрушения identity модели.

---

# 24. Контрольная карта S05B

Ученик должен пройти без собственной разработки интерфейса:

```text
[ ] открыть Equipment List
[ ] отфильтровать Equipment
[ ] создать новое Equipment через Form
[ ] найти созданное Equipment в List
[ ] открыть Customer List
[ ] создать нового Customer через Form
[ ] найти созданного Customer в List
[ ] открыть Customer повторно
[ ] открыть Rental List
[ ] создать Rental
[ ] выбрать созданного Customer через Link
[ ] выбрать созданный и существующий Equipment через Table MultiSelect
[ ] сохранить Rental
[ ] найти его в List
[ ] отфильтровать Rental по status
[ ] отфильтровать Rental по Customer
[ ] открыть сохранённый Rental повторно
[ ] изменить End Date и сохранить
[ ] изменить status и проверить List
[ ] вернуть контрольные значения
[ ] убедиться, что Git App остаётся чистым
```

---

# 25. ГОТОВО

S05B принят, если одновременно выполнено всё ниже.

## Пользовательский сценарий

Через стандартный Desk можно выполнить:

```text
Create Equipment
   ↓
Equipment List
   ↓
Create Customer
   ↓
Customer List
   ↓
Create Rental
   ├── Customer Link
   ├── Date fields
   ├── status
   └── Equipment MultiSelect
   ↓
Save
   ↓
List
   ↓
Filter
   ↓
Reopen
   ↓
Edit
```

## Модель

Ученик объясняет:

```text
Form = представление одного Document
List = реестр Documents
Link = связь, а не копия текста
Table MultiSelect = набор Links через child-table model
Desk следует за DocType metadata
```

## Владение состоянием

После создания и редактирования бизнес-записей:

```bash
git -C apps/rental_training status --short
```

остаётся пустым.

Ученик объясняет:

```text
App source ≠ runtime data Site
```

## Архитектурная граница

Не добавлены только ради UI:

```text
Workspace
Client Script
custom JS
custom Page
SPA
Web Form
Portal
```

---

# 26. НЕ ГОТОВО

S05B не принят, если:

- полный сценарий нельзя пройти Equipment → Customer → Rental стандартными Form/List;
- основной сценарий требует ручного SQL;
- Customer или Equipment копируются в Rental текстом вместо Link;
- для обычного CRUD пришлось писать собственный frontend без отдельного требования;
- `Rental Item` ведётся пользователем как самостоятельная карточка;
- обычная работа с runtime Documents неожиданно меняет source App;
- Administrator используется как доказательство корректных permissions;
- для прохождения этапа добавлены Workspace/Client Script/custom Page только ради демонстрации возможностей.

---

# 27. Что должно остаться после S05B

Предметная модель не изменилась:

```text
Equipment
Customer
Rental
└── Rental Item
```

App source после принятого S05A тоже не изменился.

На учебном Site появились только новые runtime Documents S05B:

```text
Equipment: Makita DDF487
Customer : Sofia Jansen
Rental   : RENT-##### [Planned]
```

Главный результат:

```text
CORE-модель уже полезна через штатный Frappe Desk
```

Следующая независимая ветка — S05C.

На ней впервые появляется собственная серверная логика Rental, потому что возникает реальный инвариант:

```text
end_date >= start_date
Equipment не повторяется внутри одного Rental
```

То есть переход к Python произойдёт не потому, что «мы уже закончили low-code», а потому что появилась новая ответственность, которую metadata сама по себе не гарантирует.
