#!/bin/bash
# Script de entrada para el contenedor Docker
# Se encarga de inicializar la base de datos y la aplicación

# Activar modo de error estricto
set -e

# Esperar a que Supabase esté disponible antes de continuar
# Esto es importante en entornos Docker donde los servicios pueden iniciar en diferente orden
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  >&2 echo "Postgres no está disponible - esperando..."
  sleep 1
done

echo "Postgres está listo - ejecutando migraciones"

# Ejecutar migraciones de la base de datos
if ! python cli.py migrate; then
    >&2 echo "Error ejecutando migraciones"
    exit 1
fi

# Ejecutar seeds si estamos en ambiente de desarrollo
if [ "$ENVIRONMENT" = "development" ]; then
    if ! python cli.py seed development; then
        >&2 echo "Error ejecutando seeds"
        exit 1
    fi
fi

# Ejecutar el comando proporcionado (normalmente uvicorn)
exec "$@" 