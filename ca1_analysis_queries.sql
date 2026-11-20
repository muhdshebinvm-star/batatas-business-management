-- =====================================================================
-- Bataatas Business Analytics — SQL Analysis
-- Database: bataatas_db
-- Covers: JOINs, aggregate functions, filtering, GROUP BY, sorting,
--         subqueries (rubric item 2: Data Collection, MySQL & SQL Business Analysis)
-- =====================================================================

USE bataatas_db;

-- ---------------------------------------------------------------------
-- Q1. Total sales, total expenses and net cash generated per branch
--     (JOIN + aggregation + GROUP BY + sorting)
-- ---------------------------------------------------------------------
SELECT
    b.branch_name,
    COUNT(ds.sale_id)                          AS days_recorded,
    ROUND(SUM(ds.total_sales_value), 2)        AS total_sales,
    ROUND(SUM(ds.exp_staff + ds.exp_rent_power + ds.all_purchases), 2) AS total_expenses,
    ROUND(SUM(ds.cash_available_on_day), 2)     AS net_cash_generated,
    ROUND(AVG(ds.total_sales_value), 2)         AS avg_daily_sales
FROM branches b
JOIN daily_sales ds ON ds.branch_id = b.branch_id
GROUP BY b.branch_name
ORDER BY total_sales DESC;

-- ---------------------------------------------------------------------
-- Q2. Weekday vs weekend sales pattern per branch
--     (grouping by derived value, aggregation, sorting)
-- ---------------------------------------------------------------------
SELECT
    b.branch_name,
    CASE WHEN DAYOFWEEK(ds.sale_date) IN (1,6,7) THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    ROUND(AVG(ds.total_sales_value), 2) AS avg_sales,
    COUNT(*) AS num_days
FROM daily_sales ds
JOIN branches b ON b.branch_id = ds.branch_id
GROUP BY b.branch_name, day_type
ORDER BY b.branch_name, day_type;

-- ---------------------------------------------------------------------
-- Q3. Top 5 highest single-day sales across all branches (filtering + sorting)
-- ---------------------------------------------------------------------
SELECT b.branch_name, ds.sale_date, ds.total_sales_value
FROM daily_sales ds
JOIN branches b ON b.branch_id = ds.branch_id
WHERE ds.total_sales_value > 0
ORDER BY ds.total_sales_value DESC
LIMIT 5;

-- ---------------------------------------------------------------------
-- Q4. Branches whose average daily sales are ABOVE the company-wide
--     average (subquery)
-- ---------------------------------------------------------------------
SELECT branch_name, avg_sales
FROM (
    SELECT b.branch_name, AVG(ds.total_sales_value) AS avg_sales
    FROM daily_sales ds
    JOIN branches b ON b.branch_id = ds.branch_id
    GROUP BY b.branch_name
) branch_avg
WHERE avg_sales > (SELECT AVG(total_sales_value) FROM daily_sales)
ORDER BY avg_sales DESC;

-- ---------------------------------------------------------------------
-- Q5. Top 5 costliest ingredient/purchase categories company-wide
--     (aggregation + GROUP BY + sorting)
-- ---------------------------------------------------------------------
SELECT item_name, ROUND(SUM(amount), 2) AS total_spent, COUNT(*) AS num_purchases
FROM purchases
GROUP BY item_name
ORDER BY total_spent DESC
LIMIT 5;

-- ---------------------------------------------------------------------
-- Q6. Per-branch purchase spend as a % of that branch's total sales
--     (subquery in SELECT + JOIN)
-- ---------------------------------------------------------------------
SELECT
    b.branch_name,
    ROUND((SELECT SUM(amount) FROM purchases p WHERE p.branch_id = b.branch_id), 2) AS total_purchase_spend,
    ROUND((SELECT SUM(total_sales_value) FROM daily_sales d WHERE d.branch_id = b.branch_id), 2) AS total_sales,
    ROUND(
        (SELECT SUM(amount) FROM purchases p WHERE p.branch_id = b.branch_id) /
        (SELECT SUM(total_sales_value) FROM daily_sales d WHERE d.branch_id = b.branch_id) * 100, 2
    ) AS purchase_pct_of_sales
FROM branches b
ORDER BY purchase_pct_of_sales DESC;

-- ---------------------------------------------------------------------
-- Q7. Days where cash available went negative — operational risk flag
--     (filtering + JOIN + sorting)
-- ---------------------------------------------------------------------
SELECT b.branch_name, ds.sale_date, ds.cash_available_on_day
FROM daily_sales ds
JOIN branches b ON b.branch_id = ds.branch_id
WHERE ds.cash_available_on_day < 0
ORDER BY ds.cash_available_on_day ASC;

-- ---------------------------------------------------------------------
-- Q8. Month-over-month net income per branch, from the P&L table
--     (JOIN + sorting)
-- ---------------------------------------------------------------------
SELECT b.branch_name, p.month, p.sales, p.cogs, p.gross_profit,
       p.labor_expense, p.other_expense, p.net_income,
       ROUND(p.net_income / p.sales * 100, 2) AS net_margin_pct
FROM monthly_pnl p
JOIN branches b ON b.branch_id = p.branch_id
ORDER BY b.branch_name, p.month;

-- ---------------------------------------------------------------------
-- Q9. Rank branches by net profit margin (window function)
-- ---------------------------------------------------------------------
SELECT branch_name, month, net_margin_pct,
       RANK() OVER (PARTITION BY month ORDER BY net_margin_pct DESC) AS margin_rank
FROM (
    SELECT b.branch_name, p.month, ROUND(p.net_income / p.sales * 100, 2) AS net_margin_pct
    FROM monthly_pnl p JOIN branches b ON b.branch_id = p.branch_id
) t
ORDER BY month, margin_rank;
