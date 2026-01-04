select
  date_trunc('day', order_ts) as day,
  sum(order_total) as revenue,
  count(*) as orders
from "warehouse"."raw_mart"."fct_orders"
where status <> 'CANCELLED'
group by 1
order by 1