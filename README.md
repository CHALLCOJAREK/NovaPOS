# NovaPOS

> Sistema Profesional de Punto de Venta (POS), Inventario y Gestión Comercial.

---

# Descripción

**NovaPOS** es un sistema web profesional de Punto de Venta (POS), Inventario y Gestión Comercial desarrollado inicialmente para la **Tienda de Abarrotes Danae**, pero diseñado desde el primer día para evolucionar hacia una plataforma comercial escalable para múltiples negocios.

El proyecto busca ofrecer una solución moderna, rápida e intuitiva para la administración de tiendas, integrando ventas, inventario, clientes, proveedores, caja, reportes, OCR, WhatsApp y un Centro de Inteligencia para apoyar la toma de decisiones.

Su arquitectura fue diseñada para ser mantenible, modular y preparada para crecer desde una instalación local (LAN/WiFi) hasta una futura versión multiempresa basada en PostgreSQL, sin necesidad de rehacer la lógica del sistema.

---

# Objetivos

* Desarrollar un software comercial profesional.
* Ofrecer una experiencia de usuario simple y rápida.
* Mantener una arquitectura limpia y escalable.
* Facilitar el mantenimiento y futuras ampliaciones.
* Garantizar la integridad de la información.
* Preparar el sistema para una futura arquitectura multiempresa.

---

# Funcionalidades principales

* Punto de Venta (POS)
* Inventario
* Clientes
* Proveedores
* Caja
* Cierre de Caja
* Comprobantes
* Fiados
* Reportes
* Productos por Comprar
* Productos Próximos a Vencer
* Centro de Inteligencia
* OCR para documentos
* Integración con WhatsApp
* Respaldos automáticos
* Gestión de usuarios y permisos

---

# Tecnologías

## Frontend

* React
* Vite
* TypeScript
* Tailwind CSS
* React Router
* TanStack Query
* Zustand
* React Hook Form
* Zod
* Axios
* Lucide React

## Backend

* Python
* FastAPI
* SQLAlchemy 2.0
* Alembic
* Pydantic
* SQLite
* PostgreSQL (Futuro)

---

# Arquitectura

NovaPOS utiliza una arquitectura en capas para separar responsabilidades y facilitar el mantenimiento.

```text
Frontend (React)

        │

        ▼

Routers (FastAPI)

        │

        ▼

Services

        │

        ▼

Repositories

        │

        ▼

Models (SQLAlchemy)

        │

        ▼

SQLite
```

Esta arquitectura permite migrar posteriormente a PostgreSQL sin modificar la lógica del negocio.

---

# Estructura del proyecto

```text
NovaPOS/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── db/
│   │   ├── middlewares/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│
├── data/
│   └── Danae/
│
├── docs/
│
└── scripts/
```

---

# Estado del proyecto

**Fase actual:** Arquitectura y Preparación del Proyecto.

Completado:

* Arquitectura general.
* Configuración inicial del backend.
* Configuración inicial del frontend.
* Convenciones técnicas.
* Arquitectura Backend.
* Arquitectura Frontend.
* Definición de módulos.
* Modelo inicial de base de datos.
* Preparación del entorno de desarrollo.

En desarrollo:

* Módulo de Configuración Base del Sistema.

---

# Principios del proyecto

* Arquitectura limpia.
* Separación por capas.
* Desarrollo guiado por documentación.
* Diseño antes de implementación.
* Escalabilidad desde el primer día.
* Código limpio y mantenible.
* Experiencia de usuario intuitiva.
* Sin duplicación de lógica.
* Auditoría de operaciones.
* Soft Delete para preservar la información.

---

# Flujo de desarrollo

Cada módulo seguirá el mismo proceso de trabajo:

1. Objetivo del módulo.
2. Flujo funcional.
3. Casos de uso.
4. Modelo de datos.
5. Relaciones.
6. API REST.
7. Validaciones.
8. Diseño UI.
9. Componentes React.
10. Servicios Backend.
11. Casos de error.
12. Implementación Backend.
13. Implementación Frontend.
14. Integración.
15. Pruebas.

Ningún módulo se implementará sin haber sido diseñado previamente.

---

# Documentación

Toda la documentación técnica del proyecto se encuentra dentro de la carpeta:

```text
docs/
```

Incluye:

* Documento Maestro.
* Convenciones Técnicas.
* Arquitectura Backend.
* Arquitectura Frontend.
* Módulos del Sistema.
* Modelo Base de Datos.
* API REST (en desarrollo).
* Reglas de Negocio (por módulo).
* Navegación de Pantallas (por módulo).

---

# Licencia

Este proyecto es de carácter privado y propietario.

Todos los derechos reservados.

No está permitida la copia, distribución, modificación o utilización parcial o total del código fuente sin la autorización expresa del propietario del proyecto.

---

# Autor

**Jarek Angelo Challco Juarez**

Consultor de Inteligencia Artificial, Automatización y Desarrollo de Software.

NovaPOS representa la evolución de una necesidad real hacia un producto comercial profesional, construido con un enfoque de arquitectura sólida, escalabilidad y calidad desde su concepción.
