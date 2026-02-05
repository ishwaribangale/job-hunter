-- Job Hunter MVP schema

create table if not exists applications (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  job_id text not null,
  company text,
  title text,
  location text,
  source text,
  apply_link text,
  stage text not null default 'Applied',
  notes text default '',
  applied_date timestamptz default now(),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create unique index if not exists applications_user_job_unique
  on applications (user_id, job_id);

create index if not exists applications_user_stage_idx
  on applications (user_id, stage);

create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists applications_set_updated_at on applications;
create trigger applications_set_updated_at
before update on applications
for each row execute function set_updated_at();
