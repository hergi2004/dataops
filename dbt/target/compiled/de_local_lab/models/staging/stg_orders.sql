select
  order_id,
  customer_id,
  order_ts::timestamptz as order_ts,
  upper(trim(status)) as status,
  order_total::numeric(12,2) as order_total
from raw.orders