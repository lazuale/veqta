# 43. Authentication для интеграций

В главах 41 и 42 мы уже научились:

```text
REST
→ работать с Documents

RPC
→ вызывать серверные команды
```

Но любой внешний request упирается в следующий вопрос:

```text
кто именно делает этот запрос?
```

Это и есть задача authentication.

Главный вопрос этой главы:

```text
как внешней программе
безопасно представиться Frappe
```

Проверено: **2026-08-31**.

---

# Часть I. Сначала разделим три разных понятия

## 1. Authentication

Authentication отвечает на вопрос:

```text
КТО делает запрос?
```

Например:

```text
integration@example.com
```

---

## 2. Authorization

Authorization отвечает на другой вопрос:

```text
ЧТО этому пользователю разрешено?
```

Например:

```text
Request
Read   ✓
Write  ✓
Create ✓
Delete ✗
```

---

## 3. Whitelist

Для RPC есть ещё третий уровень:

```text
можно ли эту Python-функцию
вообще вызвать по HTTP?
```

Это решает:

```python
@frappe.whitelist()
```

---

## 4. Эти три проверки нельзя смешивать

Правильная схема:

```text
HTTP request
    ↓
Authentication
    ↓
кто пользователь?
    ↓
Authorization
    ↓
что ему разрешено?
    ↓
REST / RPC operation
```

Для RPC добавляется:

```text
Whitelist + HTTP method gate
```

---

# Часть II. Какие способы authentication есть у Frappe

## 5. Для интеграций нам важны три основных варианта

```text
1. Session / password
2. API Key + API Secret
3. OAuth 2 Bearer token
```

Кроме них Framework позволяет Apps подключать собственную authentication logic через:

```text
auth_hooks
```

но это уже extension point.

---

## 6. Очень грубая карта выбора

```text
человек вошёл через браузер
→ Session

сервер ↔ сервер
→ API Key + API Secret

стороннее приложение получает доступ
от имени пользователя
→ OAuth 2
```

Это не абсолютное правило, но хороший старт.

---

# Часть III. Guest — это тоже identity

## 7. Запрос без успешной authentication

Во Frappe выполняется как:

```text
Guest
```

Это не означает:

```text
полный доступ без логина
```

---

## 8. Guest имеет только явно разрешённую поверхность

Например:

```python
@frappe.whitelist(allow_guest=True)
def public_status():
    ...
```

или публичные Website/Web Form сценарии.

---

## 9. Обычный authenticated RPC не доступен Guest

```python
@frappe.whitelist()
def internal_action():
    ...
```

требует authenticated пользователя.

---

## 10. Guest — не способ интеграции по умолчанию

Если внешняя система должна:

```text
читать внутренние данные
создавать документы
менять статусы
выполнять команды
```

обычно ей нужна настоящая identity.

---

# Часть IV. Session authentication

## 11. Это обычная модель браузерного входа

Пользователь вводит:

```text
username / email
password
```

Frappe проверяет credentials и создаёт session.

---

## 12. API login endpoint

Для программного входа существует:

```http
POST /api/method/login
```

с параметрами:

```text
usr
pwd
```

---

## 13. Пример login

```bash
curl -X POST \
  "https://example.com/api/method/login" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -c cookies.txt \
  -d '{
    "usr": "user@example.com",
    "pwd": "PASSWORD"
  }'
```

---

## 14. Что происходит при успешном login

Frappe создаёт session и отдаёт cookie:

```text
sid
```

Следующие requests могут использовать эту cookie.

---

## 15. Следующий request

```bash
curl \
  "https://example.com/api/method/frappe.auth.get_logged_user" \
  -b cookies.txt
```

Frappe восстанавливает session и понимает:

```text
кто пользователь
```

---

## 16. Session хранится server-side

Cookie `sid` является идентификатором session.

Упрощённо:

```text
Browser
  sid=abc123
     ↓
Frappe
     ↓
Sessions / cache
     ↓
User
```

---

## 17. Session имеет срок жизни

Не надо закладываться в integration code на магическое:

```text
session живёт ровно N дней
```

Session expiry зависит от настроек и server-side session lifecycle.

---

## 18. Session может закончиться раньше

Например:

```text
logout
expiry
очистка sessions
ограничение simultaneous sessions
административное действие
```

Поэтому внешний client должен уметь обрабатывать потерю session.

---

# Часть V. Password login сложнее, чем просто пароль

## 19. Login проходит Frappe authentication flow

В него могут входить:

```text
password check
user enabled check
IP restrictions
login hours
2FA
session rules
login hooks
```

в зависимости от конфигурации.

---

## 20. Может быть отключён обычный password login

System Settings могут запрещать вход:

```text
username + password
```

В таком случае `/api/method/login` не становится обходом этой политики.

---

## 21. 2FA делает machine-to-machine password login неудобным

Если account рассчитан на человека и требует second factor,

автоматическая интеграция не должна пытаться имитировать browser login.

Для server-to-server сценария обычно правильнее отдельный integration user + API credentials.

---

# Часть VI. Logout

## 22. В Frappe v16 logout — state-changing action

Актуальный код v16 определяет logout как:

```text
POST
```

---

## 23. Пример

```bash
curl -X POST \
  "https://example.com/api/method/logout" \
  -b cookies.txt
```

---

## 24. Почему это отдельно отмечено

В старых страницах документации ещё можно встретить пример:

```text
GET /api/method/logout
```

Но в текущем `version-16` handler logout whitelisted только для:

```text
POST
```

Для курса используем поведение исходного кода v16.

---

# Часть VII. CSRF и session authentication

## 25. Cookie отправляется browser-ом автоматически

Именно поэтому browser session подвержена классу атак:

```text
CSRF
```

---

## 26. Что такое CSRF простыми словами

Представим:

```text
пользователь уже вошёл на example.com
```

Затем открывает вредоносный сайт.

Тот пытается заставить browser отправить:

```text
POST example.com/delete-something
```

Browser может автоматически приложить cookies.

---

## 27. Поэтому unsafe requests проверяются отдельно

В v16 Frappe относит к unsafe methods:

```text
POST
PUT
DELETE
PATCH
```

---

## 28. Frappe проверяет CSRF token для session flow

Обычный browser client Frappe отправляет header:

```text
X-Frappe-CSRF-Token
```

для защищённых state-changing запросов.

---

## 29. Это особенно важно для собственного browser frontend

Если ваш frontend использует:

```text
Frappe login
+
sid cookie
```

нельзя просто забыть про CSRF.

---

## 30. Machine-to-machine token auth проще

При API Key / OAuth integration identity передаётся явно в:

```text
Authorization header
```

Поэтому для server-to-server client не требуется строить browser cookie session только ради API.

---

## 31. Не отключай CSRF глобально ради одного клиента

В site config существует:

```text
ignore_csrf
```

Но включать глобальное игнорирование CSRF только потому, что custom frontend не умеет правильно отправлять token — плохая архитектура.

Нужно исправить authentication flow клиента.

---

# Часть VIII. API Key + API Secret

## 32. Это основной простой вариант для server-to-server integration

Frappe User может иметь:

```text
API Key
API Secret
```

---

## 33. Они принадлежат конкретному User

Это принципиально.

Не существует абстрактного token с собственными независимыми permissions.

Схема:

```text
API Key + API Secret
        ↓
      User
        ↓
Roles / User Permissions / document permissions
```

---

## 34. API Key идентифицирует credential set

Упрощённо:

```text
API Key
→ кто это
```

---

## 35. API Secret доказывает владение credential

```text
API Secret
→ секретная часть
```

Его нельзя публиковать.

---

# Часть IX. Где создать API credentials

## 36. Через User

Открываем:

```text
User
→ Settings
→ API Access
→ Generate Keys
```

---

## 37. В User v16 действительно есть штатные поля

```text
api_key
api_secret
Generate Keys
```

`api_secret` — поле типа:

```text
Password
```

---

## 38. Generate Keys может выполнять System Manager

В текущем v16 функция:

```python
frappe.only_for("System Manager")
```

То есть обычный пользователь не должен самостоятельно создавать API credentials через этот endpoint.

---

## 39. Generate Keys вызывается через POST

В v16:

```python
@frappe.whitelist(methods=["POST"])
def generate_keys(...):
```

---

# Часть X. Очень важная деталь ротации

## 40. API Key и API Secret ведут себя не одинаково

Текущий v16 делает:

```text
если API Key отсутствует
→ создаёт API Key

всегда
→ создаёт новый API Secret
```

---

## 41. Уже существующий API Key сохраняется

В metadata User прямо указано:

```text
API Key cannot be regenerated
```

---

## 42. Secret можно заменить

Повторный Generate Keys перезаписывает:

```text
api_secret
```

---

## 43. Старый secret после этого перестаёт подходить

Потому что authentication сравнивает request secret с текущим secret User.

Следствие:

```text
rotation secret
→ update integration immediately
```

---

## 44. Один User = один актуальный API Secret

Это важная архитектурная причина не делать:

```text
один integration-user
для 12 разных систем
```

Если все используют один secret, его ротация ломает всех сразу.

---

# Часть XI. Как отправить token authentication

## 45. Стандартный Frappe header

```http
Authorization: token API_KEY:API_SECRET
```

Обрати внимание на слово:

```text
token
```

---

## 46. Пример curl

```bash
curl \
  "https://example.com/api/method/frappe.auth.get_logged_user" \
  -H "Authorization: token API_KEY:API_SECRET"
```

---

## 47. Пример REST

```bash
curl \
  "https://example.com/api/v2/document/Request?limit=10" \
  -H "Authorization: token API_KEY:API_SECRET"
```

---

## 48. Пример POST RPC

```bash
curl -X POST \
  "https://example.com/api/v2/method/my_app.api.close_request" \
  -H "Authorization: token API_KEY:API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"name":"REQ-0001"}'
```

---

# Часть XII. Python example

## 49. Requests session

```python
import requests

BASE_URL = "https://example.com"
API_KEY = "..."
API_SECRET = "..."

session = requests.Session()
session.headers.update({
    "Authorization": f"token {API_KEY}:{API_SECRET}",
    "Accept": "application/json",
})

response = session.get(
    f"{BASE_URL}/api/method/frappe.auth.get_logged_user",
    timeout=30,
)

response.raise_for_status()
print(response.json())
```

---

## 50. Не хардкодь secret в исходнике

Плохо:

```python
API_SECRET = "eK7..."
```

в Git repository.

---

## 51. Минимальный нормальный вариант

```python
import os

API_KEY = os.environ["FRAPPE_API_KEY"]
API_SECRET = os.environ["FRAPPE_API_SECRET"]
```

---

## 52. Ещё лучше в production

Использовать подходящий secret store:

```text
Docker secret
Kubernetes Secret / external secret manager
Vault
cloud secret manager
CI/CD protected secret
OS credential store
```

в зависимости от инфраструктуры.

---

# Часть XIII. Basic authentication в Frappe

## 53. Frappe также поддерживает Authorization Basic

Но здесь есть очень важная ловушка.

---

## 54. Это не обязательно Basic username:password

Для Frappe REST token authentication документация описывает:

```text
API_KEY:API_SECRET
```

которые base64-кодируются.

---

## 55. Схема

```text
API_KEY:API_SECRET
      ↓ base64
Authorization: Basic <base64>
```

---

## 56. Пример концептуально

```http
Authorization: Basic YXBpX2tleTphcGlfc2VjcmV0
```

---

## 57. Base64 не является encryption

Это только encoding.

Любой, кто получил значение, может его декодировать.

Поэтому:

```text
HTTPS обязателен
```

---

## 58. Для читаемости Frappe integration обычно проще использовать token scheme

```http
Authorization: token API_KEY:API_SECRET
```

Он однозначнее показывает, что это Frappe API credentials.

---

# Часть XIV. Что происходит на сервере при API Key auth

## 59. Frappe читает Authorization header

Поддерживаемые стандартные варианты в этом flow:

```text
Bearer
Basic
token
```

---

## 60. Для token/basic извлекаются

```text
api_key
api_secret
```

---

## 61. Затем Framework ищет credential owner

Для обычной схемы это:

```text
User
```

с подходящим:

```text
api_key
```

и:

```text
enabled = 1
```

---

## 62. Disabled User не проходит обычную API Key authentication

Это полезное свойство для аварийного отключения integration identity.

---

## 63. Secret сравнивается с сохранённым API Secret

При успехе Frappe устанавливает request user:

```text
frappe.session.user
```

на найденного User.

---

## 64. После этого работают его permissions

То есть request не становится:

```text
Administrator
```

только потому, что использует API key.

---

# Часть XV. Самая важная идея API credentials

## 65. Credentials не содержат permissions

Они только подтверждают identity.

---

## 66. Permissions живут на User

Например:

```text
Integration A User
    ↓
Role: Request Integration
    ↓
Request
Read   ✓
Create ✓
Write  ✓
Delete ✗
```

---

## 67. Поэтому правильный integration user должен быть минимальным

Не нужно выдавать:

```text
System Manager
```

только чтобы «API точно работало».

---

## 68. Если API отвечает PermissionError

Первый вопрос:

```text
каких permission реально не хватает?
```

а не:

```text
как выдать Administrator?
```

---

# Часть XVI. Отдельный User на интеграцию

## 69. Хорошая схема

```text
1C Integration
→ integration-1c@example.local

BI Export
→ integration-bi@example.local

Warehouse Sync
→ integration-warehouse@example.local
```

---

## 70. Почему это лучше

Получаем отдельно:

```text
credentials
permissions
logs
revocation
rotation
ownership
```

---

## 71. Один общий `api@example.com` хуже

Потому что потом невозможно быстро понять:

```text
какая система сделала request
какой secret утёк
кого отключать
кому нужны дополнительные rights
```

---

## 72. Человеческий User тоже не надо использовать для service integration

Плохая схема:

```text
API работает от аккаунта директора
```

Проблемы:

```text
смена сотрудника
смена ролей
2FA
пароль
аудит
лишние permissions
```

---

# Часть XVII. HTTPS

## 73. API credentials должны передаваться только по HTTPS

Authorization header содержит секрет.

Без TLS network observer может получить credentials.

---

## 74. Это относится ко всем схемам

```text
password
API Secret
OAuth access token
refresh token
sid cookie
```

---

## 75. HTTP допустим только в контролируемом local development

Например:

```text
localhost
isolated dev container
```

Но production integration должна использовать:

```text
https://
```

---

# Часть XVIII. Не клади credentials в URL

## 76. Плохо

```text
https://example.com/api/resource/Request?token=SECRET
```

---

## 77. Почему

URL может попасть в:

```text
reverse-proxy logs
browser history
monitoring
analytics
error reports
Referer
shell history
```

---

## 78. Credentials должны идти в Authorization header

```http
Authorization: token ...
```

или соответствующем OAuth flow.

---

# Часть XIX. OAuth 2

## 79. API Key хорошо подходит не всегда

Представим стороннее приложение:

```text
External Analytics App
```

которое должно читать данные конкретного пользователя.

Плохо просить пользователя:

```text
пришли свой API Secret
```

---

## 80. Для delegated access существует OAuth 2

Смысл:

```text
User
→ явно разрешает Client App доступ
→ Frappe выдаёт access token
→ Client использует Bearer token
```

---

## 81. Frappe умеет быть OAuth Provider

То есть сам Frappe site может выступать как:

```text
Authorization Server
+
Resource Server
```

для стороннего client application.

---

# Часть XX. OAuth Client

## 82. На Frappe создаётся OAuth Client

Это registration внешнего приложения, которому разрешено проходить OAuth flow.

---

## 83. В нём задаются

В зависимости от сценария:

```text
App Name
Redirect URIs
Scopes
Grant Type
Response Type
client credentials
```

---

## 84. Не путай OAuth Client и Connected App

Это противоположные направления.

```text
OAuth Client
→ внешнее приложение получает доступ К Frappe
```

```text
Connected App
→ Frappe получает доступ К внешнему OAuth service
```

Это разные задачи.

---

# Часть XXI. Authorization Code flow

## 85. Упрощённая схема

```text
External App
    ↓
redirect user to Frappe
    ↓
User logs in / approves access
    ↓
authorization code
    ↓
External App exchanges code
    ↓
access token
```

---

## 86. Frappe authorize endpoint

Документация v16 использует:

```text
/api/method/frappe.integrations.oauth2.authorize
```

---

## 87. Token endpoint

```text
/api/method/frappe.integrations.oauth2.get_token
```

---

## 88. Полученный access token используется так

```http
Authorization: Bearer ACCESS_TOKEN
```

---

# Часть XXII. OAuth example request

## 89. После получения access token

```bash
curl \
  "https://example.com/api/v2/document/Request?limit=10" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

---

## 90. Bearer означает

Кто владеет token, тот может его предъявить.

Поэтому access token тоже является секретом.

---

## 91. Bearer token нельзя логировать или хранить в Git

Относись к нему так же серьёзно, как к API Secret.

---

# Часть XXIII. OAuth scopes

## 92. OAuth вводит дополнительное понятие

```text
scope
```

Оно описывает объём доступа, который client запрашивает у OAuth provider.

---

## 93. Но scopes не отменяют Frappe permissions

Упрощённо:

```text
OAuth token
→ определяет authenticated user / granted scope

Frappe permissions
→ определяют доступ этого user к Documents
```

---

## 94. Не надо воспринимать scope как замену Role Permission Manager

Оба слоя решают разные задачи.

---

# Часть XXIV. Refresh token

## 95. OAuth access token обычно ограничен по времени

Поэтому OAuth flow может выдавать:

```text
refresh_token
```

---

## 96. Refresh token используется для получения нового access token

Без повторного ввода пароля пользователем.

---

## 97. Refresh token зачастую чувствительнее access token

Потому что позволяет получать новые access tokens.

Его нужно хранить только server-side или в подходящем secure client storage.

---

# Часть XXV. PKCE

## 98. Frappe OAuth documentation v16 описывает PKCE

Для Authorization Code flow используются:

```text
code_challenge
code_challenge_method
code_verifier
```

---

## 99. Зачем PKCE

Он защищает authorization code от использования другим client-ом, который перехватил code.

---

## 100. Для browser/native public clients PKCE особенно важен

Потому что такой client не может надёжно спрятать постоянный client secret внутри распространяемого приложения.

---

# Часть XXVI. OAuth `state`

## 101. В authorize request есть `state`

Это не декоративный параметр.

---

## 102. Client генерирует непредсказуемое значение

```text
state = random value
```

запоминает его и отправляет в OAuth authorization request.

---

## 103. После redirect проверяет то же значение

Если state не совпадает:

```text
flow нужно отклонить
```

---

## 104. Основная цель

Защита authorization flow от CSRF/session mix-up сценариев.

---

# Часть XXVII. OAuth не нужен каждой интеграции

## 105. Server A постоянно синхронизирует данные с Frappe

Например:

```text
nightly ETL
```

Если это одна доверенная server-side integration,

OAuth authorization dance часто только усложнит систему.

---

## 106. Здесь естественнее

```text
отдельный service user
+
API Key / API Secret
```

---

## 107. OAuth особенно оправдан

Когда есть:

```text
third-party application
many users
delegated access
consent
access token lifecycle
scopes
```

---

# Часть XXVIII. API Key против OAuth

## 108. Короткое сравнение

| Вопрос | API Key + Secret | OAuth 2 |
|---|---|---|
| Простота | высокая | ниже |
| Server-to-server | отлично | возможно |
| Доступ от имени многих пользователей | неудобно | естественно |
| User consent | нет отдельного flow | есть |
| Short-lived access token | нет | да |
| Refresh token | нет | возможно |
| Scopes | нет отдельного OAuth scope layer | есть |
| Подходит стороннему приложению | ограниченно | да |

---

# Часть XXIX. CORS

## 109. CORS относится к browser security

Представим:

```text
frontend.example.com
```

пытается вызвать:

```text
frappe.example.com
```

из JavaScript browser-а.

---

## 110. Browser проверяет CORS policy

Frappe может разрешать origins через site configuration:

```text
allow_cors
```

---

## 111. CORS не является authentication

Даже если origin разрешён:

```text
request всё равно должен иметь нужную identity
```

если endpoint не public.

---

## 112. CORS не является permissions

```text
allow_cors
```

не означает:

```text
этому frontend можно читать все DocTypes
```

---

## 113. Не открывай `*` без причины

Для собственного browser application лучше явно знать нужные origins.

Это уменьшает лишнюю публичную поверхность.

---

# Часть XXX. CORS и CSRF — не одно и то же

## 114. CORS

Отвечает примерно на вопрос:

```text
разрешено ли JavaScript из другого origin
читать/делать этот cross-origin request
```

---

## 115. CSRF

Защищает session-authenticated пользователя от state-changing request, который browser отправил с его credentials без его намерения.

---

## 116. Поэтому фраза

```text
мы включили CORS, значит CSRF больше не нужен
```

неверна.

---

# Часть XXXI. Authentication hooks

## 117. Framework позволяет подключить custom authentication

В `hooks.py` App можно определить:

```python
auth_hooks = [
    "my_app.auth.validate_custom_auth"
]
```

---

## 118. Метод вызывается во время request authentication

Он может, например:

```text
прочитать custom header
проверить JWT
проверить подпись
сопоставить identity с Frappe User
```

---

## 119. После успешной проверки App может установить User

```python
frappe.set_user(user)
```

---

## 120. Это extension point, а не первый выбор

Не нужно писать custom JWT authentication только потому, что стандартный header выглядит непривычно.

Сначала оцени:

```text
API Key
OAuth
```

---

# Часть XXXII. Когда custom auth действительно может понадобиться

## 121. Например

```text
корпоративный API Gateway
центральный JWT issuer
внешний identity proxy
подписанные service requests
```

где вся инфраструктура уже стандартизирована на другой authentication mechanism.

---

## 122. Но custom auth должен проверять криптографию полностью

Недостаточно:

```python
payload = decode_jwt_without_verification(token)
frappe.set_user(payload["email"])
```

Нужно проверять как минимум всё, что требует выбранный protocol:

```text
signature
issuer
audience
expiry
not-before
algorithm constraints
mapping user
revocation policy
```

---

# Часть XXXIII. Identity mapping

## 123. Внешняя identity должна однозначно переходить во Frappe User

Нельзя делать неуправляемое правило:

```text
кто прислал header X-User
→ тот и пользователь
```

без доверенной криптографической/сетевой границы.

---

## 124. `frappe.set_user()` не является authentication сам по себе

Это server-side действие:

```text
установить текущего пользователя
```

До него App обязан доказать identity.

---

# Часть XXXIV. Secret management

## 125. Что считается secret

Как минимум:

```text
password
API Secret
OAuth client secret
access token
refresh token
sid
private signing key
```

---

## 126. Что обычно не является секретом само по себе

```text
API Key
OAuth client ID
username
```

Но их всё равно не обязательно публиковать без причины.

---

## 127. Secret не должен жить в Git

Плохо:

```text
config.py
.env committed to repository
README example with real secret
Docker Compose with real production credential
```

---

## 128. `.env` не становится безопасным только из-за названия

Если `.env` попал в Git:

```text
secret уже считается раскрытым
```

Удалить строку новым commit недостаточно — credential нужно ротировать.

---

# Часть XXXV. Environment variables

## 129. Нормальный простой pattern

```bash
export FRAPPE_API_KEY="..."
export FRAPPE_API_SECRET="..."
```

---

## 130. Client

```python
import os

api_key = os.environ["FRAPPE_API_KEY"]
api_secret = os.environ["FRAPPE_API_SECRET"]
```

---

## 131. Но environment тоже не волшебный vault

Нужно учитывать:

```text
process permissions
container inspect access
CI logs
shell history
crash dumps
```

---

# Часть XXXVI. Secret rotation

## 132. Rotation должна быть запланированной операцией

Для API Secret:

```text
1. подготовить новый secret
2. безопасно передать его integration
3. обновить integration config
4. проверить connection
5. убедиться, что старый credential больше не используется
```

---

## 133. У Frappe User фактически один текущий API Secret

Поэтому штатный Generate Keys не даёт удобного overlap из двух active secrets на одном User.

---

## 134. Если нужен zero-downtime overlap

Один практичный вариант:

```text
создать второй integration user
→ выдать те же минимальные permissions
→ переключить client
→ отключить старого user
```

Это также делает ротацию наблюдаемой и обратимой.

---

# Часть XXXVII. Revocation

## 135. Если API Secret утёк

Нельзя просто:

```text
надеяться, что никто не воспользуется
```

---

## 136. Нужно заменить secret

Повторный Generate Keys создаёт новый `api_secret`.

Старый перестаёт совпадать с сохранённым значением.

---

## 137. Если нужен мгновенный жёсткий stop

Для обычного API Key user можно также отключить User:

```text
enabled = 0
```

Authentication по API Key ищет только enabled User.

---

## 138. После incident нужно проверить аудит

Как минимум:

```text
какие requests были сделаны
какие Documents изменены
какие permissions были у identity
не появились ли новые credentials
```

---

# Часть XXXVIII. Не раздавай secrets вручную в чатах

## 139. Плохие каналы

```text
общий Telegram chat
Slack channel
email thread
issue tracker
GitHub comment
wiki page
```

---

## 140. Лучше

Использовать организационный secret-sharing process:

```text
password manager
one-time secret share
vault
protected CI variable
```

в зависимости от инфраструктуры.

---

# Часть XXXIX. Logging

## 141. Не логируй Authorization header

Плохой debug:

```python
print(request.headers)
```

в production.

---

## 142. Не логируй полный request config клиента

Например:

```python
logger.info(headers)
```

если `headers` содержит:

```text
Authorization
```

---

## 143. Маскируй credentials

В debug output лучше видеть:

```text
Authorization: token ****
```

а не реальный secret.

---

# Часть XL. Permissions для integration user

## 144. Начинай с задачи

Например integration должна:

```text
читать Request
создавать Request
```

---

## 145. Тогда минимальная роль

```text
Request
Read   ✓
Create ✓
Write  ✗
Delete ✗
```

если Update действительно не нужен.

---

## 146. Не выдавай Write «на всякий случай»

Каждый лишний permission увеличивает последствия утечки credential.

---

## 147. User Permission тоже продолжает работать

Например integration user может быть ограничен:

```text
Company A
```

и не видеть:

```text
Company B
```

если модель DocType и permission chain это поддерживает.

---

# Часть XLI. Integration endpoint и permissions

## 148. REST автоматически проходит permission model

Например:

```http
GET /api/v2/document/Request/REQ-0001/
```

проверяет Read.

---

## 149. RPC требует сознательной authorization logic

Например:

```python
@frappe.whitelist(methods=["POST"])
def approve_request(name):
    doc = frappe.get_doc("Request", name)
    doc.check_permission("write")
    ...
```

---

## 150. API Secret не должен превращаться в bypass

Не делай:

```python
@frappe.whitelist()
def dangerous(name):
    doc = frappe.get_doc("Request", name)
    doc.save(ignore_permissions=True)
```

только потому, что endpoint «всё равно знает secret».

Authentication и authorization — разные вещи.

---

# Часть XLII. Test current identity

## 151. Полезный diagnostic endpoint

```text
/api/method/frappe.auth.get_logged_user
```

---

## 152. Token test

```bash
curl \
  "https://example.com/api/method/frappe.auth.get_logged_user" \
  -H "Authorization: token API_KEY:API_SECRET"
```

---

## 153. Ожидаем

В API v1 response будет примерно:

```json
{
  "message": "integration@example.com"
}
```

---

## 154. Это хороший первый тест

Он разделяет проблемы:

```text
Authentication работает?
```

от:

```text
Permissions на конкретный DocType работают?
```

---

# Часть XLIII. Диагностика 401 и 403

## 155. Упрощённо 401

Обычно означает проблему identity/authentication:

```text
неверный credential
expired/invalid access token
невалидная session
неуспешная auth scheme
```

---

## 156. 403

Обычно означает:

```text
пользователь определён
но действие запрещено
```

---

## 157. Поэтому не лечи 403 сменой API Secret

Сначала проверь:

```text
Role
DocType Permission
User Permission
Permission Level
Document owner/share
RPC authorization checks
```

---

# Часть XLIV. Типичный порядок диагностики API auth

## 158. Шаг 1

Проверить URL:

```text
https://correct-site/...
```

---

## 159. Шаг 2

Проверить:

```text
Authorization header
```

без вывода secret в публичный log.

---

## 160. Шаг 3

Вызвать:

```text
frappe.auth.get_logged_user
```

---

## 161. Шаг 4

Если identity верна — проверить конкретный resource.

```text
GET Document
```

---

## 162. Шаг 5

Если Read работает, а Write нет — проверять authorization, а не authentication.

---

# Часть XLV. Browser frontend

## 163. Если frontend работает на том же Frappe site

Например Website/Desk code,

естественно использовать существующую user session.

---

## 164. Не вставляй API Secret в JavaScript bundle

Никогда:

```javascript
const API_SECRET = "production-secret";
```

---

## 165. Почему

Весь browser code доступен пользователю.

Secret можно увидеть через:

```text
DevTools
source maps
network
bundle
browser extensions
```

---

## 166. API Key + Secret подходит server-side client

Но не как скрытый credential внутри публичного SPA.

---

## 167. Для user-facing SPA обычно лучше

В зависимости от архитектуры:

```text
session auth
или
OAuth Authorization Code + PKCE
```

а не встроенный permanent API Secret.

---

# Часть XLVI. Mobile application

## 168. Та же проблема

Secret, встроенный в APK/IPA:

```text
не является настоящим secret
```

его можно извлечь.

---

## 169. Поэтому permanent service API Secret нельзя раздавать всем mobile clients

Для user-specific access нужен flow, где каждый пользователь получает свою identity/token.

---

# Часть XLVII. Server-to-server

## 170. Типовой хороший вариант

```text
Integration Server
      ↓ HTTPS
Authorization: token KEY:SECRET
      ↓
Frappe
      ↓
Dedicated User
      ↓
Minimal Role
```

---

## 171. Такой client может быть полностью stateless относительно Frappe session

Каждый request несёт credential сам.

Не нужно хранить:

```text
sid cookie
login session
browser state
```

---

# Часть XLVIII. Reverse proxy и network layer

## 172. Authentication Frappe — не единственная защита

Дополнительно можно использовать:

```text
firewall
VPN
private network
reverse proxy ACL
mTLS at gateway
IP allowlist
WAF
```

если этого требует инфраструктура.

---

## 173. Но network allowlist не заменяет Frappe identity

Плохая модель:

```text
запрос пришёл из внутренней сети
→ значит Administrator
```

Лучше иметь оба слоя:

```text
network restriction
+
application authentication
```

---

# Часть XLIX. IP restrictions User

## 174. В User есть Restrict IP

Это часть стандартной user/login security.

---

## 175. Но не надо считать её универсальным API gateway

Для integration network policy лучше отдельно проектировать:

```text
proxy/firewall/VPN
```

и тестировать фактическое поведение выбранного auth flow.

Не строй критичную API protection только на предположении, что UI login setting обязательно одинаково применяется ко всем authentication механизмам.

---

# Часть L. Authentication audit

## 176. Для integration identity полезно знать

```text
кто владелец интеграции
для чего user создан
какие roles выданы
где хранится secret
когда была последняя rotation
что делать при compromise
```

---

## 177. Это не бюрократия ради бюрократии

Без этих данных через год появляется:

```text
api2@example.com
```

и никто не знает:

```text
можно ли его удалить
что он делает
кто использует credential
```

---

# Часть LI. Не используй Administrator

## 178. Самый плохой shortcut

```text
создадим API keys Administrator
и всё заработает
```

---

## 179. Почему это опасно

Compromise такого credential потенциально даёт максимально широкий доступ.

---

## 180. Правильнее

```text
Dedicated User
→ Dedicated Role
→ only required DocTypes/actions
```

---

# Часть LII. Не используй один secret во всех средах

## 181. Development и production должны быть разделены

Не нужно:

```text
один API Secret
→ dev
→ test
→ prod
```

---

## 182. Лучше

```text
dev integration identity
staging integration identity
prod integration identity
```

с независимыми credentials.

---

## 183. Это уменьшает blast radius

Утечка dev secret не должна автоматически открывать production.

---

# Часть LIII. Request timeout и auth retry

## 184. Не повторяй login бесконечно

Если password auth возвращает authentication failure,

не нужно делать:

```text
1000 login attempts подряд
```

Это может активировать throttling/lockout и только ухудшить проблему.

---

## 185. Token auth failure тоже не должен retry-иться как network timeout

Неверный credential:

```text
нужно исправить credential
```

а не:

```text
retry forever
```

---

## 186. Разделяй ошибки

```text
network timeout
→ retry

429
→ backoff / Retry-After

401
→ refresh/repair authentication

403
→ repair permissions
```

---

# Часть LIV. OAuth refresh strategy

## 187. Если access token expired

Client не должен снова просить пароль пользователя автоматически.

При наличии refresh token:

```text
refresh token
→ token endpoint
→ new access token
```

---

## 188. Если refresh не сработал

Например authorization отозван,

нужно вернуть пользователя в нормальный authorization flow.

---

# Часть LV. OAuth Client Secret и public clients

## 189. Server-side web application может хранить client secret

Потому что code и secret живут на сервере.

---

## 190. SPA/mobile application не может надёжно скрыть client secret

Поэтому для таких clients нужен public-client подход с PKCE, а не попытка спрятать secret внутри bundle.

---

# Часть LVI. Social Login — соседняя, но другая задача

## 191. Social Login отвечает на вопрос

```text
как человеку войти во Frappe
через Google/GitHub/Frappe IDP и т.п.
```

---

## 192. Это не то же самое, что integration API auth

Не нужно настраивать Google Social Login только потому, что Python script должен читать REST API.

---

# Часть LVII. Connected App — тоже соседняя задача

## 193. Connected App используется когда сам Frappe идёт во внешний OAuth service

Например:

```text
Frappe
→ Google API
```

---

## 194. В этой главе основное направление другое

```text
External Client
→ Frappe API
```

Поэтому здесь основной объект для OAuth provider scenario:

```text
OAuth Client
```

---

# Часть LVIII. `auth_hooks`

## 195. Порядок мысли

```text
стандартный Frappe API Key подходит?
→ используй его

нужен delegated OAuth?
→ OAuth

организация требует собственный auth protocol?
→ auth_hooks
```

---

## 196. Custom auth увеличивает ответственность

Вы сами отвечаете за:

```text
verification
expiry
key rotation
issuer trust
replay protection
identity mapping
error handling
logging
```

---

# Часть LIX. Authentication и API v1/v2

## 197. Authentication header общий

Один и тот же token может использоваться для:

```text
/api/resource/...
/api/method/...
/api/v1/...
/api/v2/document/...
/api/v2/method/...
```

если User имеет необходимые permissions.

---

## 198. API version не создаёт отдельную identity

Переход:

```text
v1 → v2
```

не требует другого API User только из-за версии endpoint.

---

# Часть LX. Практика: создаём integration identity

## 199. Шаг 1. Создай отдельного User

Например:

```text
integration-requests@example.local
```

---

## 200. Шаг 2. Создай отдельную Role

```text
Request Integration
```

---

## 201. Шаг 3. Выдай минимальные permissions

Например:

```text
Request
Read   ✓
Create ✓
Write  ✓
Delete ✗
```

---

## 202. Шаг 4. Generate Keys

В User:

```text
Settings
→ API Access
→ Generate Keys
```

---

## 203. Шаг 5. Сохрани secret сразу в secret store

Не в README.

Не в Git.

Не в общий чат.

---

## 204. Шаг 6. Проверь identity

```bash
curl \
  "https://example.com/api/method/frappe.auth.get_logged_user" \
  -H "Authorization: token API_KEY:API_SECRET"
```

---

## 205. Шаг 7. Проверь Read

```bash
curl \
  "https://example.com/api/v2/document/Request?limit=1" \
  -H "Authorization: token API_KEY:API_SECRET"
```

---

## 206. Шаг 8. Проверь только реально нужные write operations

Не проверяй систему выдачей лишних permissions.

---

# Часть LXI. Практика: Python client

## 207. Environment

```bash
export FRAPPE_URL="https://example.com"
export FRAPPE_API_KEY="..."
export FRAPPE_API_SECRET="..."
```

---

## 208. Client

```python
import os
import requests

BASE_URL = os.environ["FRAPPE_URL"].rstrip("/")
API_KEY = os.environ["FRAPPE_API_KEY"]
API_SECRET = os.environ["FRAPPE_API_SECRET"]

client = requests.Session()
client.headers.update({
    "Authorization": f"token {API_KEY}:{API_SECRET}",
    "Accept": "application/json",
})

response = client.get(
    f"{BASE_URL}/api/v2/document/Request",
    params={"limit": 10},
    timeout=30,
)

response.raise_for_status()
print(response.json())
```

---

## 209. Что здесь правильно

```text
secret не в source code
HTTPS
explicit timeout
Authorization header
raise_for_status
persistent HTTP session
```

---

# Часть LXII. Практика: session client

## 210. Когда действительно нужен session flow

Например testing browser-like behavior.

---

## 211. Python

```python
import requests

session = requests.Session()

login = session.post(
    "https://example.com/api/method/login",
    json={
        "usr": "user@example.com",
        "pwd": "PASSWORD",
    },
    timeout=30,
)

login.raise_for_status()

me = session.get(
    "https://example.com/api/method/frappe.auth.get_logged_user",
    timeout=30,
)

me.raise_for_status()
print(me.json())
```

---

## 212. Но для production server integration обычно проще token auth

Не приходится управлять:

```text
password login
session expiry
cookie jar
2FA flow
CSRF browser semantics
```

---

# Часть LXIII. Decision table

## 213. Что выбирать

| Сценарий | Authentication |
|---|---|
| Desk / Website user в browser | Session |
| Backend service → Frappe | API Key + API Secret |
| ETL / n8n / integration server | API Key + API Secret |
| Стороннее приложение от имени пользователя | OAuth 2 |
| SPA/mobile с user authorization | OAuth Code + PKCE или подходящая session architecture |
| Public endpoint | Guest только если действительно public |
| Corporate custom JWT gateway | `auth_hooks`, если стандартных механизмов недостаточно |
| Frappe → внешний OAuth provider | Connected App — это обратное направление |

---

# Часть LXIV. Архитектурная лестница

## 214. От простого к сложному

```text
одна доверенная backend integration
→ API Key + Secret

нужна browser session
→ login + session

нужно делегирование от многих пользователей
→ OAuth 2

нужен корпоративный нестандартный protocol
→ auth_hooks
```

---

## 215. Не усложняй раньше времени

Если один внутренний Python service должен каждые 10 минут читать два DocType,

не нужно строить собственный identity provider только ради этого.

---

# Часть LXV. Финальная модель

## 216. REST/RPC не определяют identity

```text
REST
RPC
```

определяют:

```text
что вызывается
```

Authentication определяет:

```text
кто вызывает
```

---

## 217. Token не определяет права сам по себе

```text
API Key + Secret
→ User
→ Roles / Permissions
```

---

## 218. OAuth тоже не превращает пользователя в Administrator

OAuth token представляет конкретную granted identity и работает внутри permission model Framework.

---

## 219. Безопасная integration — это сочетание слоёв

```text
HTTPS
+
правильная Authentication
+
минимальные Permissions
+
безопасный RPC code
+
secret management
+
rotation/revocation
+
logging/audit
```

Ни один слой не заменяет остальные.

---

# Что нужно запомнить

1. Authentication отвечает на вопрос «кто делает request».
2. Authorization отвечает на вопрос «что этому User разрешено».
3. RPC whitelist отвечает на вопрос «можно ли эту функцию вызвать по HTTP».
4. Без authentication request обычно выполняется как `Guest`.
5. Для интеграций Frappe v16 поддерживает session/password, API Key + API Secret и OAuth 2 Bearer tokens.
6. Session login выполняется через `POST /api/method/login` и создаёт `sid` cookie.
7. Session-based unsafe requests связаны с CSRF protection.
8. Не отключай CSRF глобально только ради custom client.
9. Для server-to-server integration обычно проще API Key + API Secret.
10. API credentials принадлежат конкретному Frappe User.
11. Permissions API request определяются permissions этого User.
12. Header Frappe token auth имеет вид `Authorization: token API_KEY:API_SECRET`.
13. Frappe также поддерживает Basic с base64 от `API_KEY:API_SECRET`; это не нужно путать с обычным username/password Basic Auth.
14. Base64 ничего не шифрует — production API должен использовать HTTPS.
15. `Generate Keys` в v16 требует `System Manager` и POST.
16. При первом Generate Keys создаются API Key и Secret; при повторном существующий API Key сохраняется, а API Secret заменяется.
17. Один User имеет один текущий штатный API Secret.
18. Поэтому отдельный User на каждую интеграцию значительно удобнее для rotation и audit.
19. Disabled User не проходит обычную API Key authentication.
20. Не используй Administrator как integration identity без крайней необходимости.
21. Не используй человеческий account как service identity.
22. Permanent API Secret нельзя размещать во frontend JavaScript или mobile bundle.
23. Secrets нельзя хранить в Git, README, issue tracker или обычном общем чате.
24. OAuth 2 нужен прежде всего для delegated access сторонних приложений от имени пользователей.
25. Frappe умеет выступать OAuth Provider через `OAuth Client`.
26. OAuth access token передаётся как `Authorization: Bearer ACCESS_TOKEN`.
27. Frappe OAuth flow поддерживает Authorization Code, refresh token и документированный PKCE flow.
28. `state` в OAuth flow нужен для защиты redirect/authorization процесса и должен проверяться client-ом.
29. `OAuth Client` и `Connected App` — противоположные направления интеграции.
30. CORS не является authentication и не является authorization.
31. CORS и CSRF решают разные browser security задачи.
32. `auth_hooks` позволяют App подключить custom request authentication и установить Frappe User.
33. Custom auth следует писать только когда стандартных API Key/OAuth механизмов действительно недостаточно.
34. Если custom auth принимает JWT, нужно проверять подпись, issuer, audience, expiry и остальные security properties, а не только декодировать payload.
35. `frappe.auth.get_logged_user` — удобный первый diagnostic endpoint.
36. `401` обычно указывает на authentication problem, `403` — на authorization problem.
37. Rotation credential и revocation должны быть предусмотрены заранее.
38. Неверный credential не нужно бесконечно retry-ить как network timeout.
39. Authentication одинаково применяется к REST и RPC: API version не создаёт отдельную identity.
40. Хорошая integration security строится из HTTPS + identity + minimum permissions + secure secret storage + audit.

---

# Источники

Официальная документация Frappe Framework:

- [REST API — Authentication](https://docs.frappe.io/framework/user/en/api/rest)
- [Token Based Authentication](https://docs.frappe.io/framework/user/en/guides/integration/rest_api/token_based_authentication)
- [Simple Authentication](https://docs.frappe.io/framework/user/en/guides/integration/rest_api/simple_authentication)
- [OAuth 2](https://docs.frappe.io/framework/user/en/guides/integration/rest_api/oauth-2)
- [How to setup OAuth 2](https://docs.frappe.io/framework/user/en/guides/integration/how_to_set_up_oauth)
- [Using Frappe as OAuth Service](https://docs.frappe.io/framework/user/en/using_frappe_as_oauth_service)
- [Connected App](https://docs.frappe.io/framework/user/en/guides/app-development/connected-app)
- [Hooks — Auth Hooks](https://docs.frappe.io/framework/user/en/python-api/hooks)
- [Users and Permissions](https://docs.frappe.io/framework/user/en/basics/users-and-permissions)
- [Site Configuration](https://docs.frappe.io/framework/user/en/basics/site_config)

Для поведения v16 дополнительно сверено с исходным кодом ветки `version-16`:

- [`frappe/auth.py`](https://github.com/frappe/frappe/blob/version-16/frappe/auth.py)
- [`frappe/app.py`](https://github.com/frappe/frappe/blob/version-16/frappe/app.py)
- [`frappe/sessions.py`](https://github.com/frappe/frappe/blob/version-16/frappe/sessions.py)
- [`frappe/core/doctype/user/user.py`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/user/user.py)
- [`frappe/core/doctype/user/user.json`](https://github.com/frappe/frappe/blob/version-16/frappe/core/doctype/user/user.json)
- [`frappe/integrations/oauth2.py`](https://github.com/frappe/frappe/blob/version-16/frappe/integrations/oauth2.py)

Отдельно учтено расхождение старого примера Simple Authentication с текущим v16: logout в исходном коде `version-16` разрешён через `POST`, поэтому в этой главе используется `POST /api/method/logout`.

---

Следующая глава: **44. Client Script**.
