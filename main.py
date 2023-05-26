from datetime import datetime, timedelta, timezone
import json
import api.mojo
from flask import Flask, render_template
app = Flask(__name__)


# get new cache
print("Retrieving data from Mojo...")
t1 = datetime.now()
# api.mojo.get_cache()
t2 = datetime.now()
print(f"Cache updated! Time: {t2 - t1}")


@app.route("/")
def index():
    all_tickets = api.mojo.get_cached_tickets()
    all_users = api.mojo.get_cached_users()
    all_groups = api.mojo.get_cached_groups()

    open_tickets = []
    unassigned_tickets = []
    inactive_tickets = []
    waiting_tickets = []

    for ticket in all_tickets:
        if ticket['status_id'] < 60:
            open_tickets.append(ticket)

            if not ticket['assigned_to_id']:
                unassigned_tickets.append(ticket)
            if (datetime.utcnow() - datetime.strptime(ticket['updated_on'], "%Y-%m-%dT%H:%M:%S.%fZ")).days > 18:
                inactive_tickets.append(ticket)
            if ticket['status_id'] == 30 or ticket['status_id'] == 40:
                waiting_tickets.append(ticket)
    created_1d = 0
    created_30d = 0
    closed_1d = 0
    closed_30d = 0

    for ticket in all_tickets:
        # if ticket was created today
        if (datetime.now(timezone.utc) - datetime.fromisoformat(ticket['created_on'] or '1970-01-01T12:00:00Z')) > timedelta(days=1):
            created_1d += 1

        # if ticket was created in last 30 days
        if (datetime.now(timezone.utc) - datetime.fromisoformat(ticket['created_on'] or '1970-01-01T12:00:00Z')) > timedelta(days=30):
            created_30d += 1

        # if ticket was closed today
        if (datetime.now(timezone.utc) - datetime.fromisoformat(ticket['closed_on'] or '1970-01-01T12:00:00Z')) > timedelta(days=1):
            closed_1d += 1

        # if ticket was closed in last 30 days
        if (datetime.now(timezone.utc) - datetime.fromisoformat(ticket['closed_on'] or '1970-01-01T12:00:00Z')) > timedelta(days=30):
            closed_30d += 1

    kill_ratio_1d = round(created_1d/closed_1d, 2)
    kill_ratio_30d = round(created_30d/closed_30d, 2)

    open_tickets_color = "green"
    unassigned_tickets_color = "green"
    inactive_tickets_color = "green"
    waiting_tickets_color = "green"

    if len(open_tickets) >= 50:
        open_tickets_color = "red"
    elif len(open_tickets) >= 25:
        open_tickets_color = "yellow"
        
    if len(unassigned_tickets) >= 10:
        unassigned_tickets_color = "red"
    elif len(unassigned_tickets) >= 5:
        unassigned_tickets_color = "yellow"

    if len(inactive_tickets) >= 10:
        inactive_tickets_color = "red"
    elif len(inactive_tickets) >= 5:
        inactive_tickets_color = "yellow"

    if len(waiting_tickets) >= 20:
        waiting_tickets_color = "red"
    elif len(waiting_tickets) >= 10:
        waiting_tickets_color = "yellow"

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
                           open_tickets_color=open_tickets_color,
                           unassigned_tickets_color=unassigned_tickets_color,
                           inactive_tickets_color=inactive_tickets_color,
                           waiting_tickets_color=waiting_tickets_color
                           )


if __name__ == "__main__":
    app.run(debug=True)
