# NovaPOS — Convenciones Técnicas del Proyecto

## 1. Objetivo

Este documento define las convenciones técnicas oficiales de NovaPOS.
Todo archivo, carpeta, endpoint, tabla, modelo, servicio y componente debe seguir estas reglas para mantener orden, escalabilidad y consistencia.

---

## 2. Idioma del código

El código usará nombres en inglés para mantener estándar profesional.

Ejemplos:

* `products`
* `customers`
* `sales`
* `cash_register`
* `suppliers`
* `receipts`

La interfaz visible para el usuario estará en español.

Ejemplos:

* Emitir Recibo
* Inventario
* Clientes
* Fiados
* Caja

---

## 3. Backend

### Carpetas

Usar nombres en plural y snake_case cuando corresponda.

```txt
app/
├── core/
├── db/
├── models/
├── schemas/
├── repositories/
├── services/
├── routers/
├── utils/
└── middlewares/
```

### Archivos

Usar `snake_case`.

```txt
user_model.py
product_model.py
sale_service.py
cash_register_repository.py
auth_router.py
```

### Clases

Usar `PascalCase`.

```python
User
Product
SaleService
ProductRepository
```

### Funciones y variables

Usar `snake_case`.

```python
create_product()
get_active_store()
calculate_profit()
total_amount
```

---

## 4. Frontend

### Carpetas

Usar minúsculas.

```txt
components/
pages/
features/
services/
stores/
hooks/
types/
utils/
layouts/
routes/
```

### Componentes React

Usar `PascalCase`.

```txt
ProductCard.tsx
SaleSummary.tsx
MainLayout.tsx
```

### Hooks

Usar prefijo `use`.

```txt
useProducts.ts
useAuth.ts
useSales.ts
```

### Servicios API

Usar `camelCase`.

```txt
productService.ts
authService.ts
saleService.ts
```

### Tipos TypeScript

Usar `PascalCase`.

```ts
Product
Customer
Sale
PaymentMethod
ReceiptType
```

---

## 5. Base de datos

### Nombres de tablas

Usar plural en inglés y `snake_case`.

```txt
users
roles
products
customers
sales
sale_items
suppliers
cash_registers
cash_movements
receipts
credit_sales
audit_logs
```

### Columnas

Usar `snake_case`.

```txt
id
created_at
updated_at
deleted_at
is_active
created_by
updated_by
```

### IDs

Usar enteros autoincrementales en SQLite para la primera versión.

Preparar la arquitectura para migrar posteriormente a UUID si el sistema pasa a multiempresa en PostgreSQL.

---

## 6. Fechas y hora

La zona horaria oficial será:

```txt
America/Lima
```

Toda fecha debe guardarse en formato ISO.

```txt
YYYY-MM-DD HH:mm:ss
```

Campos estándar:

```txt
created_at
updated_at
deleted_at
```

---

## 7. Moneda

La moneda oficial inicial será:

```txt
PEN - Sol Peruano
```

Los montos deben manejarse con dos decimales.

Ejemplos:

```txt
10.00
25.50
120.90
```

No usar `float` para dinero.
Usar `Decimal` en backend.

---

## 8. Soft Delete

NovaPOS no eliminará registros físicamente.

Todo registro eliminable debe tener:

```txt
deleted_at
is_active
```

Regla:

```txt
Si deleted_at tiene valor, el registro se considera eliminado lógicamente.
```

---

## 9. Auditoría

Toda operación importante debe registrar auditoría.

Acciones mínimas:

```txt
CREATE
UPDATE
DELETE
LOGIN
SALE_CREATED
RECEIPT_GENERATED
WHATSAPP_SENT
CASH_CLOSED
BACKUP_CREATED
```

Tabla sugerida:

```txt
audit_logs
```

Campos mínimos:

```txt
id
user_id
store_id
action
entity
entity_id
description
created_at
```

---

## 10. Roles oficiales

Los roles iniciales son:

```txt
Administrador
Dueño
Cajero
```

En backend se manejarán como:

```txt
admin
owner
cashier
```

---

## 11. Métodos de pago

Solo existirán:

```txt
cash
yape
credit
```

Equivalencia visual:

```txt
cash   = Efectivo
yape   = Yape
credit = Fiado
```

Plin, transferencia u otra billetera se registrarán como:

```txt
yape
```

---

## 12. Tipos de comprobante

Solo existirán:

```txt
receipt_note
invoice
```

Equivalencia visual:

```txt
receipt_note = Nota de Venta
invoice      = Boleta
```

Reglas:

```txt
Boleta calcula IGV.
Nota de Venta no calcula IGV.
```

---

## 13. Estados generales

Usar estados claros en inglés dentro del sistema.

Ejemplos:

```txt
active
inactive
pending
paid
partial
cancelled
expired
low_stock
out_of_stock
```

No usar textos libres para estados.

---

## 14. Endpoints API

Usar plural, minúsculas y guiones medios si es necesario.

```txt
/api/v1/products
/api/v1/customers
/api/v1/sales
/api/v1/receipts
/api/v1/cash-registers
/api/v1/credit-sales
```

Acciones especiales:

```txt
POST /api/v1/sales/emit-receipt
POST /api/v1/cash-registers/close
POST /api/v1/receipts/{id}/send-whatsapp
```

---

## 15. Respuestas API

Toda respuesta debe ser clara y consistente.

Ejemplo exitoso:

```json
{
  "success": true,
  "message": "Operación realizada correctamente.",
  "data": {}
}
```

Ejemplo con error:

```json
{
  "success": false,
  "message": "Este producto ya existe.",
  "error": "DUPLICATE_PRODUCT"
}
```

---

## 16. Manejo de errores

Los errores deben tener códigos internos.

Ejemplos:

```txt
DUPLICATE_PRODUCT
PRODUCT_NOT_FOUND
INSUFFICIENT_STOCK
CUSTOMER_REQUIRED_FOR_CREDIT
CASH_REGISTER_CLOSED
INVALID_PAYMENT_METHOD
RECEIPT_NOT_FOUND
```

---

## 17. Archivos documentales

Los archivos se guardarán dentro de la carpeta de cada tienda.

Ejemplo:

```txt
data/Danae/uploads/comprobantes/
data/Danae/uploads/facturas/
data/Danae/uploads/productos/
data/Danae/uploads/logos/
data/Danae/uploads/ocr/
```

La base de datos solo guardará referencias/rutas, no archivos binarios.

---

## 18. Tiendas

Cada tienda tendrá su propia carpeta.

Ejemplo:

```txt
data/Danae/database.db
```

Nunca se deben mezclar datos entre tiendas.

Toda operación debe ejecutarse dentro del contexto de una tienda activa.

---

## 19. Commits

Formato recomendado:

```txt
feat: agregar modelo de productos
fix: corregir cálculo de stock
docs: actualizar reglas de negocio
refactor: reorganizar servicio de ventas
chore: configurar entorno inicial
```

---

## 20. Regla final

Si una convención no está definida aquí, debe decidirse antes de implementar el módulo correspondiente.

No se debe improvisar dentro del código.
