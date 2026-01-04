
  
    

  create  table "warehouse"."raw_mart"."fct_orders__dbt_tmp"
  
  
    as
  
  (
    with orders as (
  select * from "warehouse"."raw_raw"."stg_orders"
),
items as (
  select
    order_id,
    sum(line_amount) as items_total,
    count(*) as line_count
  from "warehouse"."raw_raw"."stg_order_items"
  group by 1
)

select
  o.order_id,
  o.customer_id,
  o.order_ts,
  o.status,
  o.order_total,
  i.items_total,
  i.line_count
from orders o
left join items i using (order_id)
  );
  