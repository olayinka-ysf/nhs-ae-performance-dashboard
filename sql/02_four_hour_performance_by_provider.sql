-- 4-hour target performance ranked worst to best (Feb 2026)

USE NHS_AE_Analysis;
GO

SELECT
    org_code,
    org_name,
    parent_org                          AS nhs_region,
    type1_total_attendances,
    type1_total_over_4hrs               AS breaches,
    type1_pct_within_4hrs               AS pct_within_4hrs,
    CASE
        WHEN type1_pct_within_4hrs >= 95  THEN 'Excellent (>=95%)'
        WHEN type1_pct_within_4hrs >= 85  THEN 'Good (85-94%)'
        WHEN type1_pct_within_4hrs >= 78  THEN 'Meeting standard (78-84%)'
        WHEN type1_pct_within_4hrs >= 70  THEN 'Below standard (70-77%)'
        WHEN type1_pct_within_4hrs >= 60  THEN 'Poor (60-69%)'
        WHEN type1_pct_within_4hrs IS NOT NULL
                                          THEN 'Critical (<60%)'
        ELSE 'N/A - No Type 1 activity'
    END                                 AS performance_band,
    RANK() OVER (
        ORDER BY type1_pct_within_4hrs ASC
    )                                   AS rank_worst_first
FROM
    dbo.ae_provider_feb2026
WHERE
    type1_total_attendances > 0
ORDER BY
    type1_pct_within_4hrs ASC;
