# NovaPOS — Arquitectura Frontend

# 1. Objetivo

Definir la arquitectura oficial del frontend de NovaPOS para garantizar una interfaz moderna, escalable, mantenible y preparada para crecer desde una única tienda hasta una plataforma comercial multiempresa.

La arquitectura debe facilitar el desarrollo de nuevos módulos sin afectar los existentes, manteniendo una experiencia de usuario rápida, intuitiva y consistente.

---

# 2. Tecnologías oficiales

El frontend utilizará exclusivamente:

```txt
Angular
TypeScript
Angular Router
Reactive Forms
HttpClient
RxJS
Tailwind CSS
Angular CLI
Standalone Components
```

# 3. Arquitectura general

```txt
Usuario
    │
    ▼
Página
    │
    ▼
Layout
    │
    ▼
Feature (Módulo)
    │
    ▼
Componentes
    │
    ▼
Services
    │
    ▼
HttpClient
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
│   │   ├── core/
│   │   ├── features/
│   │   ├── layouts/
│   │   ├── shared/
│   │   ├── app.config.ts
│   │   ├── app.routes.ts
│   │   └── app.ts
│   │
│   ├── assets/
│   │
│   ├── environments/
│   │
│   ├── styles.css
│   └── main.ts
│
├── angular.json
├── package.json
├── tsconfig.json
└── tailwind.config.js
```

---

# 5. Responsabilidad de cada carpeta

## app

Contiene toda la aplicación Angular.

Aquí viven:

```txt
Configuración

Rutas

Layouts

Módulos

Componentes

Servicios
```

---

## core

Contiene funcionalidades globales del sistema.

Ejemplos:

```txt
authentication

guards

interceptors

services

models

constants

tokens
```

Todo lo que se comparte entre módulos vive aquí.

---

## features

Cada módulo funcional del sistema.

Ejemplos:

```txt
auth

dashboard

sales

inventory

products

customers

suppliers

cash

reports

intelligence

users

settings
```

Cada Feature contiene únicamente la lógica relacionada con su módulo.

---

## layouts

Layouts generales de la aplicación.

Ejemplos:

```txt
AuthLayout

MainLayout
```

MainLayout contendrá:

```txt
Sidebar

Header

Contenido principal
```

---

## shared

Componentes reutilizables.

Ejemplos:

```txt
components

directives

pipes

validators

models

interfaces
```

No contiene lógica de negocio.

---

## assets

Archivos estáticos.

```txt
logos

iconos

imagenes

fuentes
```

---

## environments

Configuraciones por ambiente.

Ejemplos:

```txt
environment.ts

environment.development.ts
```

---

# 6. Organización interna de cada Feature

Cada módulo seguirá la siguiente estructura:

```txt
feature/
│
├── components/
├── pages/
├── services/
├── models/
├── interfaces/
├── guards/
├── resolvers/
└── routes.ts
```

Cada módulo será independiente del resto.

---

# 7. Comunicación con el Backend

Toda comunicación utilizará:

```txt
HttpClient
```

Los componentes nunca consumirán la API directamente.

El flujo será:

```txt
Component

↓

Service

↓

HttpClient

↓

Backend
```

---

# 8. Estado de la aplicación

NovaPOS utilizará principalmente:

```txt
Signals (cuando sea necesario)

RxJS

Servicios Singleton
```

El objetivo es mantener un estado simple, predecible y fácil de mantener.

---

# 9. Formularios

Todos los formularios utilizarán:

```txt
Reactive Forms
```

Las validaciones existirán tanto en:

```txt
Frontend

Backend
```

Nunca depender únicamente del frontend.

---

# 10. Componentes reutilizables

NovaPOS tendrá un único catálogo oficial de componentes.

Ejemplos:

```txt
Button

Input

Select

Checkbox

Radio

Modal

Table

Card

Badge

SearchBox

Pagination

Loading

EmptyState

ConfirmDialog
```

Nunca crear variantes innecesarias.

---

# 11. Diseño visual

El diseño oficial será:

```txt
Minimalista

Profesional

Corporativo

Mucho espacio visual

Fondo blanco

Bordes suaves

Sombras ligeras

Tipografía limpia

Botones grandes

Sin degradados exagerados

Sin modo oscuro
```

---

# 12. Responsive

Compatible con:

```txt
PC

Tablet

Celular
```

La prioridad será:

```txt
Desktop First
```

---

# 13. Navegación

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

# 14. Rutas

Las rutas estarán centralizadas en:

```txt
app.routes.ts
```

Se utilizarán:

```txt
Lazy Loading

Route Guards

CanActivate

CanMatch
```

Las rutas privadas requerirán autenticación mediante JWT.

---

# 15. Seguridad

El frontend implementará:

```txt
JWT

Auth Guard

HTTP Interceptor

Manejo automático de Token

Redirección al Login

Control básico de permisos
```

Toda validación crítica permanecerá en el backend.

---

# 16. Pantalla principal

La pantalla principal del sistema será:

```txt
Emitir Recibo
```

Objetivo:

Emitir una venta en menos de 30 segundos.

---

# 17. Flujo de venta

```txt
Buscar producto

↓

Agregar productos

↓

Seleccionar cliente (opcional)

↓

Seleccionar comprobante

↓

Seleccionar método de pago

↓

Seleccionar opciones adicionales

↓

Emitir Recibo
```

Todo el proceso debe realizarse desde una única pantalla.

---

# 18. Acciones mediante opciones

Las acciones secundarias estarán disponibles mediante checks o interruptores.

Ejemplos:

```txt
Enviar por WhatsApp

Guardar PDF

Guardar Imagen

Registrar Cliente

Venta Fiada
```

No crear botones independientes para estas acciones.

---

# 19. Escáner

El lector USB funcionará como teclado.

No se desarrollará integración especial.

Para dispositivos móviles se evaluará ZXing cuando sea necesario.

---

# 20. Rendimiento

El frontend priorizará:

```txt
Lazy Loading

Standalone Components

Componentes reutilizables

Carga rápida

Consultas optimizadas

RxJS eficiente

Mínimas renderizaciones
```

---

# 21. Nomenclatura

Componentes

```txt
PascalCase
```

Ejemplos:

```txt
ProductCardComponent

CustomerModalComponent

SidebarComponent
```

Servicios

```txt
camelCase + Service
```

Ejemplos:

```txt
product.service.ts

sale.service.ts

auth.service.ts
```

Modelos

```txt
PascalCase
```

Ejemplos:

```txt
Product

Customer

Sale

Receipt
```

---

# 22. Filosofía UX

Todo debe poder aprenderse en menos de una hora.

El usuario nunca debe preguntarse:

> "¿Dónde está esta opción?"

La interfaz debe guiar naturalmente el flujo de trabajo, reduciendo clics y priorizando la velocidad en la operación diaria.

---

# 23. Regla final

Las páginas organizan.

Los layouts estructuran.

Los componentes muestran información.

Los servicios gestionan la comunicación con el backend.

Reactive Forms administra los formularios.

RxJS controla los flujos de datos.

Ninguna capa debe asumir responsabilidades que pertenecen a otra.