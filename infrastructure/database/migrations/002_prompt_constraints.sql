-- Asegurar que solo puede haber un prompt activo a la vez
create or replace function check_single_active_prompt()
returns trigger as $$
begin
    if NEW.is_active = true then
        update tech_analysis_prompts
        set is_active = false
        where id != NEW.id and is_active = true;
    end if;
    return NEW;
end;
$$ language plpgsql;

create trigger ensure_single_active_prompt
    before insert or update on tech_analysis_prompts
    for each row
    execute function check_single_active_prompt(); 