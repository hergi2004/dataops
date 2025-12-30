select
  order_id,
  product_id,
  category,
  unit_price::numeric(12,2) as unit_price,
  quantity::int as quantity,
  line_amount::numeric(12,2) as line_amount
from raw.order_items
