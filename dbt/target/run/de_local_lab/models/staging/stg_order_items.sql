
  create view "warehouse"."raw_raw"."stg_order_items__dbt_tmp"
    
    
  as (
    select
  order_id,
  product_id,
  category,
  unit_price::numeric(12,2) as unit_price,
  quantity::int as quantity,
  line_amount::numeric(12,2) as line_amount
from raw.order_items
  );