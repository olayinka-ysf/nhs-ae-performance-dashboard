-- Monthly A&E attendances over the last 3 years

USE NHS_AE_Analysis;
GO

SELECT
    FORMAT(period, 'MMM yyyy')      AS month_label,
    period                          AS period_date,
    type1_attendances               AS major_ae_attendances,
    type2_attendances               AS single_specialty_attendances,
    type3_attendances               AS minor_injury_attendances,
    total_attendances,
    LAG(total_attendances, 1) OVER (ORDER BY period) AS prev_month_total,
    total_attendances
        - LAG(total_attendances, 1) OVER (ORDER BY period)
                                    AS mom_change,
    ROUND(
        CAST(
            total_attendances
            - LAG(total_attendances, 1) OVER (ORDER BY period)
        AS FLOAT)
        / NULLIF(LAG(total_attendances, 1) OVER (ORDER BY period), 0)
        * 100
    , 1)                            AS mom_pct_change
FROM
    dbo.ae_timeseries_activity
WHERE
    period > DATEADD(YEAR, -3, (SELECT MAX(period) FROM dbo.ae_timeseries_activity))
ORDER BY
    period ASC;
