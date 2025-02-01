-- Tabla para lineamientos de títulos de PR
CREATE TABLE tech_pr_title_guidelines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prefix TEXT NOT NULL,
    description TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    min_length INTEGER NOT NULL DEFAULT 10,
    max_length INTEGER NOT NULL DEFAULT 72,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT valid_length_range CHECK (min_length > 0 AND max_length >= min_length)
);

-- Tabla para plantillas de descripción de PR
CREATE TABLE tech_pr_description_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    template_content TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Tabla para etiquetas de PR
CREATE TABLE tech_pr_labels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    color TEXT NOT NULL DEFAULT '#CCCCCC',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Índices
CREATE INDEX idx_title_guidelines_active ON tech_pr_title_guidelines(is_active) WHERE is_active = true;
CREATE INDEX idx_description_templates_active ON tech_pr_description_templates(is_active) WHERE is_active = true;
CREATE INDEX idx_pr_labels_active ON tech_pr_labels(is_active) WHERE is_active = true; 