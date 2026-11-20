USE bataatas_db;

-- Preview the two temporary Manjeri test rows before deletion.
SELECT sale_id, branch_id, sale_date, opening_balance, total_sales_value,
       exp_staff, exp_rent_power, all_purchases, cash_available_on_day
FROM daily_sales
WHERE branch_id = (SELECT branch_id FROM branches WHERE branch_name = 'Manjeri')
  AND sale_date = '2026-11-20'
  AND opening_balance = 10000.00
  AND exp_staff = 780.00
  AND exp_rent_power = 420.00
  AND all_purchases = 1000.00
  AND total_sales_value IN (2000.00, 12000.00);

-- Run this DELETE only after confirming the preview contains exactly the two test rows.
-- Uncomment the following statement, execute it, then run SELECT COUNT(*) to verify.
-- DELETE FROM daily_sales
-- WHERE branch_id = (SELECT branch_id FROM branches WHERE branch_name = 'Manjeri')
--   AND sale_date = '2026-11-20'
--   AND opening_balance = 10000.00
--   AND exp_staff = 780.00
--   AND exp_rent_power = 420.00
--   AND all_purchases = 1000.00
--   AND total_sales_value IN (2000.00, 12000.00);
