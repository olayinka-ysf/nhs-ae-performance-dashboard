-- Seasonal patterns in A&E attendances by calendar month

USE NHS_AE_Analysis;
GO

WITH monthly_averages AS (
    SELECT
        DATEPART(MONTH, period)         AS month_num,
        FORMAT(DATEFROMPARTS(2000, DATEPART(MONTH, period), 1), 'MMMM')
                                        AS month_name,
        COUNT(*)                        AS years_of_data,
        AVG(total_attendances)          AS avg_total_attendances,
        AVG(type1_attendances)          AS avg_type1_attendances,
        MIN(total_attendances)          AS min_total_attendances,
        MAX(total_attendances)          AS max_total_attendances,
        ROUND(
            CAST(STDEV(total_attendances) AS FLOAT)
            / NULLIF(AVG(total_attendances), 0) * 100
        , 1)                            AS variation_pct
    FROM
        dbo.ae_timeseries_activity
    GROUP BY
        DATEPART(MONTH, period)
)
SELECT
    month_name,
    month_num,
    years_of_data,
    avg_total_attendances,
    avg_type1_attendances,
    min_total_attendances,
    max_total_attendances,
    variation_pct,
    ROUND(
        CAST(avg_total_attendances AS FLOAT)
        / NULLIF(AVG(avg_total_attendances) OVER (), 0) * 100
        - 100
    , 1)                                AS pct_vs_annual_avg,
    RANK() OVER (ORDER BY avg_total_attendances DESC)
                                        AS busiest_rank
FROM
    monthly_averages
ORDER BY
    month_num;
