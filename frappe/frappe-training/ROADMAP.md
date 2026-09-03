# Маршрут практикума Frappe

Практикум проходит один путь от чистого Frappe до воспроизводимого учебного приложения.

```text
среда
  ↓
App и Site
  ↓
самостоятельные DocTypes
  ↓
связи и Child DocType
  ↓
предметное состояние
  ↓
Desk
  ↓
серверные правила
  ↓
permissions
  ↓
междокументное правило
  ↓
автоматические тесты
  ↓
поставка состояния App
  ↓
чистая установка
```

## Этапы

1. **[S00 — среда](stages/S00_ENVIRONMENT.md)**  
   Подготовить совместимый Bench и чистый `rental.localhost`.

2. **[S01 — App и Site](stages/S01_APP_AND_SITE.md)**  
   Создать `rental_training`, установить его на Site и увидеть границы Bench / App / Site / Module.

3. **[S02 — Equipment](stages/S02_EQUIPMENT_DOCTYPE.md)**  
   Создать первый самостоятельный Standard DocType.

4. **[S03 — Customer](stages/S03_CUSTOMER_DOCTYPE.md)**  
   Добавить второй самостоятельный Document.

5. **[S04 — Rental](stages/S04_RENTAL_COMPOSITION.md)**  
   Связать Customer и несколько Equipment через `Rental` и `Rental Item`.

6. **[S05A — состояние](stages/S05A_RENTAL_STATUS.md)**  
   Добавить предметный `status` без лишнего Workflow.

7. **[S05B — Desk](stages/S05B_DESK_VERTICAL_SCENARIO.md)**  
   Пройти рабочий сценарий через стандартный интерфейс Frappe.

8. **[S05C — локальные инварианты](stages/S05C_RENTAL_LOCAL_INVARIANTS.md)**  
   Добавить первые серверные проверки Rental.

9. **[S05D — роли и permissions](stages/S05D_ROLES_AND_PERMISSIONS.md)**  
   Разделить возможности оператора и менеджера штатной моделью доступа.

10. **[S06 — конфликт Rentals](stages/S06_ACTIVE_RENTAL_CONFLICT.md)**  
    Проверить правило, которое требует чтения других Documents.

11. **[S07 — тесты](stages/S07_AUTOMATED_CONTRACT_TESTS.md)**  
    Закрепить критические правила автоматическими проверками.

12. **[S08 — поставка состояния](stages/S08_APP_STATE_DELIVERY.md)**  
    Разобрать, что принадлежит App и что остаётся данными Site.

13. **[S09 — чистая установка](stages/S09_CLEAN_INSTALL.md)**  
    Установить приложение на новый Site и проверить воспроизводимость результата.

Описание модели: [`APPLICATION_MODEL.md`](APPLICATION_MODEL.md). Требования: [`REQUIREMENTS.md`](REQUIREMENTS.md).