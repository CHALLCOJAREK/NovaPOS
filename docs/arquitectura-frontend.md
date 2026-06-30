# NovaPOS — Arquitectura Frontend

## 1. Objetivo

Definir la arquitectura oficial del frontend de NovaPOS para garantizar una interfaz consistente, escalable, mantenible y orientada a una experiencia de usuario rápida e intuitiva.

La arquitectura debe permitir agregar nuevos módulos sin afectar los existentes.

---

# 2. Tecnologías oficiales

El frontend utilizará exclusivamente:

```txt
React
Vite
TypeScript
Tailwind CSS
React Router
TanStack Query
Zustand
React Hook Form
Zod
Axios
Lucide React
```

No se utilizarán:

```txt
Bootstrap
Material UI
Modo Oscuro
```

---

# 3. Arquitectura general

```txt
Usuario
    │
    ▼
Página (Page)
    │
    ▼
Feature
    │
    ▼
Componentes
    │
    ▼
Hooks
    │
    ▼
Services
    │
    ▼
API Backend
```

Cada capa tiene una única responsabilidad.

---

# 4. Estructura oficial

```txt
frontend/
│
├── public/
│
├── src/
│   │
│   ├── app/
│   ├── assets/
│   ├── components/
│   ├── config/
│   ├── features/
│   ├── hooks/
│   ├── layouts/
│   ├── pages/
│   ├── routes/
│   ├── services/
│   ├── stores/
│   ├── types/
│   ├── utils/
│   │
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
│
└── package.json
```

---

# 5. Responsabilidad de cada carpeta

## app

Configuración principal del frontend.

Ejemplos:

```txt
queryClient.ts
providers.tsx
theme.ts
```

---

## assets

Archivos estáticos.

```txt
logos
íconos
imágenes
fuentes
```

---

## components

Componentes reutilizables.

Ejemplos:

```txt
Button.tsx
Input.tsx
Modal.tsx
Card.tsx
DataTable.tsx
SearchInput.tsx
```

No contienen lógica de negocio.

---

## config

Configuraciones generales.

Ejemplos:

```txt
api.ts
constants.ts
permissions.ts
environment.ts
```

---

## features

Cada módulo funcional del sistema.

Ejemplo:

```txt
auth/
products/
customers/
sales/
inventory/
cash/
reports/
settings/
```

Dentro de cada feature:

```txt
components/
hooks/
services/
types/
```

Toda la lógica específica del módulo vive aquí.

---

## hooks

Hooks reutilizables.

Ejemplos:

```txt
useDebounce.ts
usePagination.ts
useLocalStorage.ts
useScanner.ts
```

---

## layouts

Layouts generales.

Ejemplos:

```txt
MainLayout.tsx
AuthLayout.tsx
```

El layout principal contendrá:

```txt
Sidebar
Navbar
Contenido
```

---

## pages

Pantallas completas.

Ejemplos:

```txt
DashboardPage.tsx
SalesPage.tsx
ProductsPage.tsx
CustomersPage.tsx
```

Las páginas solo organizan componentes.

No contienen lógica de negocio.

---

## routes

Configuración del enrutamiento.

Ejemplo:

```txt
index.tsx
privateRoutes.tsx
publicRoutes.tsx
```

---

## services

Comunicación con el backend.

Ejemplos:

```txt
productService.ts
saleService.ts
authService.ts
```

Aquí solo existen llamadas HTTP.

---

## stores

Estado global usando Zustand.

Ejemplos:

```txt
authStore.ts
cartStore.ts
settingsStore.ts
```

Solo información compartida.

---

## types

Interfaces y tipos TypeScript.

Ejemplos:

```txt
Product.ts
Sale.ts
Customer.ts
Receipt.ts
```

---

## utils

Funciones reutilizables.

Ejemplos:

```txt
currency.ts
date.ts
validators.ts
printer.ts
```

---

# 6. Componentes reutilizables

NovaPOS tendrá un catálogo único de componentes.

Ejemplos:

```txt
Button
Input
Select
Checkbox
Radio
Card
Badge
Modal
Table
SearchInput
EmptyState
Loading
ConfirmDialog
```

No se crearán versiones distintas del mismo componente.

---

# 7. Diseño visual

El sistema utilizará un único diseño.

Características:

```txt
Fondo blanco

Mucho espacio

Bordes suaves

Sombras ligeras

Botones grandes

Tipografía limpia

Íconos Lucide

Sin degradados exagerados

Sin animaciones innecesarias
```

---

# 8. Responsive

Todo el sistema será compatible con:

```txt
PC

Tablet

Celular
```

El orden de diseño será:

```txt
Desktop First
```

---

# 9. Navegación

La navegación principal utilizará Sidebar.

```txt
Dashboard

Emitir Recibo

Inventario

Clientes

Fiados

Proveedores

Caja

Reportes

Centro de Inteligencia

Usuarios

Configuración
```

---

# 10. Estado global

Solo se almacenará en Zustand información compartida.

Ejemplos:

```txt
Usuario autenticado

Configuración

Carrito de venta

Caja activa

Tienda activa
```

No almacenar información temporal innecesaria.

---

# 11. Datos remotos

Toda consulta al backend utilizará TanStack Query.

Beneficios:

```txt
Cache

Reintentos

Invalidación

Refetch

Optimización
```

Nunca realizar llamadas directas con Axios desde componentes.

---

# 12. Formularios

Todos los formularios utilizarán:

```txt
React Hook Form

+

Zod
```

Validación siempre en frontend y backend.

---

# 13. Pantalla principal

La pantalla principal será:

```txt
Emitir Recibo
```

Objetivo:

Emitir una venta en menos de 30 segundos.

---

# 14. Flujo de venta

```txt
Buscar producto

↓

Agregar productos

↓

Seleccionar cliente (opcional)

↓

Seleccionar comprobante

↓

Seleccionar pago

↓

Checks opcionales

↓

Emitir Recibo
```

Todo en una sola pantalla.

---

# 15. Acciones mediante checks

No existirán botones independientes para acciones secundarias.

Ejemplos:

```txt
Enviar por WhatsApp

Guardar PDF

Guardar Imagen

Registrar Cliente

Registrar Fiado
```

Todas serán opciones seleccionables mediante checks.

---

# 16. Escáner

El lector USB funcionará como teclado.

No se desarrollará integración especial.

En dispositivos móviles se utilizará ZXing.

---

# 17. Rendimiento

El frontend debe priorizar:

```txt
Pocas renderizaciones

Componentes reutilizables

Carga diferida cuando sea necesario

Consultas cacheadas

Respuestas rápidas
```

---

# 18. Nomenclatura

Componentes:

```txt
PascalCase
```

Ejemplos:

```txt
ProductCard.tsx

CustomerModal.tsx

CashSummary.tsx
```

Hooks:

```txt
useProducts.ts

useSales.ts
```

Stores:

```txt
authStore.ts

cartStore.ts
```

---

# 19. Filosofía UX

Todo debe poder aprenderse en menos de una hora.

El usuario nunca debe preguntarse:

> "¿Dónde está esta opción?"

La interfaz debe guiar naturalmente el flujo de trabajo.

---

# 20. Regla final

Las páginas organizan.

Los componentes muestran.

Los hooks reutilizan lógica.

Los services hablan con el backend.

Los stores comparten estado.

Ninguna capa debe asumir responsabilidades de otra.
