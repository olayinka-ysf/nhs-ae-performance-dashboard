-- Top 10 and bottom 10 performing Type 1 trusts (Feb 2026)

USE NHS_AE_Analysis;
GO

WITH ranked AS (
    SELECT
        org_code,
        org_name,
        parent_org                          AS nhs_region,
        type1_total_attendances,
        type1_total_over_4hrs               AS breaches,
        type1_pct_within_4hrs,
        DENSE_RANK() OVER (
            ORDER BY type1_pct_within_4hrs DESC
        )                                   AS rank_best,
        DENSE_RANK() OVER (
            ORDER BY type1_pct_within_4hrs ASC
        )                                   AS rank_worst
    FROM
        dbo.ae_provider_feb2026
    WHERE
        type1_total_attendances > 0
        AND type1_pct_within_4hrs IS NOT NULL
)
SELECT
    'Top 10'                            AS group_label,
    rank_best                           AS rank_position,
    org_code,
    org_name,
    nhs_region,
    type1_total_attendances,
    breaches,
    type1_pct_within_4hrs
FROM ranked
WHERE rank_best <= 10

UNION ALL

SELECT
    'Bottom 10'                         AS group_label,
    rank_worst                          AS rank_position,
    org_code,
    org_name,
    nhs_region,
    type1_total_attendances,
    breaches,
    type1_pct_within_4hrs
FROM ranked
WHERE rank_worst <= 10

ORDER BY
    group_label DESC,
    rank_position ASC;
