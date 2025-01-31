import typer
#import asyncio
from pathlib import Path
from infrastructure.config.settings import get_settings
#from infrastructure.database.supabase_client import get_client
import psycopg2
from urllib.parse import urlparse

app = typer.Typer()

def get_db_connection(settings):
    """Obtiene una conexión directa a la base de datos de Supabase"""
    # Parsear la URL de Supabase para obtener los datos de conexión
    url = urlparse(settings.SUPABASE_URL)
    dbname = url.path.strip('/')
    
    return psycopg2.connect(
        dbname=dbname,
        user='postgres',
        password=settings.SUPABASE_SERVICE_KEY,
        host=url.hostname,
        port=url.port or 5432
    )

def execute_sql(conn, sql: str):
    """Ejecuta SQL usando psycopg2"""
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    except Exception as e:
        conn.rollback()
        typer.echo(f"Error ejecutando SQL: {e}", err=True)
        raise typer.Exit(code=1)

@app.command()
def migrate(version: str = None):
    """Ejecuta las migraciones de la base de datos"""
    settings = get_settings()
    conn = get_db_connection(settings)
    migrations_path = Path("infrastructure/database/migrations")
    
    # Crear tabla de migraciones si no existe
    migration_table_sql = """
    CREATE TABLE IF NOT EXISTS tech_migrations (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    execute_sql(conn, migration_table_sql)
    
    # Obtener migraciones ejecutadas
    with conn.cursor() as cur:
        cur.execute("SELECT name FROM tech_migrations")
        executed_migrations = {row[0] for row in cur.fetchall()}
    
    # Obtener todas las migraciones o una específica
    if version:
        migrations = [migrations_path / f"{version}.sql"]
    else:
        migrations = sorted(migrations_path.glob("*.sql"))
    
    for migration in migrations:
        if migration.name in executed_migrations:
            typer.echo(f"Migración {migration.name} ya ejecutada, saltando...")
            continue
            
        typer.echo(f"Ejecutando migración: {migration.name}")
        try:
            with open(migration) as f:
                sql = f.read()
                execute_sql(conn, sql)
                # Registrar la migración
                execute_sql(conn, 
                    f"INSERT INTO tech_migrations (name) VALUES ('{migration.name}')"
                )
            typer.echo(f"✅ Migración {migration.name} completada")
        except Exception as e:
            typer.echo(f"❌ Error en migración {migration.name}: {str(e)}", err=True)
            raise typer.Exit(code=1)
    
    conn.close()

@app.command()
def seed(environment: str = "development"):
    """Carga datos iniciales en la base de datos"""
    settings = get_settings()
    conn = get_db_connection(settings)
    seeds_path = Path("infrastructure/database/seeds")
    
    # Crear tabla de seeds si no existe
    seed_table_sql = """
    CREATE TABLE IF NOT EXISTS tech_seeds (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        environment TEXT NOT NULL,
        executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    execute_sql(conn, seed_table_sql)
    
    # Ejecutar seeds según el ambiente
    seeds = [
        seeds_path / "initial_prompts.sql",
        seeds_path / f"{environment}_seeds.sql"
    ]
    
    for seed in seeds:
        if not seed.exists():
            typer.echo(f"Archivo seed {seed.name} no encontrado, saltando...")
            continue
            
        # Verificar si ya se ejecutó
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM tech_seeds WHERE name = %s AND environment = %s",
                (seed.name, environment)
            )
            if cur.fetchone():
                typer.echo(f"Seed {seed.name} ya ejecutado en {environment}, saltando...")
                continue
            
        typer.echo(f"Ejecutando seed: {seed.name}")
        try:
            with open(seed) as f:
                sql = f.read()
                execute_sql(conn, sql)
                # Registrar el seed
                execute_sql(conn,
                    "INSERT INTO tech_seeds (name, environment) VALUES (%s, %s)",
                    (seed.name, environment)
                )
            typer.echo(f"✅ Seed {seed.name} completado")
        except Exception as e:
            typer.echo(f"❌ Error en seed {seed.name}: {str(e)}", err=True)
            raise typer.Exit(code=1)
    
    conn.close()

@app.command()
def test():
    """Ejecuta las pruebas"""
    import pytest
    pytest.main(["-v", "tests"])

if __name__ == "__main__":
    app() 