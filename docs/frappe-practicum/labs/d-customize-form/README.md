# Lab D. Customize Form / Custom Field / Property Setter / Export Customizations

Lab D — отдельная лаборатория по штатной кастомизации Standard DocType без изменения его исходного JSON вручную.

Для эксперимента используем уже существующий:

```text
Equipment
```

Временно добавим локальное поле и изменим одно свойство штатного поля.

После лаборатории исходный site и экспортированный файл будут возвращены к базовому состоянию L11. Если эксперимент уже синхронизировали на другой site, его локальные Custom Field / Property Setter очищаются там отдельно — отсутствие записи в exported JSON само по себе не является командой удаления.

Базовая версия: **Frappe Framework v16.32.0**.

---

# 1. Что изучаем

В лаборатории нужны только штатные механизмы Frappe:

```text
Customize Form
Custom Field
Property Setter
Module for Export
Export Customizations
Sync on Migrate
Custom Permissions
bench migrate
```

Главная схема:

```text
Standard DocType
      ↓
Customize Form
      ├── новое поле → Custom Field
      └── изменение свойства штатного поля → Property Setter
                         ↓
                 Export Customizations
                         ↓
           <module>/custom/equipment.json
                         ↓
                    bench migrate
```

Не редактируем:

```text
facility_ops/facility_operations/doctype/equipment/equipment.json
```

ради локальной кастомизации.

---

# 2. Проверить стенд

В терминале:

```bash
cd ~/frappe/facility-ops-bench

bench version
bench --site facility-ops.localhost list-apps

cd apps/facility_ops
git status
```

Нужно подтвердить:

```text
Frappe 16.32.0
facility_ops установлен
working tree clean
```

Developer Mode должен быть включён.

---

# 3. Зафиксировать исходное состояние Equipment

До лаборатории `Equipment` является Standard DocType приложения.

Основные поля:

```text
Equipment Code
Equipment Name
Location
Category
Status
Serial Number
Commissioning Date
Photo
Notes
```

В L11 для `Equipment` уже мог быть создан файл:

```text
facility_ops/facility_operations/custom/equipment.json
```

с экспортированными `Custom DocPerm`.

Проверить:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

ls -l facility_ops/facility_operations/custom/equipment.json
```

Если файл существует, посмотреть его только для чтения:

```bash
sed -n '1,240p' \
  facility_ops/facility_operations/custom/equipment.json
```

Зафиксировать наличие:

```text
"sync_on_migrate": 1
"custom_perms"
```

Не менять JSON руками.

---

# 4. Почему используем Customize Form, а не DocType

`Equipment` — Standard DocType нашего app.

Если мы хотим изменить **саму стандартную модель приложения**, мы редактируем Standard DocType в Developer Mode и изменение попадает в его source JSON.

Если же хотим наложить site/app customization поверх уже существующего Standard DocType, используем:

```text
Customize Form
```

В этой лаборатории специально изучаем второй вариант.

То есть:

```text
DocType editor
= изменить стандартное определение

Customize Form
= наложить Custom Field / Property Setter
```

---

# 5. Открыть Customize Form

Войти как:

```text
Administrator
```

Через Awesomebar открыть:

```text
Customize Form
```

В поле выбора формы выбрать:

```text
Equipment
```

Должна загрузиться текущая мета-модель Equipment.

Не использовать:

```text
Reset All Customizations
```

В нашем учебном приложении уже есть важные custom permissions из L5/L11.

Эта кнопка слишком широкая для точечного эксперимента.

---

# 6. Добавить Custom Field

В Form Builder / Fields добавить новое поле после `Notes`.

Настроить:

```text
Label:        Internal Comment
Field Type:   Small Text
Insert After: Notes
Mandatory:    No
Read Only:    No
Hidden:       No
```

Если Fieldname можно указать явно, использовать:

```text
custom_internal_comment
```

Если оставить его пустым, Frappe сам сформирует fieldname из Label.

Для Custom Field, созданного из `Internal Comment`, ожидается:

```text
custom_internal_comment
```

Сохранить Customize Form через штатную кнопку обновления формы.

---

# 7. Проверить поле на Equipment

Открыть любой существующий `Equipment`.

В форме должно появиться:

```text
Internal Comment
```

Записать тестовое значение:

```text
Lab D local customization
```

Сохранить Equipment.

Открыть другой Equipment.

Поле существует и там, потому что Custom Field меняет metadata DocType, а не один Document.

---

# 8. Найти созданный Custom Field

Через Awesomebar открыть:

```text
Custom Field
```

Отфильтровать:

```text
Document Type = Equipment
Fieldname     = custom_internal_comment
```

Открыть запись.

Проверить минимум:

```text
Document Type = Equipment
Label         = Internal Comment
Field Type    = Small Text
Insert After  = notes
```

Главный вывод:

```text
новая строка в Customize Form
→ отдельный Document типа Custom Field
```

Это не новая строка `DocField` внутри исходного Standard DocType JSON.

---

# 9. Понять изменение схемы

Возвращаться к MariaDB вручную для работы не нужно.

Но важно понимать результат:

```text
Custom Field
→ frappe.db.updatedb("Equipment")
→ физическая колонка custom_internal_comment в tabEquipment
```

То есть Custom Field — это не только визуальное поле формы.

Для обычного не-virtual поля Frappe обновляет схему таблицы.

---

# 10. Изменить свойство штатного поля

Снова открыть:

```text
Customize Form → Equipment
```

Найти штатное поле:

```text
Notes
```

Изменить только Label:

```text
Notes
→ Maintenance Notes
```

Сохранить.

Не менять:

```text
fieldname = notes
fieldtype = Small Text
Permission Level
```

Нам нужен один безопасный пример Property Setter.

---

# 11. Проверить результат в форме

Открыть любой Equipment.

Поле с прежним fieldname:

```text
notes
```

теперь должно отображаться как:

```text
Maintenance Notes
```

Данные старых Equipment не исчезают.

Изменился presentation/meta property, а не смысл хранения поля.

---

# 12. Найти Property Setter

Через Awesomebar открыть:

```text
Property Setter
```

Отфильтровать:

```text
Doc Type   = Equipment
Field Name = notes
Property   = label
```

Открыть запись.

Ожидаем примерно:

```text
Doc Type          = Equipment
DocType or Field  = DocField
Field Name        = notes
Property          = label
Value             = Maintenance Notes
Property Type     = Data
```

Имя Property Setter формируется штатно по схеме:

```text
Equipment-notes-label
```

Главный вывод:

```text
изменение свойства стандартного поля
→ не переписывает исходный DocField
→ создаёт Property Setter
```

---

# 13. Сравнить три слоя metadata

Теперь у нас одновременно есть:

```text
Standard DocType source
        ↓
Equipment

Custom Field
        ↓
custom_internal_comment

Property Setter
        ↓
notes.label = Maintenance Notes
```

При чтении metadata Frappe объединяет их в итоговую форму.

Это и есть причина, почему Customize Form нельзя воспринимать как «редактор исходного DocType».

---

# 14. Проверить Git до Export Customizations

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

git status --short
```

После только UI-кастомизации может не появиться изменения source app, потому что:

```text
Custom Field
Property Setter
```

сначала являются configuration Documents текущего site.

При этом рабочее значение:

```text
Lab D local customization
```

на конкретном Equipment — это working data.

Оно тем более не должно появляться в Git.

---

# 15. Проверить Module for Export

Открыть созданный:

```text
Custom Field → Equipment-custom_internal_comment
```

Найти поле модуля для экспорта, если оно отображается, и установить:

```text
Facility Operations
```

Открыть Property Setter:

```text
Equipment-notes-label
```

Аналогично установить:

```text
Module = Facility Operations
```

Это понадобится при использовании:

```text
Apply Module Export Filter = Yes
```

Для основной лаборатории фильтр не включаем, чтобы не исключить другие существующие customization records Equipment.

---

# 16. Экспортировать Customizations

Открыть:

```text
Customize Form → Equipment
```

Нажать:

```text
Actions
→ Export Customizations
```

В диалоге задать:

```text
Module to Export:             Facility Operations
Sync on Migrate:              Yes
Export Custom Permissions:    Yes
Apply Module Export Filter:   No
```

`Export Custom Permissions = Yes` в этой лаборатории обязателен.

В L11 `equipment.json` уже используется для переноса прав. Если сейчас экспортировать без permissions, файл можно перезаписать версией без `custom_perms`.

Не теряем ранее настроенные права ради лаборатории.

---

# 17. Посмотреть exported equipment.json

В терминале:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

sed -n '1,320p' \
  facility_ops/facility_operations/custom/equipment.json
```

Найти разделы:

```text
"custom_fields"
"property_setters"
"custom_perms"
"sync_on_migrate": 1
```

В `custom_fields` найти:

```text
custom_internal_comment
```

В `property_setters` найти:

```text
notes
label
Maintenance Notes
```

В `custom_perms` должны остаться permissions из L11.

Не редактировать этот JSON руками.

---

# 18. Проверить Git diff

```bash
git status --short
git diff -- \
  facility_ops/facility_operations/custom/equipment.json
```

Теперь отличие важно:

```text
до Export Customizations
→ изменения жили только в site DB

после Export Customizations
→ переносимое описание появилось в app source
```

Но тестовое значение конкретного Equipment:

```text
Lab D local customization
```

в экспортированный metadata-файл не входит.

---

# 19. Зафиксировать эксперимент отдельным commit

```bash
git add \
  facility_ops/facility_operations/custom/equipment.json

git diff --cached

git commit -m "Experiment with Equipment customizations"
```

Этот commit нужен не потому, что customization должна остаться в финальном приложении.

Он нужен, чтобы в Git history был виден полный жизненный цикл механизма.

---

# 20. Проверить Sync on Migrate

На текущем site выполнить:

```bash
cd ~/frappe/facility-ops-bench

bench --site facility-ops.localhost migrate
bench --site facility-ops.localhost clear-cache
```

После migrate проверить Equipment.

Должны сохраниться:

```text
Internal Comment
Maintenance Notes
```

Причина:

```text
custom/equipment.json
+ "sync_on_migrate": 1
→ sync_customizations()
```

---

# 21. Проверить установку customization на clean site

Если clean site из L11 ещё существует:

```text
facility-ops-clean.localhost
```

выполнить:

```bash
cd ~/frappe/facility-ops-bench

bench --site facility-ops-clean.localhost migrate
bench --site facility-ops-clean.localhost clear-cache
```

Открыть Equipment на clean site.

Даже без рабочих Equipment Documents metadata должна содержать:

```text
Internal Comment
Maintenance Notes
```

То есть переносится customization definition, а не данные исходного site.

Зафиксировать, что именно этот clean site **получил эксперимент**. Это понадобится в конце лаборатории для проверки семантики удаления.

---

# 22. Проверить, что Custom Field не является Standard field

На source app посмотреть Standard DocType JSON:

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

grep -n "custom_internal_comment" \
  facility_ops/facility_operations/doctype/equipment/equipment.json
```

Ожидается отсутствие строки.

Затем:

```bash
grep -n "custom_internal_comment" \
  facility_ops/facility_operations/custom/equipment.json
```

Здесь поле должно находиться.

Это наглядная граница:

```text
Standard field
→ doctype/equipment/equipment.json

Custom Field
→ custom/equipment.json
```

---

# 23. Не использовать Reset All Customizations для очистки

В этой лаборатории **не нажимать**:

```text
Reset All Customizations
```

Причина:

`Equipment` уже содержит не только наш эксперимент, но и полезные настройки курса, например permissions L5/L11.

Нам нужен точечный rollback:

```text
удалить только Internal Comment
вернуть только label Notes
```

---

# 24. Вернуть Label стандартного поля

Открыть:

```text
Customize Form → Equipment
```

Найти поле:

```text
Maintenance Notes
```

Вернуть Label:

```text
Notes
```

Сохранить Customize Form.

Frappe сравнит значение с исходным Standard DocField.

Поскольку оно снова совпадает, Property Setter для:

```text
Equipment / notes / label
```

должен быть удалён **на текущем site**.

---

# 25. Проверить удаление Property Setter на исходном site

Открыть:

```text
Property Setter
```

Искать:

```text
Equipment-notes-label
```

Запись больше не должна существовать.

На Equipment снова должно отображаться:

```text
Notes
```

---

# 26. Удалить только Custom Field лаборатории

Открыть:

```text
Customize Form → Equipment
```

Найти:

```text
Internal Comment
```

Удалить эту строку из Form Builder / Fields.

Сохранить Customize Form.

Frappe должен удалить соответствующий:

```text
Custom Field Equipment-custom_internal_comment
```

на текущем site.

Не удалять стандартные поля — Customize Form штатно блокирует такую операцию.

---

# 27. Проверить удаление Custom Field на исходном site

Через `Custom Field` убедиться, что записи:

```text
Equipment-custom_internal_comment
```

больше нет.

Открыть Equipment.

Поля:

```text
Internal Comment
```

быть не должно.

Значение, введённое в лаборатории, больше не доступно через metadata после удаления поля.

---

# 28. Важная граница: удаление metadata и физической колонки

Удаление Custom Field убирает metadata и использование поля.

Но Frappe специально не обязан немедленно физически удалять orphaned database column при обычном удалении Custom Field.

Для физической очистки существует отдельный опасный инструмент:

```text
Customize Form
→ Actions
→ Trim Table
```

Он предупреждает о **необратимой потере данных**.

В базовой лаборатории `Trim Table` **не запускать**.

Достаточно понять разницу:

```text
удалить Custom Field
≠
немедленно DROP COLUMN
```

Работу с Trim Table не превращаем в обязательную часть курса.

---

# 29. Повторно экспортировать базовое состояние Equipment

После точечного rollback снова выполнить:

```text
Customize Form → Equipment
Actions → Export Customizations
```

Параметры:

```text
Module to Export:             Facility Operations
Sync on Migrate:              Yes
Export Custom Permissions:    Yes
Apply Module Export Filter:   No
```

Теперь `equipment.json` должен снова содержать необходимые permissions L11, но не содержать лабораторные:

```text
custom_internal_comment
Equipment-notes-label
Maintenance Notes
```

---

# 30. Проверить cleanup JSON

```bash
cd ~/frappe/facility-ops-bench/apps/facility_ops

grep -nE \
  'custom_internal_comment|Maintenance Notes|Equipment-notes-label' \
  facility_ops/facility_operations/custom/equipment.json
```

Ожидается:

```text
нет совпадений
```

При этом:

```bash
grep -n 'custom_perms' \
  facility_ops/facility_operations/custom/equipment.json
```

должен по-прежнему находить permissions section.

---

# 31. Commit очистки

```bash
git status --short
git diff

git add \
  facility_ops/facility_operations/custom/equipment.json

git diff --cached

git commit -m "Remove Lab D Equipment customizations"

git status
```

Ожидается:

```text
working tree clean
```

Git history теперь показывает:

```text
baseline
→ experiment customization
→ clean rollback
```

---

# 32. Доказать, что Export Customizations не удаляет stale customization на другом site

Этот тест выполняется только если в шаге 21 эксперимент уже был применён к:

```text
facility-ops-clean.localhost
```

После очистки исходного site и повторного экспорта выполнить:

```bash
cd ~/frappe/facility-ops-bench

bench --site facility-ops-clean.localhost migrate
bench --site facility-ops-clean.localhost clear-cache
```

Теперь открыть Equipment на clean site.

Важный результат `v16.32.0`:

```text
отсутствие Custom Field / Property Setter
в новом equipment.json
не является инструкцией удалить уже существующий record на site
```

`sync_customizations()` синхронизирует записи, которые перечислены в файле: создаёт или обновляет Custom Field / Property Setter. Для этих двух типов он не выполняет декларативное удаление всех записей, которых больше нет в JSON.

Поэтому ранее установленный эксперимент на clean site может остаться:

```text
Internal Comment
Maintenance Notes
```

Это **не ошибка migrate**.

Это граница механизма Export Customizations.

---

# 33. Точечно очистить ранее синхронизированный clean site

Если на `facility-ops-clean.localhost` остались лабораторные Custom Field / Property Setter, войти на этот site как Administrator и выполнить тот же точечный rollback:

```text
Customize Form → Equipment
```

1. вернуть:

```text
Maintenance Notes → Notes
```

2. удалить только:

```text
Internal Comment
```

Не использовать:

```text
Reset All Customizations
```

После этого проверить на clean site:

```text
Property Setter Equipment-notes-label отсутствует
Custom Field Equipment-custom_internal_comment отсутствует
Equipment снова показывает Notes
Internal Comment отсутствует
```

Затем ещё раз выполнить:

```bash
bench --site facility-ops-clean.localhost migrate
bench --site facility-ops-clean.localhost clear-cache
```

Лабораторные customization records **не должны появиться снова**, потому что их уже нет и в site DB, и в актуальном exported `equipment.json`.

Именно так выглядит корректная очистка временной customization, которая уже была развёрнута на другом site.

---

# 34. Что должен уметь объяснить студент

После Lab D без подсказки объяснить:

```text
что такое Customize Form;
чем Standard Field отличается от Custom Field;
что создаётся при добавлении нового поля;
что создаётся при изменении свойства штатного поля;
что такое Property Setter;
почему Custom Field хранится отдельно от Standard DocType source;
что делает Export Customizations;
что означает Sync on Migrate;
зачем сохранять Custom Permissions при повторном экспорте;
почему Reset All Customizations опасен на уже настроенном DocType;
почему удаление Custom Field не равно немедленному DROP COLUMN;
почему удаление записи из exported JSON не удаляет автоматически ранее синхронизированный Custom Field / Property Setter на другом site;
чем Export Customizations отличается от fixtures.
```

---

# 35. Финальная приёмка Lab D

Лаборатория пройдена, если выполнено всё:

```text
[ ] открыт Customize Form для Equipment
[ ] создан Custom Field Internal Comment
[ ] подтверждён Custom Field Document
[ ] Notes временно переименован в Maintenance Notes
[ ] подтверждён Property Setter
[ ] Standard equipment.json не редактировался вручную
[ ] выполнен Export Customizations
[ ] equipment.json содержит custom_fields/property_setters/custom_perms во время эксперимента
[ ] bench migrate сохраняет customization
[ ] на clean site customization устанавливается без рабочих Equipment Documents
[ ] Label возвращён к Notes на исходном site
[ ] Property Setter удалён штатно на исходном site
[ ] Custom Field удалён штатно на исходном site
[ ] Trim Table не запускался
[ ] повторный Export Customizations сохранил permissions L11
[ ] лабораторные customization records исчезли из актуального exported JSON
[ ] проверено, что migrate сам не является механизмом удаления stale Custom Field / Property Setter на ранее синхронизированном site
[ ] ранее синхронизированный clean site очищен точечно
[ ] повторный migrate после точечной очистки не возвращает лабораторные customization records
[ ] Git содержит отдельный commit эксперимента и cleanup
[ ] итоговая модель приложения снова не расширена
```

После Lab D постоянное ядро остаётся:

```text
Facility Location
Equipment
Service Request
```

Следующая лаборатория:

```text
Lab E — Print / PDF
```
