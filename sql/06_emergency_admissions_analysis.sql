-- Emergency admissions as a percentage of attendances by region and trust size

USE NHS_AE_Analysis;
GO

WITH provider_calcs AS (
    SELECT
        org_code,
        org_name,
        parent_org                          AS nhs_region,
        type1_total_attendances,
        emergency_admissions_type1,
        ROUND(
            CAST(emergency_admissions_type1 AS FLOAT)
            / NULLIF(type1_total_attendances, 0) * 100
        , 1)                                AS admission_rate_pct,
        CASE
            WHEN type1_total_attendances > 10000 THEN 'Large (>10k/month)'
            WHEN type1_total_attendances >  5000 THEN 'Medium (5k-10k/month)'
            WHEN type1_total_attendances >     0 THEN 'Small (<5k/month)'
            ELSE 'No Type 1 activity'
        END                                 AS trust_size_band,
        CASE
            WHEN CAST(emergency_admissions_type1 AS FLOAT)
                 / NULLIF(type1_total_attendances, 0) > 0.35
                THEN 'High (>35%)'
            WHEN CAST(emergency_admissions_type1 AS FLOAT)
                 / NULLIF(type1_total_attendances, 0) > 0.25
                THEN 'Moderate (25-35%)'
            WHEN CAST(emergency_admissions_type1 AS FLOAT)
                 / NULLIF(type1_total_attendances, 0) > 0
                THEN 'Low (<25%)'
            ELSE 'No data'
        END                                 AS admission_pressure_flag
    FROM dbo.ae_provider_feb2026
    WHERE type1_total_attendances > 0
)
SELECT
    nhs_region,
    trust_size_band,
    COUNT(*)                                AS trust_count,
    SUM(type1_total_attendances)            AS total_type1_attendances,
    SUM(emergency_admissions_type1)         AS total_emerg_admissions,
    ROUND(
        CAST(SUM(emergency_admissions_type1) AS FLOAT)
        / NULLIF(SUM(type1_total_attendances), 0) * 100
    , 1)                                    AS group_admission_rate_pct,
    ROUND(AVG(CAST(admission_rate_pct AS FLOAT)), 1)
                                            AS avg_trust_admission_rate,
    MIN(admission_rate_pct)                 AS min_admission_rate,
    MAX(admission_rate_pct)                 AS max_admission_rate
FROM
    provider_calcs
GROUP BY
    nhs_region,
    trust_size_band
ORDER BY
    nhs_region,
    trust_size_band;
