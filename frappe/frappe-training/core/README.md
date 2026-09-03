# Практические этапы Frappe

Практикум последовательно проводит через создание собственного Frappe `App`.

Каждый этап продолжает состояние предыдущего. Начните с `S00` и двигайтесь по порядку.

| Этап | Результат |
|---|---|
| [S00](S00_ENVIRONMENT.md) | подготовлена чистая среда Frappe v16 |
| [S01](S01_APP_AND_SITE.md) | создан и установлен `rental_training` |
| [S02](S02_EQUIPMENT_DOCTYPE.md) | создан самостоятельный `Equipment` |
| [S03](S03_CUSTOMER_DOCTYPE.md) | создан самостоятельный `Customer` |
| [S04](S04_RENTAL_COMPOSITION.md) | собраны `Rental`, `Rental Item` и связи между документами |
| [S05A](S05A_RENTAL_STATUS.md) | добавлено предметное состояние Rental |
| [S05B](S05B_DESK_VERTICAL_SCENARIO.md) | пройден полный рабочий сценарий через Desk |
| [S05C](S05C_RENTAL_LOCAL_INVARIANTS.md) | добавлены серверные проверки одного Rental |
| [S05D](S05D_ROLES_AND_PERMISSIONS.md) | настроены роли и базовые permissions |
| [S06](S06_ACTIVE_RENTAL_CONFLICT.md) | запрещены пересекающиеся Active Rentals одного Equipment |
| [S07](S07_AUTOMATED_CONTRACT_TESTS.md) | критические правила покрыты автоматическими тестами |
| [S08](S08_APP_STATE_DELIVERY_AUDIT.md) | разобрано, какое состояние принадлежит App, а какое Site |
| [S09](S09_CLEAN_INSTALL_ACCEPTANCE.md) | приложение проверено установкой на новый чистый Site |

После S09 получается небольшое, но полностью воспроизводимое приложение: модель и правила хранятся в `App`, а экземплярные данные остаются на `Site`.

Общее описание практикума: [`../README.md`](../README.md).