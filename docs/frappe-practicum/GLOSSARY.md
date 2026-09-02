# Краткий словарь

Словарь объясняет термины в том смысле, в котором они используются в практикуме.

| Термин | Значение |
|---|---|
| Bench | каталог и набор команд для управления Frappe, app, site и процессами разработки |
| Site | отдельный экземпляр Frappe со своей базой данных, настройками, пользователями и установленными app |
| App | устанавливаемый пакет исходников, metadata и программной логики; один app можно установить на несколько site |
| Module | раздел внутри app, которому принадлежат DocType, Report, Workspace и другие standard-объекты |
| Desk | внутренний интерфейс Frappe для System User |
| Apps Page | экран навигации между установленными app в Frappe v16 |
| Workspace | рабочая страница с быстрыми ссылками, Number Card, Dashboard Chart и другими блоками |
| DocType | описание вида документа: поля, naming, permissions, поведение и представления |
| Document | один экземпляр конкретного DocType с lifecycle Frappe |
| Standard DocType | DocType, принадлежащий app и сохраняемый в его исходниках |
| Custom DocType | DocType, существующий как настройка конкретного site и не являющийся исходником app |
| Metadata | описание структуры и декларативного поведения: DocType, поля, permissions, Workspace, Report и другие настройки |
| `name` | системный уникальный идентификатор Document |
| Title Field | поле, которое показывается человеку как понятное название рядом с `name` |
| Link | поле, которое хранит `name` существующего Document другого DocType |
| Child Table | строки, принадлежащие одному родительскому Document и не имеющие самостоятельного процесса |
| Tree DocType | DocType с иерархией родительских и дочерних узлов |
| Mandatory | серверное требование заполнить поле; для Check значение `0` не считается отсутствующим |
| Unique | ограничение, запрещающее одинаковое значение поля в двух документах |
| Set Only Once | запрет менять поле после первого сохранения Document |
| `docstatus` | системное состояние документа: `0` Draft, `1` Submitted, `2` Cancelled |
| Submittable | DocType, документы которого поддерживают Submit, Cancel и Amend |
| Role | набор полномочий, назначаемый пользователю |
| DocPerm | строка базовых прав Role на DocType |
| Permission Level | доступ к группе полей внутри Document, а не к отдельным строкам |
| If Owner | ограничение прав документами, где системный `owner` равен текущему пользователю |
| User Permission | сужение видимости документов по значениям Link, например по Department |
| Share | точечная выдача доступа к одному Document |
| System User | пользователь, который входит в Desk |
| Website User | пользователь внешнего web-контура без обычного Desk |
| Guest | неавторизованный посетитель сайта |
| Workflow | разрешённые переходы между состояниями с ролями и условиями |
| Workflow Action | действие пользователя, выполняющее разрешённый переход Workflow |
| Assignment | указание конкретного ответственного через Assign To и ToDo; не является правом доступа |
| Notification | штатная реакция на событие или условие: системное либо email-уведомление |
| Report Builder | отчёт по доступному DocType без собственного Python или SQL |
| Fixture | выбранная конфигурационная запись базы, экспортированная в app и загружаемая при install/migrate |
| Export Customizations | экспорт Custom Field, Property Setter и Custom DocPerm для расширяемого DocType |
| Developer Mode | режим, в котором Standard metadata разрешено сохранять в исходники app |
| `migrate` | применение schema, patches, metadata, fixtures и других изменений app к site |
| Clean site | новый site без рабочей базы, используемый для проверки fresh install app |
| Test site | отдельный site для automated tests; не рабочий и не clean-install acceptance site |
| Web Form | внешний маршрут, создающий или изменяющий документы выбранного DocType по своему списку полей |
| REST API | стандартный HTTP-интерфейс Frappe для операций с DocType и вызова разрешённых методов |
| API key/secret | учётные данные API user; относятся к секретам site и не входят в app |
| Controller | Python-класс конкретного DocType, наследующий `Document` и владеющий его программным поведением |
| Document lifecycle | последовательность серверных фаз Document: insert/save/validate/submit/cancel и связанные controller events |
| `before_insert` | controller event только для создания нового Document до DB insert; подходит creation-only invariant |
| `validate` | controller event перед сохранением, применимый шире одного insert; не должен использоваться для creation-only правила без причины |
| Whitelisted method | Python method/function, который Frappe разрешает вызывать через HTTP/RPC при выполнении остальных проверок |
| Semantic command | предметное действие вроде `create_case`, которое выражает бизнес-операцию и не дублирует generic CRUD |
| Request transaction | транзакция БД, которой Frappe управляет вокруг HTTP request; успешная write-операция commit, uncaught exception rollback |
| Rollback | отмена незакоммиченных изменений транзакции |
| `after_commit` | callback, который выполняется только после успешного commit текущей транзакции |
| Background Job | работа, выполняемая Frappe worker вне текущего HTTP request; нужна для реальной async/heavy ответственности |
| `enqueue_after_commit` | режим `frappe.enqueue`, при котором job ставится в очередь только после успешного commit текущей транзакции |
| Webhook | штатная настраиваемая отправка HTTP по событию DocType; в v16 обычный event-path отправляется после commit через background queue |
| Patch | одноразовая миграция данных/состояния site, регистрируемая в `patches.txt` и выполняемая через migrate |
| `post_model_sync` | секция patches, выполняемая после синхронизации DocType schema; нужна patch, зависящей от нового поля |
| `IntegrationTestCase` | Frappe base class для integration tests, которым нужна БД и реальный framework environment |
| Проверка исходников | проверка того, какие файлы app изменились после настройки/кода |
| Проверка на чистом site | установка app на новый site и повторение сценария без копирования базы |
| Upgrade check | обновление уже существующего site с историческими данными через новую версию app и `migrate` |

Если термин отсутствует в таблице, сначала искать его в текущей лабораторной, затем в
[REFERENCES.md](REFERENCES.md).
