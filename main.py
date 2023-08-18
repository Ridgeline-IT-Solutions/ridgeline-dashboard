from datetime import datetime, timedelta, timezone
import json
import api.mojo
import api.kaseya
import api.comet
import api.ruon
import api.dnsfilter
import api.huntress
from api.caching import get_cache
from flask import Flask, render_template

import os

os.makedirs('cache', exist_ok=True)
os.makedirs('cache/mojo', exist_ok=True)
os.makedirs('cache/comet', exist_ok=True)
os.makedirs('cache/dnsfilter', exist_ok=True)
os.makedirs('cache/kaseya', exist_ok=True)
os.makedirs('cache/ruon', exist_ok=True)
os.makedirs('cache/huntress', exist_ok=True)

app = Flask(__name__)

@app.route("/")
def index():
    all_tickets = api.mojo.get_tickets()
    all_users = api.mojo.get_users()
    all_groups = api.mojo.get_groups()
    jobs = api.comet.get_jobs()
    jobs_statuses = api.comet.get_jobs_status(jobs)
    device_counts = get_cache('comet/counts.json', timedelta(minutes = 10), api.comet.counts)
    ruon_agents = get_cache('ruon/agents.json', timedelta(minutes = 10), api.ruon.get_agents)

    open_tickets = []
    unassigned_tickets = []
    inactive_tickets = []
    waiting_tickets = []

    for ticket in all_tickets.values():
        if ticket['status_id'] < 60:
            open_tickets.append(ticket)

            if not ticket['assigned_to_id']:
                unassigned_tickets.append(ticket)
            if (datetime.utcnow() - datetime.strptime(ticket['updated_on'], "%Y-%m-%dT%H:%M:%S.%fZ")).days > 15:
                inactive_tickets.append(ticket)
            if ticket['status_id'] == 30 or ticket['status_id'] == 40:
                waiting_tickets.append(ticket)
    created_1d = 0
    created_30d = 0
    closed_1d = 0
    closed_30d = 0

    for ticket in all_tickets.values():
        # if ticket was created today
        if (datetime.now(timezone.utc) - datetime.fromisoformat(ticket['created_on'] or '1970-01-01T12:00:00Z')) < timedelta(days=1):
            created_1d += 1

        # if ticket was created in last 30 days
        if (datetime.now(timezone.utc) - datetime.fromisoformat(ticket['created_on'] or '1970-01-01T12:00:00Z')) < timedelta(days=30):
            created_30d += 1

        # if ticket was closed today
        if (datetime.now(timezone.utc) - datetime.fromisoformat(ticket['closed_on'] or '1970-01-01T12:00:00Z')) < timedelta(days=1):
            closed_1d += 1

        # if ticket was closed in last 30 days
        if (datetime.now(timezone.utc) - datetime.fromisoformat(ticket['closed_on'] or '1970-01-01T12:00:00Z')) < timedelta(days=30):
            closed_30d += 1

    try:
        kill_ratio_1d = round(closed_1d/created_1d, 2)
    except:
        kill_ratio_1d = closed_1d
    try:
        kill_ratio_30d = round(closed_30d/created_30d, 2)
    except:
        kill_ratio_30d = closed_1d

    agents = api.kaseya.get_agents()
    patches = api.kaseya.get_patches()
    alarms = api.kaseya.get_alarms()

    inactive_agents = []
    ood_agents = []
    critical_agents = []
    recent_alarms = []

    huntress_agents = api.huntress.get_agents()
    huntress_incidents = api.huntress.get_incidents()

    huntress_incidents_resolved_7d = 0
    huntress_incidents_resolved_30d = 0
    huntress_incidents_resolved_90d = 0
    huntress_incidents_critical = 0
    huntress_incidents_high = 0
    huntress_incidents_low = 0

    for incident in huntress_incidents:
        if incident['closed_at']:
            date = datetime.fromisoformat(incident['closed_at'] or '1970-01-01T12:00:00Z')
            comp = datetime.now(timezone.utc) - datetime.fromisoformat(incident['closed_at'] or '1970-01-01T12:00:00Z')
            if comp < timedelta(days=7):
                huntress_incidents_resolved_7d += 1
            if comp < timedelta(days=30):
                huntress_incidents_resolved_30d += 1
            if comp < timedelta(days=90):
                huntress_incidents_resolved_90d += 1
        else :
            match incident['severity']:
                case "low":
                    huntress_incidents_low += 1
                case "high":
                    huntress_incidents_high += 1
                case "critical":
                    huntress_incidents_critical += 1

    for agent in agents:
        if (datetime.now(timezone.utc) - datetime.fromisoformat(agent['LastCheckInTime'])) > timedelta(days=15):
            inactive_agents.append(agent)

    for agent in patches:
        if agent['TotalVulnerabilitiesCount'] >= 4:
            ood_agents.append(agent)
        if agent['PatchAnalysisProfileName'] == 'Critical Only':
            critical_agents.append(agent)

    for alarm in alarms:
        if (datetime.now(timezone.utc) - datetime.fromisoformat(alarm['EventUtcTime'])) < timedelta(days=1):
            recent_alarms.append(alarm)

    ruon_statuses = {
        "Okay": 0,
        "Critical": 0,
        "Major": 0,
        "Minor": 0
    }
    
    for agent in ruon_agents:
        ruon_statuses[ruon_agents[agent]] += 1

    dnsfilter_numbers_2h = get_cache('dnsfilter/total_stats_2.json', timedelta(minutes=10), api.dnsfilter._get_total_stats, (2))
    dnsfilter_numbers_24h = get_cache('dnsfilter/total_stats_24.json', timedelta(minutes=10), api.dnsfilter._get_total_stats, (24))
    dnsfilter_top5_2h = api.dnsfilter.get_most_threats(5, 2)
    dnsfilter_top5_24h = api.dnsfilter.get_most_threats(5, 24)

    return render_template("index.html",
        open_tickets=len(open_tickets),
        unassigned_tickets=len(unassigned_tickets),
        inactive_tickets=len(inactive_tickets),
        waiting_tickets=len(waiting_tickets),
        open_tickets_json=json.dumps(open_tickets),
        unassigned_tickets_json=json.dumps(unassigned_tickets),
        inactive_tickets_json=json.dumps(inactive_tickets),
        waiting_tickets_json=json.dumps(waiting_tickets),
        users=json.dumps(all_users),
        groups=json.dumps(all_groups),
        kill_ratio_1d=kill_ratio_1d,
        kill_ratio_30d=kill_ratio_30d,
        all_agents=json.dumps(agents),
        inactive_agents=len(inactive_agents),
        inactive_agents_json=json.dumps(inactive_agents),
        ood_agents=len(ood_agents),
        ood_agents_json=json.dumps(ood_agents),
        critical_agents=len(critical_agents),
        critical_agents_json=json.dumps(critical_agents),
        recent_alarms=len(recent_alarms),
        recent_alarms_json=json.dumps(recent_alarms),
        jobs_json=json.dumps(jobs),
        jobs_statuses=json.dumps(jobs_statuses),
        device_counts=json.dumps(device_counts),
        ruon_statuses=json.dumps(ruon_statuses),
        ruon_alerts = len(get_cache('ruon/alarms.json', timedelta(minutes=10), api.ruon.get_alarms)),
        dnsfilter_numbers_2h = dnsfilter_numbers_2h,
        dnsfilter_numbers_24h = dnsfilter_numbers_24h,
        dnsfilter_top5_2h = dnsfilter_top5_2h,
        dnsfilter_top5_24h = dnsfilter_top5_24h,
        huntress_agents_count = len(huntress_agents),
        huntress_incidents_resolved_7d = huntress_incidents_resolved_7d,
        huntress_incidents_resolved_30d = huntress_incidents_resolved_30d,
        huntress_incidents_resolved_90d = huntress_incidents_resolved_90d,
        huntress_incidents_critical = huntress_incidents_critical,
        huntress_incidents_high = huntress_incidents_high,
        huntress_incidents_low = huntress_incidents_low,
        )


if __name__ == "__main__":
    app.run(debug=True)