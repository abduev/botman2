# These are example SQL queries. Adapt to your real schema.

QUERIES = {
    "avg_today_bill": {
        "title": "Средний чек за день",
        "sql":"""
SELECT AVG("DishDiscountSumInt") AS avg_check
FROM public.sales_report_tortberi_test
WHERE CAST("OpenDate.Typed" as date) = CURRENT_DATE;
""",
    },
    "weekly_sales": {
        "title": "Выручка за последнюю неделю",
        "sql": """
SELECT SUM("DishDiscountSumInt") AS revenue
FROM public.sales_report_tortberi_test
WHERE CAST("OpenDate.Typed" as date) >= CURRENT_DATE - INTERVAL '7 days';
""",
    },
    "top_10_dishes": {
        "title": "Топ 10 блюд за последние 30 дней",
        "sql": """
SELECT "DishName", SUM("DishAmountInt") AS total_sold
FROM public.sales_report_tortberi_test
WHERE CAST("OpenDate.Typed" as date) >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY "DishName"
ORDER BY total_sold DESC
LIMIT 10;
""",
    },
    "today_sales": {
        "title": "Продажи сегодня",
        "sql": """
SELECT SUM("DishDiscountSumInt") AS revenue
FROM public.sales_report_tortberi_test
WHERE CAST("OpenDate.Typed" AS date) = CURRENT_DATE;
""",
    },
}
