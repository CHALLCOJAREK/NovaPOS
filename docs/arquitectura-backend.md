# NovaPOS — Arquitectura Backend

## 1. Objetivo

Definir la arquitectura oficial del backend de NovaPOS, asegurando separación por capas, mantenibilidad, escalabilidad y preparación para migrar de SQLite a PostgreSQL sin rehacer la lógica del sistema.

---

## 2. Tecnología oficial

El backend usará:

```txt
Python
FastAPI
SQLAlchemy 2.0
Alembic
Pydantic
SQLite
PostgreSQL futuro
```

---

## 3. Estructura oficial

```txt
backend/
│
├── app/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── routers/
│   ├── utils/
│   ├── middlewares/
│   └── main.py
│
├── alembic/
├── alembic.ini
├── requirements.txt
├── .env
└── README.md
```

---

## 4. Responsabilidad de cada carpeta

### core

Contiene configuración central del sistema.

Ejemplos:

```txt
config.py
security.py
constants.py
exceptions.py
permissions.py
```

No debe contener lógica de negocio.

---

### db

Contiene conexión a base de datos, sesión y configuración de SQLAlchemy.

Ejemplos:

```txt
database.py
base.py
session.py
```

Debe permitir trabajar inicialmente con SQLite y posteriormente con PostgreSQL.

---

### models

Contiene modelos SQLAlchemy.

Ejemplos:

```txt
user_model.py
product_model.py
sale_model.py
customer_model.py
```

Los modelos representan tablas.

No deben contener lógica de negocio.

---

### schemas

Contiene esquemas Pydantic.

Ejemplos:

```txt
product_schema.py
sale_schema.py
customer_schema.py
auth_schema.py
```

Se usan para validar entrada y salida de datos.

---

### repositories

Contiene acceso a datos.

Ejemplos:

```txt
product_repository.py
sale_repository.py
customer_repository.py
```

Responsabilidades:

```txt
Crear registros
Consultar registros
Actualizar registros
Aplicar filtros
Consultar por ID
Consultar activos
```

No debe contener reglas de negocio.

---

### services

Contiene lógica de negocio.

Ejemplos:

```txt
sale_service.py
cash_register_service.py
receipt_service.py
credit_sale_service.py
```

Aquí viven las reglas del negocio.

Ejemplo:

```txt
Si una venta es Fiado:
- No suma caja
- No suma Yape
- Sí registra venta
- Sí genera deuda
- Sí genera utilidad
- Sí genera comprobante
```

---

### routers

Contiene endpoints FastAPI.

Ejemplos:

```txt
product_router.py
sale_router.py
auth_router.py
cash_register_router.py
```

Responsabilidades:

```txt
Recibir request
Validar schema
Llamar service
Retornar response
```

Nunca debe tener lógica de negocio.

---

### utils

Contiene funciones reutilizables.

Ejemplos:

```txt
date_utils.py
money_utils.py
file_utils.py
pdf_utils.py
image_utils.py
```

---

### middlewares

Contiene middlewares del sistema.

Ejemplos:

```txt
tenant_middleware.py
audit_middleware.py
error_handler.py
```

---

## 5. Flujo obligatorio de backend

Todo endpoint debe seguir este flujo:

```txt
Router
  ↓
Service
  ↓
Repository
  ↓
Model
  ↓
Database
```

Y la respuesta vuelve así:

```txt
Database
  ↓
Model
  ↓
Repository
  ↓
Service
  ↓
Router
  ↓
Client
```

---

## 6. Regla principal

Está prohibido mezclar lógica de negocio en routers.

Incorrecto:

```python
@router.post("/sales")
def create_sale(data):
    if data.payment_method == "credit":
        # lógica de fiado aquí
        pass
```

Correcto:

```python
@router.post("/sales")
def create_sale(data, service: SaleService):
    return service.create_sale(data)
```

---

## 7. Base de datos por tienda

Cada tienda tendrá su propia base SQLite.

Ejemplo:

```txt
data/Danae/database.db
```

El backend debe resolver la base activa según el contexto de tienda.

Primera versión:

```txt
DEFAULT_STORE=Danae
```

Futuro:

```txt
store_id
tenant_id
subdominio
usuario autenticado
```

---

## 8. Contexto de tienda

Toda operación debe ejecutarse dentro de una tienda activa.

Ejemplo inicial:

```txt
Danae
```

Ningún servicio debe operar sin conocer la tienda activa.

---

## 9. Migración futura a PostgreSQL

La lógica de negocio no debe depender de SQLite.

La conexión debe centralizarse en:

```txt
app/db/database.py
```

Así, cuando se migre a PostgreSQL, se cambiará configuración, no lógica de negocio.

---

## 10. Manejo de dinero

No usar `float`.

Usar:

```txt
Decimal
```

Ejemplo:

```python
from decimal import Decimal
```

Motivo:

```txt
Evitar errores de redondeo en precios, IGV, ganancias, caja y fiados.
```

---

## 11. Fechas

Toda fecha debe manejarse con zona horaria:

```txt
America/Lima
```

Campos estándar:

```txt
created_at
updated_at
deleted_at
```

---

## 12. Soft Delete

No se deben eliminar registros físicos.

Toda tabla eliminable debe tener:

```txt
is_active
deleted_at
```

Las consultas normales deben traer solo registros activos.

---

## 13. Auditoría

Toda acción crítica debe registrar auditoría.

Ejemplos:

```txt
Usuario inició sesión
Producto creado
Venta emitida
Comprobante generado
Fiado registrado
Caja cerrada
WhatsApp enviado
Backup generado
```

---

## 14. Seguridad

El backend usará:

```txt
JWT
Contraseñas hasheadas
Roles
Permisos
Auditoría
Validaciones Pydantic
```

Roles iniciales:

```txt
admin
owner
cashier
```

---

## 15. Respuesta estándar

Toda respuesta del backend debe seguir este formato:

```json
{
  "success": true,
  "message": "Operación realizada correctamente.",
  "data": {}
}
```

Error:

```json
{
  "success": false,
  "message": "Este producto ya existe.",
  "error": "DUPLICATE_PRODUCT"
}
```

---

## 16. Excepciones

Las excepciones personalizadas vivirán en:

```txt
app/core/exceptions.py
```

Ejemplos:

```txt
DuplicateProductError
ProductNotFoundError
InsufficientStockError
CustomerRequiredForCreditError
CashRegisterClosedError
```

---

## 17. Versionado API

Toda API debe estar bajo:

```txt
/api/v1
```

Ejemplos:

```txt
/api/v1/auth
/api/v1/products
/api/v1/sales
/api/v1/customers
/api/v1/receipts
```

---

## 18. Generación de comprobantes

La generación de PDF e imagen no debe estar en el router.

Debe vivir en servicios/utilidades:

```txt
receipt_service.py
pdf_utils.py
image_utils.py
```

Flujo:

```txt
sale_service
  ↓
receipt_service
  ↓
pdf_utils
  ↓
image_utils
```

---

## 19. WhatsApp

La integración con Evolution API debe estar aislada.

Ubicación sugerida:

```txt
app/services/whatsapp_service.py
```

El sistema debe registrar todo envío en base de datos.

---

## 20. OCR

El OCR debe estar separado.

Ubicación sugerida:

```txt
app/services/ocr_service.py
```

El OCR no actualiza inventario directamente.

Flujo obligatorio:

```txt
Subir documento
Procesar OCR
Guardar resultado
Usuario confirma
Actualizar inventario
```

---

## 21. Backups

Los backups deben estar en servicio separado.

Ubicación sugerida:

```txt
app/services/backup_service.py
```

Los backups se guardarán en:

```txt
data/Danae/backups/
```

---

## 22. Regla final

El backend debe priorizar claridad, separación de responsabilidades y mantenibilidad.

Si una funcionalidad no tiene diseño previo, no se implementa.
