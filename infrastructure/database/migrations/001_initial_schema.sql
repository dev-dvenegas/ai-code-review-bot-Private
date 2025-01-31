-- Este archivo define la estructura inicial de la base de datos
-- Usamos el prefijo 'tech_' para diferenciar nuestras tablas de otras aplicaciones en Supabase

-- Tabla para almacenar los Pull Requests que vamos a analizar
create table if not exists tech_prs (
    id bigint primary key generated always as identity,  -- ID auto-incremental
    github_id bigint unique not null,                    -- ID único de GitHub
    number integer not null,                             -- Número del PR en GitHub
    title text not null,                                 -- Título del PR
    body text,                                          -- Descripción del PR
    status text not null,                               -- Estado del PR (open, closed, etc)
    author text not null,                               -- Autor del PR
    repository text not null,                           -- Repositorio del PR
    base_branch text not null,                          -- Rama destino
    head_branch text not null,                          -- Rama origen
    created_at timestamp with time zone not null,       -- Fecha de creación
    updated_at timestamp with time zone not null,       -- Fecha de última actualización
    labels jsonb default '[]'::jsonb                    -- Labels del PR en formato JSON
);

-- Tabla para almacenar las revisiones realizadas por la IA
create table if not exists tech_reviews (
    id bigint primary key generated always as identity,
    pull_request_id bigint references tech_prs(id),     -- Referencia al PR
    status text not null,                               -- Estado de la revisión
    summary text not null,                              -- Resumen de la revisión
    score float not null,                               -- Puntuación de la revisión
    created_at timestamp with time zone default now(),  -- Fecha de creación
    suggested_title text,                               -- Sugerencia de título
    suggested_labels jsonb default '[]'::jsonb          -- Sugerencia de labels
);

-- Tabla para almacenar los comentarios específicos de cada revisión
create table if not exists tech_review_comments (
    id bigint primary key generated always as identity,
    review_id bigint references tech_reviews(id),       -- Referencia a la revisión
    file_path text not null,                           -- Archivo comentado
    line_number integer not null,                      -- Línea del comentario
    content text not null,                             -- Contenido del comentario
    suggestion text                                    -- Sugerencia de código
);

-- Tabla para almacenar los prompts que usa la IA para analizar
create table if not exists tech_analysis_prompts (
    id uuid primary key default gen_random_uuid(),
    name text not null,                                -- Nombre del prompt
    version text not null,                            -- Versión del prompt
    prompt_text text not null,                        -- Texto del prompt
    is_active boolean default true,                   -- Si está activo
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now(),
    metadata jsonb default '{}'::jsonb,               -- Metadata adicional
    constraint unique_prompt_version unique (name, version)  -- No duplicar versiones
);

-- Tabla para almacenar las reglas de análisis
create table if not exists tech_analysis_rules (
    id uuid primary key default gen_random_uuid(),
    name text not null,                               -- Nombre de la regla
    description text,                                 -- Descripción
    rule_type text not null,                         -- Tipo (style, security, etc)
    rule_content text not null,                      -- Contenido de la regla
    priority integer default 1,                      -- Prioridad de aplicación
    is_active boolean default true,                  -- Si está activa
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now(),
    metadata jsonb default '{}'::jsonb                -- Metadata adicional
);

-- Índices para optimizar las consultas más comunes
create index if not exists idx_tech_prs_github_id on tech_prs(github_id);
create index if not exists idx_tech_reviews_pr_id on tech_reviews(pull_request_id);
create index if not exists idx_tech_review_comments_review_id on tech_review_comments(review_id);
create index if not exists idx_tech_prompts_name_version on tech_analysis_prompts(name, version);
create index if not exists idx_tech_prompts_active on tech_analysis_prompts(is_active) where is_active = true;
create index if not exists idx_tech_rules_type on tech_analysis_rules(rule_type);
create index if not exists idx_tech_rules_active on tech_analysis_rules(is_active) where is_active = true; 