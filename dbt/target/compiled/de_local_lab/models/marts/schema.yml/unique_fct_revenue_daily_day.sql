
    
    

select
    day as unique_field,
    count(*) as n_records

from "warehouse"."raw_mart"."fct_revenue_daily"
where day is not null
group by day
having count(*) > 1


