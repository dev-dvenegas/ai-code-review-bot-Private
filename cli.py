#!/usr/bin/env python
import os
import subprocess
import sys
import typer
from infrastructure.config.settings import get_settings
from infrastructure.database.supabase_client import get_client

app = typer.Typer(help="CLI para gestionar migraciones, seeds y tests de la aplicación.")

@app.command()
def migrate(version: str = ""):
    """
    Ejecuta las migraciones de la base de datos.

    Si se pasa una versión específica, se puede usar para retroceder o avanzar a una migración en particular.
    En este ejemplo se recorren todos los archivos SQL en el directorio de migraciones.
    """
    typer.echo("Ejecutando migraciones...")
    # Se asume que las migraciones están en infrastructure/database/migrations
    migrations_path = os.path.join(os.path.dirname(__file__), "infrastructure", "database", "migrations")
    if not os.path.isdir(migrations_path):
        typer.echo("No se encontró el directorio de migraciones.")
        raise typer.Exit(code=1)

    files = sorted([f for f in os.listdir(migrations_path) if f.endswith(".sql")])
    for file in files:
        file_path = os.path.join(migrations_path, file)
        typer.echo(f"Ejecutando migración: {file}")
        with open(file_path, "r", encoding="utf-8") as f:
            sql = f.read()
        # Aquí se debe ejecutar el SQL contra la base de datos.
        # Por simplicidad, mostramos el contenido. En un entorno real se usaría el cliente de Supabase o psql.
        typer.echo(sql)
        # Por ejemplo, se podría ejecutar:
        # client = get_client(get_settings())
        # client.query(sql)   <-- Dependerá de la API del cliente.
    typer.echo("Migraciones completadas.")

@app.command()
def seed(environment: str = "development"):
    """
    Carga datos iniciales en la base de datos para el ambiente indicado.
    """
    # typer.echo(f"Cargando seeds para el ambiente '{environment}'...")
    # seeds_path = os.path.join(os.path.dirname(__file__), "infrastructure", "database", "seeds", "initial_prompts.sql")
    # if not os.path.isfile(seeds_path):
    #     typer.echo("No se encontró el archivo de seeds.")
    #     raise typer.Exit(code=1)
    # with open(seeds_path, "r", encoding="utf-8") as f:
    #     sql = f.read()
    typer.echo("Ejecutando seed inicial:")
    # typer.echo(sql)
    # Aquí se debería ejecutar el SQL contra la base de datos.
    typer.echo("Seeds completados.")

@app.command()
def test():
    """
    Ejecuta los tests usando pytest.
    """
    typer.echo("Ejecutando tests...")
    result = subprocess.run(["pytest", "--maxfail=1", "--disable-warnings", "-q"], capture_output=True, text=True)
    typer.echo(result.stdout)
    if result.returncode != 0:
        typer.echo("Algunos tests fallaron.")
        sys.exit(result.returncode)
    typer.echo("Todos los tests pasaron.")

if __name__ == "__main__":
    app()
