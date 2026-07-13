"""Sets the ad schedule (AD_SCHEDULE spec in build_campaigns.py) on all campaigns.

Creates one criterion per day of week with the configured start/end hours.
Idempotent: campaigns whose existing schedule already matches are skipped;
a mismatched schedule is removed and recreated.

Run: .venv/bin/python scripts/set_ad_schedule.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from build_campaigns import AD_SCHEDULE, get_client, search

DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]


def main():
    client = get_client()
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    svc = client.get_service("CampaignCriterionService")
    start, end = AD_SCHEDULE["start_hour"], AD_SCHEDULE["end_hour"]

    campaigns = search(
        client,
        customer_id,
        "SELECT campaign.resource_name, campaign.name FROM campaign "
        "WHERE campaign.status != 'REMOVED'",
    )
    for c in campaigns:
        rn = c.campaign.resource_name
        existing = search(
            client,
            customer_id,
            "SELECT campaign_criterion.resource_name, "
            "campaign_criterion.ad_schedule.day_of_week, "
            "campaign_criterion.ad_schedule.start_hour, "
            "campaign_criterion.ad_schedule.end_hour "
            "FROM campaign_criterion "
            f"WHERE campaign_criterion.type = 'AD_SCHEDULE' "
            f"AND campaign.resource_name = '{rn}'",
        )
        current = sorted(
            (r.campaign_criterion.ad_schedule.day_of_week.name,
             r.campaign_criterion.ad_schedule.start_hour,
             r.campaign_criterion.ad_schedule.end_hour)
            for r in existing
        )
        wanted = sorted((d, start, end) for d in DAYS)
        if current == wanted:
            print(f"• {c.campaign.name}: schedule already {start}:00-{end}:00 daily")
            continue

        ops = []
        for r in existing:
            op = client.get_type("CampaignCriterionOperation")
            op.remove = r.campaign_criterion.resource_name
            ops.append(op)
        for day in DAYS:
            op = client.get_type("CampaignCriterionOperation")
            crit = op.create
            crit.campaign = rn
            crit.ad_schedule.day_of_week = getattr(
                client.enums.DayOfWeekEnum, day
            )
            crit.ad_schedule.start_hour = start
            crit.ad_schedule.start_minute = client.enums.MinuteOfHourEnum.ZERO
            crit.ad_schedule.end_hour = end
            crit.ad_schedule.end_minute = client.enums.MinuteOfHourEnum.ZERO
            ops.append(op)
        svc.mutate_campaign_criteria(customer_id=customer_id, operations=ops)
        print(f"✓ {c.campaign.name}: schedule set to {start}:00-{end}:00 daily "
              f"({len(existing)} old criteria removed)")

    print("\nDone. Ads now serve only inside the scheduled window.")


if __name__ == "__main__":
    main()
