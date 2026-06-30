# NovaPOS — Modelo Base de Datos

## 1. Objetivo

Definir el modelo inicial de base de datos de NovaPOS para SQLite, preparado para una futura migración a PostgreSQL.

---

## 2. Principios

* Cada tienda tendrá su propia base SQLite.
* No se mezclarán datos entre tiendas.
* No se eliminarán registros físicamente.
* Se usará Soft Delete.
* Toda operación crítica será auditada.
* Los montos se manejarán como Decimal.
* Los comprobantes serán permanentes.

---

## 3. Tablas base

```txt
stores
users
roles
user_roles
permissions
role_permissions
audit_logs
```

---

## 4. Tablas comerciales

```txt
suppliers
customers
products
product_categories
inventory_entries
inventory_entry_items
sales
sale_items
receipts
credit_sales
credit_payments
cash_registers
cash_movements
whatsapp_messages
ocr_documents
ocr_items
backups
```

---

## 5. stores

Guarda los datos generales de cada tienda.

Campos:

```txt
id
name
slug
ruc
address
phone
whatsapp
yape_number
logo_path
data_path
is_active
created_at
updated_at
deleted_at
```

---

## 6. users

Usuarios del sistema.

Campos:

```txt
id
store_id
full_name
username
email
password_hash
is_active
created_at
updated_at
deleted_at
```

---

## 7. roles

Roles oficiales.

Campos:

```txt
id
name
code
description
is_active
created_at
updated_at
deleted_at
```

Roles iniciales:

```txt
admin
owner
cashier
```

---

## 8. user_roles

Relación entre usuarios y roles.

Campos:

```txt
id
user_id
role_id
created_at
```

---

## 9. suppliers

Proveedores.

Campos:

```txt
id
store_id
name
ruc
phone
whatsapp
email
address
contact_name
is_active
created_at
updated_at
deleted_at
```

---

## 10. customers

Clientes.

Campos:

```txt
id
store_id
full_name
document_number
phone
whatsapp
address
total_purchased
total_debt
is_active
created_at
updated_at
deleted_at
```

---

## 11. product_categories

Categorías de productos.

Campos:

```txt
id
store_id
name
description
is_active
created_at
updated_at
deleted_at
```

---

## 12. products

Productos comerciales.

Campos:

```txt
id
store_id
supplier_id
category_id
image_path
code
barcode
name
brand
unit
cost_price
sale_price
margin_percentage
profit_amount
stock
minimum_stock
expiration_date
lot
is_weight_product
is_cold_modifier_enabled
cold_extra_price
status
is_active
created_at
updated_at
deleted_at
```

Reglas:

```txt
code no debe repetirse dentro de la misma tienda.
barcode no debe repetirse dentro de la misma tienda si existe.
Los productos helados no se duplican.
El modificador helado incrementa el precio.
```

---

## 13. inventory_entries

Cabecera de ingreso de inventario.

Campos:

```txt
id
store_id
supplier_id
invoice_number
document_type
document_path
entry_date
total_amount
notes
created_by
created_at
updated_at
deleted_at
```

---

## 14. inventory_entry_items

Detalle del ingreso de inventario.

Campos:

```txt
id
inventory_entry_id
product_id
package_total_cost
package_quantity
unit_cost
margin_percentage
suggested_sale_price
final_sale_price
quantity_added
expiration_date
lot
created_at
updated_at
deleted_at
```

Regla:

```txt
unit_cost = package_total_cost / package_quantity
```

---

## 15. cash_registers

Caja diaria.

Campos:

```txt
id
store_id
opened_by
closed_by
opening_amount
counted_cash_amount
expected_cash_amount
expected_yape_amount
total_sales
total_cash
total_yape
total_credit
total_cost
total_profit
difference_amount
status
opened_at
closed_at
created_at
updated_at
deleted_at
```

Estados:

```txt
open
closed
```

---

## 16. cash_movements

Movimientos de caja.

Campos:

```txt
id
store_id
cash_register_id
movement_type
payment_method
amount
description
reference_type
reference_id
created_by
created_at
deleted_at
```

Tipos:

```txt
sale
income
expense
adjustment
credit_payment
```

---

## 17. sales

Cabecera de venta.

Campos:

```txt
id
store_id
cash_register_id
customer_id
receipt_id
sale_code
payment_method
receipt_type
subtotal
igv_amount
total_amount
total_cost
total_profit
status
created_by
created_at
updated_at
deleted_at
```

Métodos de pago:

```txt
cash
yape
credit
```

Tipos de comprobante:

```txt
invoice
receipt_note
```

---

## 18. sale_items

Detalle de venta.

Campos:

```txt
id
sale_id
product_id
product_name
quantity
weight
unit_price
cost_price
subtotal
profit_amount
is_cold
cold_extra_price
created_at
updated_at
deleted_at
```

Reglas:

```txt
Si is_cold = true, se suma cold_extra_price.
Si es producto por peso, se usa weight.
```

---

## 19. receipts

Comprobantes generados.

Campos:

```txt
id
store_id
sale_id
receipt_type
receipt_number
pdf_path
image_path
subtotal
igv_amount
total_amount
is_sent_whatsapp
sent_whatsapp_at
created_by
created_at
updated_at
deleted_at
```

Reglas:

```txt
Boleta calcula IGV.
Nota de Venta no calcula IGV.
Todo comprobante se guarda en PDF e imagen.
Nunca se elimina físicamente.
```

---

## 20. credit_sales

Fiados generados por ventas.

Campos:

```txt
id
store_id
sale_id
customer_id
total_amount
paid_amount
balance_amount
status
due_date
created_by
created_at
updated_at
deleted_at
```

Estados:

```txt
pending
partial
paid
cancelled
```

---

## 21. credit_payments

Pagos parciales de fiados.

Campos:

```txt
id
store_id
credit_sale_id
customer_id
payment_method
amount
notes
created_by
created_at
deleted_at
```

Regla:

```txt
Todo pago de fiado sí suma a caja o Yape según método.
```

---

## 22. whatsapp_messages

Historial de envíos por WhatsApp.

Campos:

```txt
id
store_id
customer_id
phone
message_type
message
file_path
status
provider_response
sent_by
sent_at
created_at
deleted_at
```

Tipos:

```txt
receipt
report
purchase_list
credit_reminder
cash_closing
```

Estados:

```txt
pending
sent
failed
```

---

## 23. ocr_documents

Documentos procesados por OCR.

Campos:

```txt
id
store_id
supplier_id
document_type
image_path
raw_text
total_amount
document_date
status
created_by
created_at
updated_at
deleted_at
```

Estados:

```txt
processed
confirmed
rejected
```

---

## 24. ocr_items

Productos detectados por OCR.

Campos:

```txt
id
ocr_document_id
product_name
quantity
unit_price
total_price
matched_product_id
status
created_at
updated_at
deleted_at
```

---

## 25. audit_logs

Auditoría del sistema.

Campos:

```txt
id
store_id
user_id
action
entity
entity_id
description
created_at
```

---

## 26. backups

Respaldos generados.

Campos:

```txt
id
store_id
backup_path
backup_type
status
size_mb
created_by
created_at
```

Tipos:

```txt
manual
automatic
```

Estados:

```txt
created
failed
```

---

## 27. Relaciones principales

```txt
stores 1 → N users
stores 1 → N products
stores 1 → N customers
stores 1 → N suppliers
stores 1 → N sales
stores 1 → N receipts

suppliers 1 → N products
product_categories 1 → N products

customers 1 → N sales
customers 1 → N credit_sales

sales 1 → N sale_items
sales 1 → 1 receipt
sales 1 → 0/1 credit_sale

cash_registers 1 → N sales
cash_registers 1 → N cash_movements

inventory_entries 1 → N inventory_entry_items
products 1 → N inventory_entry_items
products 1 → N sale_items
```

---

## 28. Regla final

Este modelo será la base inicial del sistema.

Cualquier cambio en tablas, relaciones o campos debe justificarse antes de implementarse.
