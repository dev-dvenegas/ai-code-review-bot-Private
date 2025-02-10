-- Modificar la tabla de prompts para soportar categorías
ALTER TABLE tech_analysis_prompts
    ADD COLUMN category VARCHAR(50) NOT NULL DEFAULT 'code_analysis',
    DROP COLUMN is_active;

-- Crear índice para búsqueda eficiente por categoría y versión
CREATE INDEX idx_prompts_category_version ON tech_analysis_prompts(category, version);

-- Actualizar los prompts existentes
UPDATE tech_analysis_prompts 
SET category = 'code_analysis' 
WHERE category = 'code_analysis';

-- Insertar prompt para metadata
INSERT INTO tech_analysis_prompts (name, version, category, prompt_text) 
VALUES (
    'pr_metadata_generator',
    '1.0.0',
    'metadata',
    'As a Pull Request Metadata Generator, analyze the following context and generate appropriate metadata following these guidelines:

    Title Guidelines:
    {title_guidelines}

    Description Template:
    {description_template}

    Available Labels:
    {label_guidelines}

    Context:
    {context}

    Generate metadata that follows our guidelines and helps maintainers understand the changes.
    {format_instructions}'
); 