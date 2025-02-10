# AI Pull Request Review Bot

Un bot que analiza Pull Requests usando IA para proporcionar revisiones de código automáticas y sugerencias de mejora.

## Características Principales

- **Análisis Automático de PRs:**
  - Revisión de código usando GPT-4
  - Detección de problemas de seguridad y rendimiento
  - Sugerencias de código específicas por línea
  - Análisis de complejidad y calidad
  - Resumen general con puntuación

- **Gestión de Reglas:**
  - Prompts personalizables
  - Reglas de revisión configurables
  - Priorización de reglas
  - Templates para títulos y descripciones

- **Integración con GitHub:**
  - Webhooks automáticos
  - Comentarios en línea con sugerencias de código
  - Resumen general con problemas de seguridad y rendimiento
  - Etiquetas automáticas

- **Infraestructura:**
  - Base de datos Supabase
  - Contenedor de dependencias
  - API RESTful
  - CLI para administración

- **Integración con LangChain:**
  - Procesamiento de prompts personalizables
  - Parseo estructurado de respuestas
  - Cadenas de procesamiento configurables
  - Integración con múltiples modelos de IA

## Arquitectura

### Capas (DDD)

1. **Domain:**
   - Modelos de negocio (PullRequest, Review, etc.)
   - Excepciones de dominio
   - Interfaces de repositorios

2. **Application:**
   - Casos de uso
   - DTOs para transferencia de datos
   - Transformadores y helpers

3. **Infrastructure:**
   - Implementaciones de repositorios
   - Servicios externos (GitHub, OpenAI)
   - Configuración y contenedor DI
   - Cliente Supabase

4. **Interfaces:**
   - Controllers API
   - CLI
   - Webhooks

## Requisitos Previos

- Python 3.11+
- Docker y Docker Compose
- Cuenta en GitHub
- Cuenta en Supabase
- Cuenta en OpenAI

## Configuración Inicial

### 1. GitHub App

1. Ve a Settings > Developer settings > GitHub Apps
2. Crea una nueva app con los siguientes permisos:
   ```
   Repository permissions:
   - Pull requests: Read & Write
   - Checks: Read & Write
   - Contents: Read
   - Metadata: Read
   
   Subscribe to events:
   - Pull request
   - Pull request review
   ```
3. Guarda el App ID y genera una, Private Key

### 2. Supabase

1. Crea un nuevo proyecto
2. Guarda la URL y Service Key
3. Las tablas se crearán automáticamente con las migraciones

### 3. Variables de Entorno

```bash
cp .env.example .env
```

Configura las siguientes variables:

```env
# GitHub App
GITHUB_APP_ID=tu_app_id
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
GITHUB_WEBHOOK_SECRET=tu_webhook_secret

# OpenAI
OPENAI_API_KEY=tu_api_key

# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_KEY=tu_service_key

# Configuración App
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## Instalación y Desarrollo

### Usando Docker (Recomendado)

```bash
# Asegúrate de tener el archivo .env configurado con las variables necesarias:
GITHUB_APP_ID=tu_app_id
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
GITHUB_WEBHOOK_SECRET=tu_webhook_secret
OPENAI_API_KEY=tu_api_key
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_KEY=tu_service_key

# Construir e iniciar el servicio
docker-compose up --build
```

La aplicación estará disponible en:
- API: http://localhost:8000
- Documentación: http://localhost:8000/docs

### Estructura del Docker

El proyecto utiliza:
- `Dockerfile`: Imagen base Python 3.11 con las dependencias mínimas necesarias
- `docker-compose.yml`: Configura el servicio de la API y maneja las variables de entorno
- Hot-reload activado para desarrollo

### Notas Importantes
- La aplicación se conecta directamente a una instancia existente de Supabase
- No es necesario ejecutar migraciones ni seeds
- Las tablas y estructura de datos deben existir previamente en Supabase

### Desarrollo Local

```bash
# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Iniciar servidor
uvicorn main:app --reload
```

## API Endpoints

### Documentación
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Webhooks
```http
POST /webhook/github
X-GitHub-Event: pull_request
X-Hub-Signature-256: sha256=...

{
  "action": "opened",
  "pull_request": {
    "number": 123,
    ...
  }
}
```

### Prompts y Reglas
```http
# Crear prompt
POST /api/v1/prompts
Content-Type: application/json

{
    "name": "code_review",
    "version": "1.0.0",
    "prompt_text": "Analiza el siguiente código...",
    "metadata": {
        "language": "python",
        "type": "security"
    }
}

# Crear regla
POST /api/v1/rules
Content-Type: application/json

{
    "name": "naming_convention",
    "rule_type": "style",
    "rule_content": "Use snake_case for variables",
    "priority": 1
}
```

## Integración con LangChain

### Componentes Principales

- **LangchainOrchestrator:**
  - Coordina el proceso de análisis de código
  - Gestiona la comunicación con el modelo de IA
  - Procesa y estructura las respuestas

- **Template Processor:**
  - Combina el prompt base con las reglas de análisis
  - Inserta el contexto del PR y el código a analizar
  - Formatea las instrucciones para el modelo

- **Output Parser:**
  - Convierte las respuestas del modelo en estructuras de datos
  - Valida el formato de las respuestas
  - Maneja errores de parseo

### Flujo de Procesamiento

1. **Preparación:**
   ```bash
   orchestrator = LangchainOrchestrator(openai_api_key=settings.OPENAI_API_KEY)
   ```

2. **Análisis:**
   ```bash
   result = await orchestrator.analyze_code(
       code=pr.diff,
       context=pr.to_dict(),
       rules=active_rules
   )
   ```

3. **Resultado:**
   - El resultado se estructura en un objeto `AIAnalysisResult`
   - Incluye comentarios, sugerencias y metadatos
   - Se utiliza para actualizar el PR en GitHub

### Configuración de Prompts

Los prompts se pueden personalizar y almacenar en la base de datos:

```bash
prompt_template = """
Analiza el siguiente código teniendo en cuenta:
{rules}

CÓDIGO:
{code}

CONTEXTO:
{context}

Genera un análisis estructurado siguiendo este formato:
{format_instructions}
"""
```

### Diagrama de Flujo LangChain

El siguiente diagrama muestra cómo se procesa un análisis usando LangChain:

[Ver diagrama de flujo LangChain](diagrams/langchain_flow.mmd)

## CLI

```bash
# Ver comandos disponibles
python cli.py --help

# Migraciones
python cli.py migrate [--version VERSION]
python cli.py migrate:status
python cli.py migrate:rollback

# Datos semilla
python cli.py seed [development|staging|production]

# Tests
python cli.py test
python cli.py test:coverage
```

## Estructura de Archivos

```
.
├── application/
│   ├── dto/                 # Data Transfer Objects
│   ├── helpers/            # Funciones auxiliares
│   └── use_cases/         # Casos de uso
├── domain/
│   ├── exceptions.py      # Excepciones de dominio
│   └── models/            # Modelos de dominio
├── infrastructure/
│   ├── ai/               # Servicios de IA
│   ├── config/          # Configuración
│   ├── database/        # Acceso a datos
│   └── github/          # Servicios de GitHub
├── interfaces/
│   ├── api/            # Controladores API
│   └── cli/           # Comandos CLI
├── tests/             # Tests
├── diagrams/          # Diagramas Mermaid
├── .env.example      # Template variables de entorno
├── docker-compose.yml
└── README.md
```

## Base de Datos

### Tablas

- **tech_prs:**
  - Almacena información de Pull Requests
  - Campos: id, github_id, number, title, body, status, etc.

- **tech_reviews:**
  - Almacena revisiones de código
  - Campos: id, pull_request_id, status, summary, score, etc.

- **tech_review_comments:**
  - Comentarios específicos de las revisiones
  - Campos: id, review_id, file_path, line_number, content, etc.

- **tech_analysis_prompts:**
  - Prompts para el análisis de código
  - Campos: id, name, version, prompt_text, is_active, etc.

- **tech_analysis_rules:**
  - Reglas de análisis técnico
  - Campos: id, name, rule_type, rule_content, priority, etc.

- **tech_pr_title_guidelines:**
  - Guías para títulos de Pull Requests
  - Campos: id, prefix, description, is_active, min_length, max_length
  - Ejemplo: prefijos como "feat:", "fix:", "docs:", etc.

- **tech_pr_description_templates:**
  - Plantillas para descripciones de Pull Requests
  - Campos: id, name, template_content, is_active
  - Define la estructura esperada para las descripciones de PR

- **tech_pr_labels:**
  - Etiquetas disponibles para Pull Requests
  - Campos: id, name, description, color, is_active
  - Etiquetas como "breaking-change", "bug-fix", "enhancement", etc.

### Índices

- `idx_title_guidelines_active`: Optimiza búsqueda de guías de título activas
- `idx_description_templates_active`: Optimiza búsqueda de plantillas activas
- `idx_pr_labels_active`: Optimiza búsqueda de etiquetas activas

## Diagramas

- [Diagrama de Dependencias](diagrams/dependencies.mmd)
- [Diagrama de Arquitectura DDD](diagrams/architecture.mmd)
- [Diagrama de Flujo de Datos](diagrams/data_flow.mmd)
- [Diagrama de Flujo de Usuario](diagrams/user_flow.mmd)
- [Diagrama de Casos de Uso](diagrams/use_cases.mmd)
- [Diagrama de Flujo LangChain](diagrams/langchain_flow.mmd)

## Tests

```bash
# Ejecutar todos los tests
python -m pytest

# Con cobertura
python -m pytest --cov=. --cov-report=html

# Tests específicos
python -m pytest tests/test_webhook.py
```

## Monitoreo

### Logs
```bash
# Ver logs en tiempo real
docker-compose logs -f app

# Ver logs específicos
docker-compose logs -f app | grep ERROR
```

### Endpoints de Monitoreo
- Health Check: `GET /health`
- Métricas: `GET /metrics`

## Contribución

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

### Guías de Contribución

- Sigue el estilo de código existente
- Añade tests para nueva funcionalidad
- Actualiza la documentación
- Verifica que los tests pasen
- Usa mensajes de commit descriptivos

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE] para más detalles.

## Contacto

Nombre - [@twitter_handle](https://twitter.com/twitter_handle)
Email - email@example.com
Project Link: [https://github.com/username/repo](https://github.com/username/repo)

## Estructura del Proyecto

### Domain
- **Modelos:**
  - Review (con security_concerns y performance_issues)
  - PullRequest
  - ReviewComment
- Excepciones de dominio
- Interfaces de repositorios

### Application
- **DTOs:**
  - CodeAnalysisResult
  - PRMetadataResult
  - AIAnalysisResult
- Casos de uso
- Transformadores y helpers

## Flujo de Análisis

1. Recepción de webhook de GitHub
2. Análisis del código usando LangChain:
   - Análisis de código y problemas
   - Generación de metadata
3. Generación de resultados:
   - Resumen general con puntuación
   - Lista de problemas de seguridad
   - Lista de problemas de rendimiento
   - Comentarios específicos por línea con sugerencias
4. Publicación en GitHub:
   - Comentario general con resumen, score y problemas
   - Comentarios en línea con sugerencias de código

## Integración con GitHub

El bot crea dos tipos de comentarios en los Pull Requests:

1. **Comentario General:**
   ```markdown
   # Pull Request Analysis

   ## Summary
   [Resumen del análisis]

   ## Score: XX/100

   ## Security Concerns
   - [Lista de problemas de seguridad]

   ## Performance Issues
   - [Lista de problemas de rendimiento]
   ```

2. **Comentarios en Línea:**
   ```markdown
   [TIPO - severidad] Explicación del problema

   ```suggestion
   Código sugerido para corregir el problema
   ```
   ```

