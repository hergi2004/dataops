-- After dbt build, try these:

-- Daily revenue trend
select * from mart.fct_revenue_daily order by day desc limit 14;

-- Top customers by revenue
select
  c.customer_id,
  c.state,
  sum(o.order_total) as revenue
from mart.fct_orders o
join mart.dim_customers c using (customer_id)
where o.status <> 'CANCELLED'
group by 1,2
order by revenue desc
limit 20;

-- Streaming table (if enabled)
select event_type, count(*) from raw.order_events group by 1 order by 2 desc;
