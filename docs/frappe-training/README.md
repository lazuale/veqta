# Frappe Training CORE

Статус: **принятый baseline CORE с обязательной коррекцией role provisioning**.

Основные документы:

1. [`ARCHITECTURE_PASSPORT.md`](ARCHITECTURE_PASSPORT.md)
2. [`REQUIREMENTS_MATRIX.md`](REQUIREMENTS_MATRIX.md)
3. [`STAGE_DEPENDENCY_GRAPH.md`](STAGE_DEPENDENCY_GRAPH.md)
4. [`PRACTICUM_ROADMAP.md`](PRACTICUM_ROADMAP.md)
5. [`CORE_STAGE_SPECIFICATION.md`](CORE_STAGE_SPECIFICATION.md)
6. [`core/`](core/README.md) — исполняемые этапы S00–S09

## Обязательная baseline-коррекция

Перед чтением delivery/permissions частей используйте:

- [`BASELINE_CORRECTIONS.md`](BASELINE_CORRECTIONS.md)
- [`../frappe-architecture-standard/13_ROLE_PROVISIONING.md`](../frappe-architecture-standard/13_ROLE_PROVISIONING.md)

Они исправляют единственный обнаруженный после принятия CORE delivery-contract:

```text
СТАРОЕ
Role names
→ Role fixtures
→ fixtures/role.json

АКТУАЛЬНОЕ ДЛЯ ЭТОГО CORE
Role names
→ Standard DocPerm собственного App
→ make_module_and_roles() при Standard DocType sync
```

Если в больших ранее принятых документах встречается старое утверждение `Role → fixture`, оно считается superseded этой коррекцией.

Исполняемые этапы уже приведены к актуальной модели:

- [`core/S05D_ROLES_AND_PERMISSIONS.md`](core/S05D_ROLES_AND_PERMISSIONS.md)
- [`core/S08_APP_STATE_DELIVERY_AUDIT.md`](core/S08_APP_STATE_DELIVERY_AUDIT.md)
- [`core/S09_CLEAN_INSTALL_ACCEPTANCE.md`](core/S09_CLEAN_INSTALL_ACCEPTANCE.md)

Все остальные решения первого CORE остаются без изменений.
