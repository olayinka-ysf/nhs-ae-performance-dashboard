-- Year-over-year 4-hour target performance

USE NHS_AE_Analysis;
GO

WITH yearly_perf AS (
    SELECT
        DATEPART(YEAR, period)              AS performance_year,
        COUNT(*)                            AS months_of_data,
        ROUND(AVG(CAST(pct_within_4hrs AS FLOAT)), 1)
                                            AS avg_pct_within_4hrs,
        ROUND(MIN(pct_within_4hrs), 1)      AS worst_month_pct,
        ROUND(MAX(pct_within_4hrs), 1)      AS best_month_pct,
        SUM(total_within_4hrs)              AS total_seen_within_4hrs,
        SUM(total_over_4hrs)                AS total_breaches,
        SUM(total_all)                      AS total_all_attendances
    FROM
        dbo.ae_timeseries_performance
    GROUP BY
        DATEPART(YEAR, period)
),
with_lag AS (
    SELECT
        performance_year,
        months_of_data,
        avg_pct_within_4hrs,
        worst_month_pct,
        best_month_pct,
        total_seen_within_4hrs,
        total_breaches,
        total_all_attendances,
        LAG(avg_pct_within_4hrs, 1) OVER (ORDER BY performance_year)
                                            AS prev_year_pct
    FROM
        yearly_perf
)
SELECT
    performance_year,
    months_of_data,
    avg_pct_within_4hrs,
    worst_month_pct,
    best_month_pct,
    total_breaches,
    prev_year_pct,
    ROUND(avg_pct_within_4hrs - prev_year_pct, 1)
                                            AS yoy_change_pp,
    CASE
        WHEN avg_pct_within_4hrs > prev_year_pct  THEN 'Improving'
        WHEN avg_pct_within_4hrs < prev_year_pct  THEN 'Deteriorating'
        WHEN prev_year_pct IS NULL                THEN 'No prior year'
        ELSE 'Flat'
    END                                     AS trend_direction
FROM
    with_lag
ORDER BY
    performance_year ASC;
