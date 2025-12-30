select
  customer_id,
  email,
  state,
  created_at
from {{ ref('stg_customers') }}
