
  create view "warehouse"."raw_raw"."stg_customers__dbt_tmp"
    
    
  as (
    select
  customer_id,
  lower(trim(email)) as email,
  upper(trim(state)) as state,
  created_at::timestamptz as created_at
from raw.customers
  );