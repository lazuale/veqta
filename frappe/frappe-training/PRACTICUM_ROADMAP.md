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

1. **[S00 — среда](core/S00_ENVIRONMENT.md)**  
   Подготовить совместимый Bench и чистый `rental.localhost`.

2. **[S01 — App и Site](core/S01_APP_AND_SITE.md)**  
   Создать `rental_training`, установить его на Site и увидеть границы Bench / App / Site / Module.

3. **[S02 — Equipment](core/S02_EQUIPMENT_DOCTYPE.md)**  
   Создать первый самостоятельный Standard DocType.

4. **[S03 — Customer](core/S03_CUSTOMER_DOCTYPE.md)**  
   Добавить второй самостоятельный Document.

5. **[S04 — Rental](core/S04_RENTAL_COMPOSITION.md)**  
   Связать Customer и несколько Equipment через `Rental` и `Rental Item`.

6. **[S05A — состояние](core/S05A_RENTAL_STATUS.md)**  
   Добавить предметный `status` без лишнего Workflow.

7. **[S05B — Desk](core/S05B_DESK_VERTICAL_SCENARIO.md)**  
   Пройти рабочий сценарий через стандартный интерфейс Frappe.

8. **[S05C — локальные инварианты](core/S05C_RENTAL_LOCAL_INVARIANTS.md)**  
   Добавить первые серверные проверки Rental.

9. **[S05D — роли и permissions](core/S05D_ROLES_AND_PERMISSIONS.md)**  
   Разделить возможности оператора и менеджера штатной моделью доступа.

10. **[S06 — конфликт Rentals](core/S06_ACTIVE_RENTAL_CONFLICT.md)**  
    Проверить правило, которое требует чтения других Documents.

11. **[S07 — тесты](core/S07_AUTOMATED_CONTRACT_TESTS.md)**  
    Закрепить критические правила автоматическими проверками.

12. **[S08 — поставка состояния](core/S08_APP_STATE_DELIVERY_AUDIT.md)**  
    Разобрать, что принадлежит App и что остаётся данными Site.

13. **[S09 — чистая установка](core/S09_CLEAN_INSTALL_ACCEPTANCE.md)**  
    Установить приложение на новый Site и проверить воспроизводимость результата.

Описание модели: [`CORE_STAGE_SPECIFICATION.md`](CORE_STAGE_SPECIFICATION.md). Требования: [`REQUIREMENTS_MATRIX.md`](REQUIREMENTS_MATRIX.md).