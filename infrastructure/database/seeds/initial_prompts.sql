-- Este archivo contiene los datos iniciales necesarios para que la aplicación funcione
-- Incluye prompts base y reglas predefinidas para el análisis de código

-- Prompt base para análisis técnico
-- Este es el prompt principal que usa la IA para analizar PRs
INSERT INTO tech_analysis_prompts (name, version, prompt_text) VALUES
('code_review_prompt', '1.0.0', 
'You are an expert code reviewer. Analyze the provided pull request changes and provide detailed feedback.
Focus on the following aspects and apply the company rules below:

Company Rules:
{company_rules}

Key Areas to Review:
1. Code quality and best practices
2. Potential bugs or issues
3. Performance considerations
4. Security concerns
5. Maintainability and readability

Format your response according to the following schema:
{format_instructions}
');

-- Reglas de ejemplo para el análisis de código
-- Estas reglas se combinan con el prompt principal
INSERT INTO tech_analysis_rules (name, rule_type, description, rule_content, priority) VALUES
-- Regla de estilo de código
('naming_convention', 'style', 'Naming conventions for variables and functions', 
'Use snake_case for variables and functions in Python. Use PascalCase for classes.', 1),

-- Regla de seguridad
('security_check', 'security', 'Security best practices', 
'Never log sensitive information. Always validate user input. Use parameterized queries for database operations.', 2),

-- Regla de rendimiento
('performance_rule', 'performance', 'Performance considerations', 
'Avoid N+1 queries. Use bulk operations when possible. Consider pagination for large datasets.', 3),

-- Regla de testing
('testing_requirement', 'testing', 'Testing requirements', 
'All new features must include unit tests. Integration tests are required for API endpoints.', 4);

-- Data inicial para tech_pr_title_guidelines
INSERT INTO tech_pr_title_guidelines (prefix, description, min_length, max_length)
VALUES
  ('feat', 'New feature PRs should start with "feat:" followed by a concise description.', 10, 72),
  ('fix', 'Bug fix PRs should start with "fix:" followed by a concise description.', 10, 72),
  ('refactor', 'Refactoring PRs should start with "refactor:" followed by a concise description.', 10, 72),
  ('perf', 'Performance improvement PRs should start with "perf:" followed by a concise description.', 10, 72),
  ('style', 'Style changes should start with "style:" followed by a concise description.', 10, 72),
  ('test', 'Test-related PRs should start with "test:" followed by a concise description.', 10, 72),
  ('docs', 'Documentation changes should start with "docs:" followed by a concise description.', 10, 72),
  ('build', 'Build or dependency updates should start with "build:" followed by a concise description.', 10, 72),
  ('ops', 'Operations or infrastructure changes should start with "ops:" followed by a concise description.', 10, 72),
  ('chore', 'Chore tasks should start with "chore:" followed by a concise description.', 10, 72);

-- Data inicial para tech_pr_description_templates
INSERT INTO tech_pr_description_templates (name, template_content)
VALUES
  (
    'default',
    '## Tipo de PR (selecciona una opción):\n' ||
    '- [ ] feat: Nueva funcionalidad.\n' ||
    '- [ ] fix: Corrección de un bug.\n' ||
    '- [ ] refactor: Reestructuración del código sin cambiar la lógica.\n' ||
    '- [ ] perf: Mejoras de rendimiento.\n' ||
    '- [ ] style: Cambios estéticos sin afectar la lógica.\n' ||
    '- [ ] test: Adición o corrección de pruebas.\n' ||
    '- [ ] docs: Cambios en la documentación.\n' ||
    '- [ ] build: Cambios en dependencias o herramientas de compilación.\n' ||
    '- [ ] ops: Cambios operativos como infraestructura o despliegue.\n' ||
    '- [ ] chore: Tareas misceláneas.\n\n' ||
    '## 🚀 Descripción:\n' ||
    'Explica qué hace este PR y por qué es necesario.\n' ||
    '- Motivación: ¿Qué problema resuelve o qué necesidad cubre?\n' ||
    '- Contexto adicional: Información que pueda ayudar a entender mejor el cambio.\n\n' ||
    '## 📋 Cambios Realizados:\n' ||
    'Lista clara y concisa de los cambios introducidos.\n\n' ||
    '## 🛠️ ¿Cómo Probarlo?:\n' ||
    'Pasos para validar este PR.\n\n' ||
    '## ✅ Checklist:\n' ||
    'Verifica que se cumplan los siguientes puntos antes de aprobar el PR.\n\n' ||
    '## 🔍 Impacto y Métricas:\n' ||
    'Describe el impacto esperado y las métricas a monitorear.\n\n' ||
    '## 🛡️ Identificación de Riesgos:\n' ||
    'Riesgos potenciales y plan de mitigación.\n\n' ||
    '## 🔗 Relacionado con:\n' ||
    'Referencia a issues o PRs relacionados.'
  );

-- Data inicial para tech_pr_labels
INSERT INTO tech_pr_labels (name, description, color)
VALUES
  ('build', 'Changes affecting the build system or external dependencies.', '#1F8A70'),
  ('chore', 'Miscellaneous changes that do not affect functionality.', '#B83227'),
  ('docs', 'Documentation changes only.', '#2C3E50'),
  ('feat', 'New feature development.', '#27AE60'),
  ('fix', 'Bug fixes.', '#E74C3C'),
  ('ops', 'Operational or infrastructure changes.', '#8E44AD'),
  ('perf', 'Performance improvements.', '#F39C12'),
  ('refactor', 'Code refactoring without changing functionality.', '#2980B9'),
  ('style', 'Style or cosmetic changes.', '#D35400'),
  ('test', 'Test-related changes.', '#7DCEA0');
