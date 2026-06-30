# NovaPOS — Módulos Oficiales del Sistema

## 1. Objetivo

Definir los módulos funcionales oficiales de NovaPOS, sus responsabilidades, dependencias y orden de implementación.

Este documento evita agregar funcionalidades innecesarias y mantiene el desarrollo alineado al Documento Maestro.

---

## 2. Orden oficial de implementación

```txt
1. Configuración base del sistema
2. Autenticación y usuarios
3. Roles y permisos
4. Proveedores
5. Clientes
6. Productos
7. Inventario
8. Caja
9. Emitir Recibo
10. Comprobantes
11. Fiados
12. Cierre de caja
13. Reportes
14. Productos por comprar
15. Productos próximos a vencer
16. Centro de Inteligencia
17. OCR
18. WhatsApp
19. Respaldos
```

---

## 3. Módulo 1 — Configuración base del sistema

### Responsabilidad

Gestionar los datos generales de la tienda.

Incluye:

```txt
Nombre de tienda
Logo
Dirección
RUC
WhatsApp
Número Yape
Impresora
Tienda activa
Ruta de datos
```

### Dependencias

No depende de otros módulos.

### Es necesario porque

Todo el sistema debe operar dentro del contexto de una tienda activa.

---

## 4. Módulo 2 — Autenticación y usuarios

### Responsabilidad

Permitir acceso seguro al sistema.

Incluye:

```txt
Login
JWT
Contraseña hasheada
Usuario activo/inactivo
Sesión
```

### Dependencias

Depende de:

```txt
Configuración base
```

---

## 5. Módulo 3 — Roles y permisos

### Responsabilidad

Controlar qué puede hacer cada usuario.

Roles oficiales:

```txt
Administrador
Dueño
Cajero
```

Backend:

```txt
admin
owner
cashier
```

### Dependencias

Depende de:

```txt
Usuarios
```

---

## 6. Módulo 4 — Proveedores

### Responsabilidad

Registrar y consultar proveedores.

Incluye:

```txt
Nombre
RUC
Teléfono
WhatsApp
Correo
Dirección
Contacto
Productos suministrados
Historial
```

### Dependencias

Depende de:

```txt
Usuarios
Auditoría
```

---

## 7. Módulo 5 — Clientes

### Responsabilidad

Gestionar clientes y su historial.

Incluye:

```txt
Nombre
Documento
Teléfono
WhatsApp
Dirección
Compras
Fiados
Monto total comprado
```

### Dependencias

Depende de:

```txt
Usuarios
Auditoría
```

---

## 8. Módulo 6 — Productos

### Responsabilidad

Gestionar productos comerciales.

Incluye:

```txt
Imagen
Código
Código de barras
Nombre
Marca
Categoría
Proveedor
Unidad
Precio costo
Precio venta
Margen
Ganancia
Stock
Stock mínimo
Caducidad
Lote
Estado
```

### Reglas importantes

```txt
No permitir códigos duplicados.
Si el producto existe, mostrar: "Este producto ya existe."
Los productos helados serán modificadores, no productos duplicados.
Los productos por peso se manejarán con precio por kilo.
```

### Dependencias

Depende de:

```txt
Proveedores
Usuarios
Auditoría
```

---

## 9. Módulo 7 — Inventario

### Responsabilidad

Registrar compras e ingresos de stock.

Incluye:

```txt
Costo total del paquete
Cantidad del paquete
Costo unitario calculado
Margen
Precio sugerido
Precio final modificable
Proveedor
Factura
Fecha
Caducidad
Lote
```

### Reglas importantes

```txt
No se registra directamente el precio de venta.
NovaPOS calcula primero el costo unitario.
Luego calcula precio sugerido según margen.
```

### Dependencias

Depende de:

```txt
Productos
Proveedores
Auditoría
```

---

## 10. Módulo 8 — Caja

### Responsabilidad

Gestionar caja diaria.

Incluye:

```txt
Caja abierta
Movimientos
Ventas
Efectivo
Yape
Fiados
Historial
```

### Dependencias

Depende de:

```txt
Usuarios
Ventas
Auditoría
```

---

## 11. Módulo 9 — Emitir Recibo

### Responsabilidad

Pantalla principal de venta.

Debe permitir vender en menos de 30 segundos.

Incluye:

```txt
Escáner
Buscar producto
Producto por peso
Cliente opcional
Tipo de comprobante
Método de pago
Checks de acciones
Botón EMITIR RECIBO
```

### Tipos de comprobante

```txt
Boleta
Nota de Venta
```

### Métodos de pago

```txt
Efectivo
Yape
Fiado
```

### Reglas importantes

```txt
No usar "Nueva Venta".
No crear botones independientes para acciones secundarias.
Todo debe manejarse mediante checks o selectores.
```

### Dependencias

Depende de:

```txt
Productos
Clientes
Caja
Comprobantes
Fiados
Auditoría
```

---

## 12. Módulo 10 — Comprobantes

### Responsabilidad

Generar, guardar y consultar comprobantes.

Incluye:

```txt
Boleta
Nota de Venta
PDF
Imagen PNG
Visualizar
Descargar
Reimprimir
Reenviar por WhatsApp
```

### Reglas importantes

```txt
Boleta calcula IGV.
Nota de Venta no calcula IGV.
Todo comprobante se guarda permanentemente.
Nunca eliminar comprobantes.
```

### Dependencias

Depende de:

```txt
Ventas
Clientes
WhatsApp
Auditoría
```

---

## 13. Módulo 11 — Fiados

### Responsabilidad

Gestionar ventas al crédito/fiado.

Incluye:

```txt
Monto
Fecha
Cliente
Productos
Pagos parciales
Saldo
Historial
Recordatorios por WhatsApp
```

### Reglas importantes

```txt
Fiado no suma dinero a caja.
Fiado no suma dinero a Yape.
Fiado sí registra venta.
Fiado sí registra utilidad.
Fiado sí genera deuda.
```

### Dependencias

Depende de:

```txt
Clientes
Ventas
Comprobantes
WhatsApp
Auditoría
```

---

## 14. Módulo 12 — Cierre de caja

### Responsabilidad

Cerrar la caja diaria mediante proceso guiado.

Incluye:

```txt
Resumen
Conteo efectivo
Confirmar Yape
Verificar diferencias
Confirmación
Enviar reporte
Cerrar caja
```

### Al cerrar

Debe generar reporte con:

```txt
Ventas
Costo
Ganancia
Margen
Cobrado efectivo
Cobrado Yape
Fiados
Productos vendidos
Productos por comprar
Productos próximos a vencer
Productos con stock bajo
```

### Dependencias

Depende de:

```txt
Caja
Ventas
Reportes
WhatsApp
Auditoría
```

---

## 15. Módulo 13 — Reportes

### Responsabilidad

Generar reportes del negocio.

Incluye:

```txt
Ventas
Compras
Ganancias
Productos
Clientes
Fiados
Caja
Proveedores
Inventario
Caducidad
Stock
```

### Exportación

```txt
PDF
Excel
```

### Dependencias

Depende de:

```txt
Todos los módulos operativos
```

---

## 16. Módulo 14 — Productos por comprar

### Responsabilidad

Calcular automáticamente productos que deben reponerse.

Incluye:

```txt
Stock actual
Stock mínimo
Ventas promedio
Proveedor
Cantidad sugerida
Costo estimado
PDF
Envío por WhatsApp
```

### Dependencias

Depende de:

```txt
Productos
Inventario
Ventas
Proveedores
Reportes
WhatsApp
```

---

## 17. Módulo 15 — Productos próximos a vencer

### Responsabilidad

Detectar productos cercanos a caducar.

Incluye:

```txt
Producto
Lote
Fecha
Días restantes
Cantidad
Alerta
```

### Dependencias

Depende de:

```txt
Productos
Inventario
Centro de Inteligencia
WhatsApp
```

---

## 18. Módulo 16 — Centro de Inteligencia

### Responsabilidad

Mostrar recomendaciones inteligentes.

No será chatbot.

Incluye:

```txt
Productos por comprar
Productos por vencer
Productos sin movimiento
Clientes con deuda
Productos más rentables
Productos menos rentables
Ganancia semanal
Comparación mensual
```

### Dependencias

Depende de:

```txt
Ventas
Productos
Clientes
Fiados
Inventario
Caja
```

---

## 19. Módulo 17 — OCR

### Responsabilidad

Leer documentos de proveedores y apoyar el ingreso de inventario.

Incluye:

```txt
Factura
Boleta proveedor
Nota
Proveedor
Productos
Cantidad
Precio
Fecha
Total
Confirmación del usuario
Actualización de inventario
Imagen original
Datos OCR
```

### Reglas importantes

```txt
OCR no actualiza inventario automáticamente.
El usuario siempre debe confirmar.
```

### Dependencias

Depende de:

```txt
Proveedores
Productos
Inventario
Auditoría
```

---

## 20. Módulo 18 — WhatsApp

### Responsabilidad

Enviar documentos y mensajes mediante Evolution API.

Incluye:

```txt
Boletas
Notas
PDF
Reportes
Lista de compras
Recordatorio de fiados
Historial de envíos
```

### Dependencias

Depende de:

```txt
Comprobantes
Reportes
Fiados
Configuración
Auditoría
```

---

## 21. Módulo 19 — Respaldos

### Responsabilidad

Generar respaldos automáticos de la tienda.

Incluye:

```txt
Backup diario
ZIP
Base de datos
Archivos documentales
Sincronización futura con Google Drive
```

### Dependencias

Depende de:

```txt
Configuración
Auditoría
```

---

## 22. Dependencias críticas

```txt
Configuración base
    ↓
Usuarios
    ↓
Roles y permisos
    ↓
Proveedores / Clientes / Productos
    ↓
Inventario
    ↓
Caja
    ↓
Emitir Recibo
    ↓
Comprobantes / Fiados
    ↓
Cierre de caja / Reportes
    ↓
Centro de Inteligencia
    ↓
OCR / WhatsApp / Respaldos
```

---

## 23. Regla final

Ningún módulo nuevo debe agregarse sin autorización explícita del propietario del proyecto.

Cada módulo debe diseñarse antes de implementarse.
