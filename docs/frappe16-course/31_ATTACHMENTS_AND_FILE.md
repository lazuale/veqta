# 31. Attachments и File

Во Frappe файл — это не просто «кусок данных, лежащий рядом с документом».

Когда пользователь прикрепляет PDF, фотографию или таблицу, Framework обычно работает сразу с двумя вещами:

```text
само содержимое файла
        +
Document типа File
```

`File` хранит сведения о файле и его связи с другими документами.

Сам бинарный файл при стандартном локальном хранении лежит в файловой системе Site.

Проверено: **2026-08-31**.

---

## 1. Самый простой пример

Есть документ:

```text
Request REQ-0001
```

Пользователь прикрепляет:

```text
invoice.pdf
```

В упрощённом виде получается:

```text
Request REQ-0001
        ↑
        │ attached_to_doctype = Request
        │ attached_to_name    = REQ-0001
        │
File
├── file_name = invoice.pdf
├── file_url
├── is_private
├── file_size
├── file_type
└── content_hash
```

Главная мысль:

> **вложения во Frappe представлены отдельными Documents типа `File`.**

Исходный `Request` не обязан хранить внутри себя байты PDF.

---

## 2. Что такое `File`

`File` — системный DocType Framework.

В актуальном v16 среди его основных полей есть:

```text
file_name
file_url
file_size
file_type
is_private
folder
attached_to_doctype
attached_to_name
attached_to_field
content_hash
thumbnail_url
```

Для обычной работы новичку важнее всего понимать пять из них:

| Поле | Что означает |
|---|---|
| `file_name` | имя файла для человека |
| `file_url` | адрес, по которому Framework обращается к файлу |
| `is_private` | публичный файл или защищённый |
| `attached_to_doctype` | к какому типу документа прикреплён файл |
| `attached_to_name` | к какой конкретной записи он прикреплён |

Например:

```text
file_name           = invoice.pdf
file_url            = /private/files/invoice.pdf
is_private          = 1
attached_to_doctype = Request
attached_to_name    = REQ-0001
```

---

## 3. `file_url` — это не содержимое файла

Представим поле:

```text
attachment = /private/files/invoice.pdf
```

Строка:

```text
/private/files/invoice.pdf
```

не является самим PDF.

Это только ссылка на файл.

Поэтому удобно разделять:

```text
File.file_url
→ где Framework ищет файл

содержимое файла
→ реальные байты PDF, PNG, XLSX и т. д.
```

Это особенно важно, когда позже появятся API, внешнее файловое хранилище и резервное копирование.

---

## 4. Где лежат файлы при стандартном локальном хранении

Для обычного self-hosted Site Framework использует две основные директории.

Публичные файлы:

```text
frappe-bench/sites/<site>/public/files/
```

Их URL обычно выглядит так:

```text
/files/example.pdf
```

Приватные файлы:

```text
frappe-bench/sites/<site>/private/files/
```

Их URL выглядит так:

```text
/private/files/example.pdf
```

То есть:

```text
is_private = 0
→ /files/...

is_private = 1
→ /private/files/...
```

---

## 5. Но `File` не надо жёстко связывать только с локальным диском

Стандартная реализация пишет файл в файловую систему Site.

Но в v16 сохранение проходит через hook `write_file`.

Упрощённо:

```text
сохранить File
      ↓
есть custom write_file hook?
      ├── да → использовать его
      └── нет → сохранить в стандартную файловую систему
```

Есть и соответствующий hook для удаления содержимого.

Это означает, что приложение может заменить стандартный backend хранения своим.

Поэтому правильная модель такая:

```text
File
→ метаданные и логическая запись файла

storage backend
→ где физически лежит содержимое
```

А не:

```text
File всегда означает конкретный файл на локальном диске
```

---

## 6. Public и Private — принципиально разные режимы

### Public

Для публичного файла:

```text
is_private = 0
file_url = /files/...
```

Он предназначен для публичного чтения.

В permission-коде v16 `read` и `select` для непубличного? Нет — именно для **неприватного** файла разрешаются сразу:

```text
if not doc.is_private and ptype in ("read", "select"):
    return True
```

Практический вывод:

> **не делай файл Public, если его должен защищать доступ к родительскому документу.**

Даже если сам `Request` доступен только ограниченной роли, публичный `/files/...` уже не следует этой модели доступа.

### Private

Для приватного файла:

```text
is_private = 1
file_url = /private/files/...
```

Frappe проверяет право пользователя на файл.

Если File прикреплён к документу, permission controller связывает доступ к File с доступом к родительскому Document.

Упрощённо:

```text
Private File
     ↓
attached to Request REQ-0001
     ↓
можно Read Request?
     ↓
можно читать attachment
```

Для операций изменения файла проверка связана с `write` родительского документа.

---

## 7. Read документа и Read файла

Официальная документация формулирует основное правило просто:

> пользователь с Read-доступом к документу может получить доступ к прикреплённым к нему файлам.

Но это имеет смысл именно для защищённых вложений.

Сводка:

| Ситуация | Основная модель |
|---|---|
| Public File | читается публично |
| Private File, прикреплённый к Document | Read обычно наследуется от родительского Document |
| Private File без родительского Document | доступ определяется самим File, например владельцем |

Также в v16 учитываются владелец File и явный Sharing самого File.

---

## 8. Чтобы прикрепить файл, обычно нужен Write родительского документа

Стандартный endpoint загрузки перед созданием File вызывает проверку записи целевого документа.

Для уже существующего Document логика примерно такая:

```text
хочу загрузить файл в Request REQ-0001
        ↓
есть Write на REQ-0001?
        ↓
да
        ↓
можно продолжать upload
```

Поэтому обычный пользователь с одним только `Read` не должен автоматически получать возможность менять набор вложений документа.

Это логично:

```text
Read
→ посмотреть документ и его защищённые вложения

Write
→ изменять документ и управлять его вложениями
```

---

## 9. Sidebar Attachment и поле `Attach` — не одно и то же

Есть два очень похожих сценария.

### Обычное вложение документа

Пользователь прикладывает файл через attachments-интерфейс формы.

Связь может выглядеть так:

```text
File
├── attached_to_doctype = Request
├── attached_to_name = REQ-0001
└── attached_to_field = пусто
```

Файл относится к документу вообще.

### Поле `Attach`

В DocType есть конкретное поле:

```text
Contract File
Field Type: Attach
Fieldname: contract_file
```

Тогда пользователь видит на форме отдельное место для конкретного файла.

Значением поля становится URL, например:

```text
/private/files/contract.pdf
```

А соответствующий `File` может хранить:

```text
attached_to_doctype = Request
attached_to_name    = REQ-0001
attached_to_field   = contract_file
```

То есть `attached_to_field` помогает понять, через какое поле был прикреплён File.

---

## 10. Поле `Attach` не содержит бинарник

Это одна из самых важных вещей главы.

Допустим, в `Request` есть:

```text
contract_file
```

В базе значение этого поля будет похоже не на PDF-данные, а на:

```text
/private/files/contract.pdf
```

Поэтому:

```text
Attach field
→ хранит ссылку

File Document
→ описывает файл

storage
→ хранит содержимое
```

Не надо пытаться проектировать DocType так, будто `Attach` — это BLOB-поле с содержимым файла.

---

## 11. `Attach Image`

`Attach Image` использует ту же основную модель файла, но интерфейс ориентирован на изображения.

Например:

```text
photo
Field Type: Attach Image
```

Значением всё так же будет путь/URL к файлу.

Разница в основном в поведении интерфейса и отображении изображения, а не в появлении какого-то отдельного хранилища картинок.

---

## 12. Attachment Gallery в v16

В актуальном v16 есть отдельный Field Type:

```text
Attachment Gallery
```

Он показывает прикреплённые к текущему Document файлы как галерею.

Для изображений используются превью, другие типы показываются карточками файлов.

По умолчанию Gallery может показать все attachments текущего Document.

Также можно ограничить выбор через Filters.

Например, только PDF:

```text
[["File", "file_type", "=", "PDF"]]
```

Или только файлы, относящиеся к определённому полю:

```text
[["File", "attached_to_field", "=", "marketing_assets"]]
```

Это всё ещё обычные `File` Documents. Gallery — только другой штатный интерфейс работы с ними.

---

## 13. Один файл может существовать как несколько File Documents

Внутри `File` есть:

```text
content_hash
```

При загрузке локального файла v16 вычисляет hash содержимого.

Если уже найден File с тем же содержимым и тем же режимом `is_private`, Framework может переиспользовать существующий `file_url` вместо записи ещё одной физической копии.

В результате возможна модель:

```text
File A ─┐
        ├── /private/files/document.pdf
File B ─┘
```

То есть:

> два `File` Documents не обязательно означают две физические копии одинаковых байтов.

---

## 14. Что тогда происходит при удалении одного File

Frappe проверяет, используется ли тот же `content_hash` другими File-записями.

Если физическое содержимое больше никем не используется:

```text
удалить File
→ удалить физический файл
```

Если другой File всё ещё ссылается на то же содержимое:

```text
удалить File A
→ File B остаётся
→ общие байты не надо уничтожать
```

Это ещё одна причина не воспринимать File Document и физический файл как строго одно и то же.

---

## 15. Удаление attachment оставляет событие в Timeline

После обычного прикрепления v16 создаёт служебный Comment типа:

```text
Attachment
```

При удалении:

```text
Attachment Removed
```

Поэтому пользователь может увидеть соответствующие события в Timeline.

Но, как мы уже знаем из главы 29:

```text
Timeline event
≠ текущее состояние attachment
```

Текущий attachment — это `File`.

Timeline только показывает, что с ним происходило.

---

## 16. `Max Attachments`

У DocType есть настройка:

```text
Max Attachments
```

Например:

```text
Request
Max Attachments = 5
```

Тогда Framework считает уже связанные `File` Documents по:

```text
attached_to_doctype
attached_to_name
```

и не позволит превысить заданный предел.

Это ограничение количества файлов на один документ, а не размера каждого файла.

---

## 17. Ограничение размера файла

Здесь есть важное отличие между текущей документацией и исходниками v16.

Страница документации Attachments всё ещё говорит о стандартном лимите:

```text
10 MB
```

Но актуальная ветка `version-16` в `get_max_file_size()` использует порядок:

```text
System Settings: max_file_size
        ↓ если не задано
site config: max_file_size
        ↓ если не задано
25 MiB
```

Поэтому для поведения **текущего v16** в этом учебнике считаем точным именно исходный код:

```text
fallback = 25 MiB
```

а не старое число из страницы документации.

Главное практическое правило всё равно простое:

> лимит нужно проверять на конкретном Site, а не заучивать число из старой статьи.

---

## 18. Public ↔ Private можно переключить

Для локального файла при изменении `is_private` Framework переносит файл между каталогами.

Например:

```text
/files/report.pdf
```

становится:

```text
/private/files/report.pdf
```

или наоборот.

При этом обновляется `file_url`.

Если исходный File был связан с Attach-полем, v16 также умеет обновить значение соответствующего поля родительского документа на новый URL.

Это важно, потому что путь является частью значения Attach field.

---

## 19. Remote File

`File` может описывать не только локально загруженное содержимое.

Например, пользователь может прикрепить Web Link:

```text
https://example.com/manual.pdf
```

Для такого File:

```text
file_url = https://example.com/manual.pdf
```

а сам PDF не обязан копироваться в локальный `sites/.../files`.

В текущем controller URL, начинающиеся с:

```text
http://
https://
/api/method/
```

обрабатываются как remote file URL.

Поэтому опять правильная модель:

```text
File
→ запись о файле/ресурсе

file_url
→ способ добраться до содержимого
```

---

## 20. File Manager

Frappe предоставляет штатный File Manager.

Из интерфейса можно работать с уже загруженными файлами и папками.

Официальная документация указывает путь через Files / File Manager.

Это полезно, когда нужно:

- найти загруженный ранее файл;
- повторно прикрепить существующий файл;
- работать с папками;
- импортировать ZIP;
- экспортировать набор файлов ZIP-архивом.

Но папки File Manager — это организация файлов внутри Frappe, а не новая бизнес-модель документов.

---

## 21. Можно прикрепить уже существующий File

Стандартный uploader поддерживает выбор файла из библиотеки.

То есть не обязательно каждый раз загружать одни и те же байты заново.

Логика:

```text
файл уже есть в File Manager
        ↓
выбрать его
        ↓
создать attachment для другого Document
```

В v16 для эффективного копирования attachment есть и серверная логика, способная создать новый File Document, переиспользовав существующий `file_url`.

---

## 22. Защита attachments у Submitted документов

В актуальном v16 у DocType есть дополнительная настройка:

```text
Protect Attached Files
```

Она важна для документов с lifecycle Submit/Cancel.

Идея такая:

```text
Draft
→ неправильное вложение ещё можно исправить

Submitted + Protect Attached Files
→ удалить attachment нельзя как обычную редактируемую деталь
```

После Cancel удаление снова возможно только при выполнении соответствующих проверок, включая право Delete на связанный документ.

Это полезно, когда вложения являются частью зафиксированного Submitted Document.

---

## 23. Public File не становится Private из-за родительского документа

Очень опасная ошибка:

```text
Request закрыт правами
→ значит всё, что к нему приложено, тоже автоматически секретно
```

Нет.

Если File создан как:

```text
is_private = 0
```

он публичный.

Правильная логика для защищённых документов:

```text
закрытый Document
+
чувствительное вложение
=
Private File
```

Права родительского документа имеют смысл как защита приватного attachment, а не как волшебная оболочка вокруг `/files/...`.

---

## 24. `File` и база данных

Не нужно думать:

```text
удалил базу
→ файлы обязательно исчезли
```

или наоборот:

```text
скопировал только БД
→ получил полноценный Site со всеми attachments
```

При стандартном локальном storage:

```text
БД
→ содержит File Documents и ссылки

файловая система Site
→ содержит реальные public/private files
```

Поэтому полноценный backup Site должен учитывать и базу, и файлы.

Подробно backup/restore будет разбираться позже.

---

## 25. Upload через REST API

У Frappe есть штатный endpoint:

```text
POST /api/method/upload_file
```

Он принимает файл и создаёт соответствующий `File` Document.

При upload можно передать сведения о целевом документе:

```text
doctype
 docname
 fieldname
 is_private
```

Упрощённо:

```text
POST upload_file
      ↓
проверка прав
      ↓
создание File
      ↓
связь с Document
```

Сам REST API подробно будет разобран в отдельной главе. Здесь достаточно понимать, что UI использует ту же серверную файловую модель, а не какое-то отдельное «браузерное» хранилище.

---

## 26. Загрузка гостями — отдельное разрешение

Текущий v16 позволяет отдельно разрешить guest upload через System Settings.

Но это не означает:

```text
Guest всегда может загрузить что угодно куда угодно
```

Framework проверяет соответствующую настройку, а также может ограничивать список DocType, для которых гостевая загрузка разрешена.

Кроме того, для Guest и пользователей без Desk Access upload ограничивается разрешёнными MIME-типами.

Для начала достаточно правила:

> guest file upload нужно считать отдельной явно включаемой возможностью, а не стандартным доступом любого посетителя.

---

## 27. File type и расширение тоже проверяются

При создании File controller выполняет несколько проверок:

```text
размер
расширение
file_url
путь
доступ к приватному файлу
attachment limit
```

То есть сервер не полагается только на то, что пользовательский интерфейс показал красивую кнопку Upload.

Это хороший пример общей архитектуры Frappe:

```text
UI
→ удобство

server controller
→ реальные проверки
```

---

## 28. Image optimization

Стандартный uploader умеет оптимизировать изображения.

Официальная документация описывает уменьшение изображения до ограниченного размера и снижение качества для уменьшения файла.

В текущем backend также есть `optimize_file()` для локальных изображений.

Дополнительно Site может быть настроен на удаление EXIF metadata у загружаемых JPEG.

Это полезная штатная возможность, но она не превращает `File` в полноценную DAM-систему обработки медиа.

---

## 29. File permissions устроены немного особым образом

Если открыть metadata `File`, можно увидеть обычные Role permissions.

Но реальный доступ дополнительно определяется controller-функцией:

```text
has_permission()
```

Она учитывает:

```text
Public / Private
owner
Sharing
attached_to_doctype
attached_to_name
права на связанный Document
```

Поэтому анализировать безопасность File только по строкам Role Permission Manager недостаточно.

Это хороший пример из главы 22: некоторые системные DocType Framework имеют собственную permission logic поверх базовой таблицы ролей.

---

## 30. Что не надо делать

### Ошибка 1. Считать Attach бинарным полем

Неверно:

```text
Attach хранит PDF внутри Request
```

Правильно:

```text
Attach хранит URL
File описывает файл
storage хранит содержимое
```

### Ошибка 2. Делать чувствительный attachment Public

Если содержимое не должно быть доступно публично:

```text
is_private = 1
```

### Ошибка 3. Хранить путь в обычном Data и забыть про File

Если это нормальный attachment Frappe, штатный `File` уже даёт:

- связь с Document;
- permission logic;
- File Manager;
- Timeline events;
- размер;
- тип;
- hash;
- public/private;
- удаление и обслуживание.

### Ошибка 4. Использовать attachment вместо бизнес-сущности

Например, если системе нужны структурированные данные документа:

```text
номер договора
дата
контрагент
сумма
статус
```

одного PDF attachment недостаточно.

PDF — файл.

Бизнес-данные лучше моделировать отдельными полями/DocType.

### Ошибка 5. Считать File неизменяемым архивом

`File` — рабочая файловая модель Framework.

Он поддерживает удаление, смену public/private, повторное использование и другие операции.

Если нужен юридически значимый неизменяемый архив с retention policy, отдельным журналом и специальными гарантиями хранения — это уже другая задача.

---

## 31. Практический пример целиком

Создадим `Request` с полем:

```text
Field Label: Contract
Fieldname: contract
Field Type: Attach
```

Создай:

```text
Request REQ-0001
Subject: New supplier contract
```

Сохрани документ.

Затем приложи:

```text
contract.pdf
```

После загрузки проверь значение поля `Contract`.

Оно должно быть похоже на:

```text
/private/files/contract.pdf
```

или публичный `/files/...`, в зависимости от выбранного режима.

Теперь открой соответствующий File и найди:

```text
File Name
File URL
Is Private
Attached To DocType
Attached To Name
Attached To Field
File Size
File Type
```

Проверь связь:

```text
Attached To DocType = Request
Attached To Name    = REQ-0001
Attached To Field   = contract
```

После этого отдельно приложи второй файл через общий attachments-интерфейс формы, а не через поле Contract.

Сравни два File Documents.

Главное, что нужно увидеть руками:

```text
оба являются File

но один связан с конкретным Attach field,
а второй может быть просто attachment всего Document
```

---

## 32. Мини-практика

### Упражнение 1. Public и Private

Загрузи два тестовых файла:

```text
public.txt
private.txt
```

Один сделай Public, второй Private.

Сравни:

```text
is_private
file_url
```

Ожидаемая идея:

```text
Public  → /files/...
Private → /private/files/...
```

### Упражнение 2. Max Attachments

Для тестового DocType задай:

```text
Max Attachments = 2
```

Попробуй прикрепить три файла.

Убедись, что третий upload отклоняется сервером.

### Упражнение 3. Attachment Gallery

Добавь поле:

```text
Field Type: Attachment Gallery
```

Сохрани Document и прикрепи несколько файлов.

Посмотри, как те же `File` Documents показываются уже через другой UI.

### Упражнение 4. Timeline

Прикрепи файл, затем удали его.

Проверь Timeline.

Найди события:

```text
Attachment
Attachment Removed
```

и вспомни:

```text
событие в Timeline
≠ существующий сейчас File
```

---

## 33. Что запомнить

1. **Каждый штатный attachment представлен отдельным `File` Document.**
2. **`File` хранит метаданные и ссылку, а не является самим бинарным содержимым.**
3. При стандартном локальном storage public-файлы лежат в `public/files`, private — в `private/files`.
4. `file_url` обычно начинается с `/files/` или `/private/files/`.
5. Public File предназначен для публичного чтения; права родительского документа не делают его автоматически закрытым.
6. Private File, прикреплённый к Document, использует права связанного документа как часть permission logic.
7. Обычный upload в существующий Document требует `Write` на этот Document.
8. `Attach` хранит URL, а `attached_to_field` связывает File с конкретным полем.
9. Общий attachment документа может существовать без конкретного `attached_to_field`.
10. `Attachment Gallery` — другой интерфейс над теми же File Documents.
11. `content_hash` позволяет Framework обнаруживать одинаковое содержимое и переиспользовать физический файл.
12. `Max Attachments` ограничивает количество вложений на документ.
13. В актуальном v16 fallback лимита размера в исходниках — **25 MiB**, несмотря на старое упоминание 10 MB на странице документации.
14. `Protect Attached Files` может защищать attachments Submitted Document от удаления.
15. `File` может ссылаться и на удалённый URL, поэтому не каждый File обязан иметь локальный бинарник.
16. Стандартное локальное storage можно заменить через hooks приложения.
17. Backup файлов и backup базы — связанные, но не одинаковые вещи.

---

## Официальные источники

- [Frappe Framework — Attachments](https://docs.frappe.io/framework/user/en/desk/attachments)
- [Frappe Framework — Field Types: Attach, Attach Image, Attachment Gallery](https://docs.frappe.io/framework/user/en/basics/doctypes/fieldtypes)
- [Frappe Framework — Static Assets: public/private user uploads](https://docs.frappe.io/framework/user/en/basics/static-assets)
- [Frappe Framework — REST API: File Uploads](https://docs.frappe.io/framework/user/en/api/rest)
- [`File` metadata, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/file/file.json)
- [`File` controller, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/file/file.py)
- [`upload_file`, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/handler.py)
- [File API, version-16](https://github.com/frappe/frappe/blob/version-16/frappe/core/api/file.py)

---

Следующая глава: **32. Email / Communication**.
