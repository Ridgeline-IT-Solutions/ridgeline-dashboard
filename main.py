from datetime import datetime, timedelta, timezone
import json
import api.mojo
import api.kaseya
import api.comet
from flask import Flask, render_template

from threading import Thread

app = Flask(__name__)

def get_cache():
    """
    Updates all caches.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    print("Retrieving data from Mojo...")
    t1 = datetime.now()
    api.mojo.get_cache()
    t2 = datetime.now()
    print(f"Mojo cache updated! Time: {t2 - t1}")

    print("Retrieving data from Kaseya...")
    t1 = datetime.now()
    api.kaseya.update_cache()
    t2 = datetime.now()
    print(f"Kaseya cache updated! Time: {t2 - t1}")

    print("Retrieving data from Comet...")
    t1 = datetime.now()
    api.comet.update_cache()
    t2 = datetime.now()
    print(f"Comet cache updated! Time: {t2 - t1}")

def update_cache():
    from time import sleep
    while True:
        get_cache()
        sleep(600) # sleep for 10 mins


@app.route("/")
def index():
    all_tickets = api.mojo.get_cached_tickets()
    all_users = api.mojo.get_cached_users()
    all_groups = api.mojo.get_cached_groups()
    jobs = api.comet.get_cached_jobs()
    jobs_statuses = api.comet.get_jobs_status(jobs)

    open_tickets = []
    unassigned_tickets = []
    inactive_tickets = []
    waiting_tickets = []

    for ticket in all_tickets:
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

    turnarounds = []

    for ticket in all_tickets:
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
            turnarounds.append((datetime.fromisoformat(ticket['closed_on']) - datetime.fromisoformat(ticket['created_on'])))

    avg_turnaround = sum(turnarounds, timedelta(0)) / len(turnarounds)
    avg_turnaround_str = f"{avg_turnaround.days}d{(avg_turnaround.seconds%3600)%24}h"

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
    recent_alarms = []

    for agent in agents:
        if (datetime.now(timezone.utc) - datetime.fromisoformat(agent['LastCheckInTime'])) > timedelta(days=15):
            inactive_agents.append(agent)

    for agent in patches:
        if agent['TotalVulnerabilitiesCount'] >= 4:
            ood_agents.append(agent)

    for alarm in alarms:
        if (datetime.now(timezone.utc) - datetime.fromisoformat(alarm['EventUtcTime'])) < timedelta(days=1):
            recent_alarms.append(alarm)

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
        avg_turnaround=avg_turnaround_str,
        all_agents=json.dumps(agents),
        inactive_agents=len(inactive_agents),
        inactive_agents_json=json.dumps(inactive_agents),
        ood_agents=len(ood_agents),
        ood_agents_json=json.dumps(ood_agents),
        recent_alarms=len(recent_alarms),
        recent_alarms_json=json.dumps(recent_alarms),
        jobs_json=json.dumps(jobs),
        jobs_statuses=json.dumps(jobs_statuses)
        )


if __name__ == "__main__":
    t = Thread(target=update_cache, daemon=True, name='Background Cache Updates')
    t.start()
    app.run(debug=True)