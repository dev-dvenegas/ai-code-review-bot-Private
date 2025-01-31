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