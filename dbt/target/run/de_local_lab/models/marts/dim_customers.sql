
  
    

  create  table "warehouse"."raw_mart"."dim_customers__dbt_tmp"
  
  
    as
  
  (
    select
  customer_id,
  email,
  state,
  created_at
from "warehouse"."raw_raw"."stg_customers"
  );
  