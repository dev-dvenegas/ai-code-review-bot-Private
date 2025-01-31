# AI Pull Request Review Bot

Un bot que analiza Pull Requests usando IA para proporcionar revisiones de código automáticas.

## Características

- Análisis automático de Pull Requests usando GPT-4
- Gestión de prompts y reglas de revisión personalizables
- Integración con GitHub Apps
- Almacenamiento en Supabase
- API RESTful para gestión de prompts y reglas
- CI/CD automatizado con GitHub Actions
- CLI para gestión de migraciones y seeds
- Docker para desarrollo y producción

## Requisitos Previos

- Python 3.11+
- Docker y Docker Compose
- Cuenta en GitHub
- Cuenta en Supabase
- Cuenta en OpenAI

## Configuración Inicial

1. **Crear una GitHub App**:
   - Ve a Settings > Developer settings > GitHub Apps
   - Crea una nueva app
   - Configura los permisos necesarios:
     - Pull requests: Read & Write
     - Checks: Read & Write
     - Contents: Read
   - Guarda el App ID y genera una Private Key

2. **Configurar Supabase**:
   - Crea un proyecto en Supabase
   - Guarda la URL y la Service Key

3. **Variables de Entorno**:
   ```bash
   cp .env.example .env
   ```
   Edita `.env` con tus valores:
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
   ```

## Desarrollo Local

### Usando Docker (Recomendado)

1. **Iniciar servicios**:
   ```bash
   docker-compose up --build
   ```

2. **Ejecutar migraciones**:
   ```bash
   docker-compose exec app python cli.py migrate
   ```

3. **Cargar datos iniciales**:
   ```bash
   docker-compose exec app python cli.py seed development
   ```

### Sin Docker

1. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Ejecutar migraciones**:
   ```bash
   python cli.py migrate
   ```

3. **Iniciar servidor**:
   ```bash
   uvicorn main:app --reload
   ```

## CLI

El proyecto incluye un CLI para tareas comunes:

```bash
# Ver comandos disponibles
python cli.py --help

# Ejecutar migraciones
python cli.py migrate [--version VERSION]

# Cargar datos iniciales
python cli.py seed [development|staging|production]

# Ejecutar tests
python cli.py test
```

## API Endpoints

### Documentación

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Prompts

#### Crear Prompt
```http
POST /api/v1/prompts
Content-Type: application/json

{
    "name": "code_review_prompt",
    "version": "1.0.0",
    "prompt_text": "texto del prompt...",
    "metadata": {}
}
```

### Reglas

#### Crear Regla
```http
POST /api/v1/rules
Content-Type: application/json

{
    "name": "naming_convention",
    "rule_type": "style",
    "rule_content": "Use snake_case...",
    "priority": 1
}
```

### Webhook GitHub

```http
POST /webhook/github
X-GitHub-Event: pull_request
X-Hub-Signature-256: sha256=...
```

## CI/CD

El proyecto utiliza GitHub Actions para automatización:

### CI (Integración Continua)
- Ejecuta en push a main/develop y pull requests
- Ejecuta tests con cobertura
- Verifica estilo de código (ruff, black)
- Verifica tipos (mypy)
- Usa Supabase local para tests

### CD (Despliegue Continuo)
- Ejecuta en push a main y tags
- Construye y publica imagen Docker
- Despliega automáticamente en producción

### Configuración de Secrets

En GitHub, configura los siguientes secrets:
```bash
# Docker Hub
DOCKERHUB_USERNAME=usuario
DOCKERHUB_TOKEN=token

# Servidor de Producción
SSH_HOST=ip_servidor
SSH_USERNAME=usuario
SSH_PRIVATE_KEY=llave_ssh
```

## Estructura del Proyecto

```
.
├── application/          # Casos de uso y DTOs
├── domain/              # Modelos y lógica de dominio
├── infrastructure/      # Implementaciones técnicas
│   ├── ai/             # Integración con LangChain
│   ├── database/       # Repositorios y migraciones
│   └── github/         # Servicios de GitHub
├── interfaces/         # API y controladores
├── tests/             # Tests
├── .github/           # Workflows de GitHub Actions
├── docker-compose.yml # Configuración de Docker
└── cli.py            # CLI de la aplicación
```

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

# Ver logs de base de datos
docker-compose logs -f db
```

### Endpoints de Monitoreo
- Health Check: `GET /health`
- Métricas: `GET /metrics` (si está configurado)

## Contribuir

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Base de Datos

Las tablas del sistema usan el prefijo `tech_` para diferenciarlas de otras aplicaciones:

- `tech_prs`: Pull requests a revisar
- `tech_reviews`: Revisiones técnicas realizadas
- `tech_review_comments`: Comentarios de las revisiones
- `tech_analysis_prompts`: Prompts para el análisis
- `tech_analysis_rules`: Reglas de análisis técnico

