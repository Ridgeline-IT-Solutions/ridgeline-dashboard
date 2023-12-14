from datetime import datetime, timedelta, timezone
import json
import api.mojo
import api.kaseya
import api.comet
import api.ruon
import api.dnsfilter
import api.huntress
from api.caching import get_cache
import sqlite3
from flask import Flask, render_template, request
import os
from geopy.geocoders import Nominatim

con = sqlite3.connect('database.db', timeout=10)
cur = con.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS clients(abbreviation CHAR(8) PRIMARY KEY, name TEXT, address CHAR(50), city CHAR(50), state CHAR(2), zip_code INT, latitude REAL, longitude REAL, server INT, ipv4 CHAR(15));')
con.commit()
con.close()

os.makedirs('cache', exist_ok=True)
os.makedirs('cache/mojo', exist_ok=True)
os.makedirs('cache/comet', exist_ok=True)
os.makedirs('cache/dnsfilter', exist_ok=True)
os.makedirs('cache/kaseya', exist_ok=True)
os.makedirs('cache/ruon', exist_ok=True)
os.makedirs('cache/huntress', exist_ok=True)

def geolocate_address(address):
    geolocator = Nominatim(user_agent="ridgeline-map")
    location = geolocator.geocode(address)
    return location.latitude, location.longitude

app = Flask(__name__)

@app.route("/map")
def map():
    return render_template("html/map.html")

@app.route("/js_functions")
def js_functions():
    return render_template("js/functions.js")

@app.route("/edit_clients")
def edit_clients():
    return render_template("html/edit_clients.html")

@app.route("/get_clients", methods=['POST'])
def get_clients():
    con = sqlite3.connect('database.db', timeout=10)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    res = cur.execute('SELECT * FROM clients ORDER BY abbreviation')
    clients = res.fetchall() 
    con.commit()
    con.close()

    return [dict(client) for client in clients]

@app.route("/new_client", methods=['POST'])
def new_client():
    data = request.json
    con = sqlite3.connect('database.db', timeout=10)
    cur = con.cursor()
    res = cur.execute(f'SELECT * FROM clients WHERE abbreviation = "{data["abbreviation"]}"')
    client = res.fetchone()

    if client:
        con.close()
        return f"Client with abbreviation {data['abbreviation']} already exists!", 403

    if not data['latitude'] and not data['longitude']:
        try:
            try_coords = geolocate_address(f"{data['address']} {data['city']} {data['zip_code']}")
            data['latitude'] = try_coords[0]
            data['longitude'] = try_coords[1]
        except:
            pass

    cur.execute(f'INSERT INTO clients (abbreviation, name, address, city, state, zip_code, latitude, longitude, server, ipv4) VALUES ("{data["abbreviation"]}", "{data["name"]}", "{data["address"]}", "{data["city"]}", "{data["state"]}", {int(data["zip_code"])}, "{data["latitude"]}", "{data["longitude"]}", {int(data["server"])}, "{data["ipv4"]}")')
    con.commit()
    con.close()
    return "", 200

@app.route('/edit_client', methods=['POST'])
def edit_client():
    data = request.json
    con = sqlite3.connect('database.db', timeout=10)
    cur = con.cursor()
    cur.execute(f'UPDATE clients SET name = "{data["name"]}", address = "{data["address"]}", city = "{data["city"]}", state = "{data["state"]}", zip_code = {data["zip_code"]}, latitude = {data["latitude"]}, longitude = {data["longitude"]}, server = {data["server"] if data["server"] else "NULL"}, ipv4 = "{data["ipv4"]}" WHERE abbreviation = "{data["id"]}"')
    con.commit()
    con.close()
    return "", 200

@app.route("/delete_client", methods=['DELETE'])
def delete_client():
    data = request.json
    con = sqlite3.connect('database.db', timeout=10)
    cur = con.cursor()
    cur.execute(f'DELETE FROM clients WHERE abbreviation = "{data["abbreviation"]}"')
    con.commit()
    con.close()
    return "", 200

def check_servers(clients):
    map = {}
    for client in clients:
        if client['server']:
            map[client['abbreviation']] = client['server']

    return api.kaseya.get_agents_online(map) 

@app.route("/check_alerts", methods=['POST'])
def check_alerts():
    alerts = {}

    con = sqlite3.connect('database.db', timeout=10)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    res = cur.execute('SELECT abbreviation, server, ipv4 FROM clients')
    clients = res.fetchall()
    con.commit()
    con.close()

    servers = check_servers(clients)
    for server in servers:
        if servers[server] == 0:
            alerts[server] = "Server Down"
            print(f"Alert: Server is down for {server}")

    networks = get_cache('ruon/agents.json', timedelta(minutes = 1), api.ruon.get_agents)

    networks_new = {}
    for d in networks.values():
        networks_new[d['IP']] = d['Severity']
        
    for client in clients:
        if client['ipv4'] in networks_new:
            if networks_new[client['ipv4']] != "Okay":
                alerts[client['abbreviation']] = "Network Down"
                print(f"Alert: Network is down for {client['abbreviation']}")

    return alerts, 200

# main dashboard
@app.route("/")
def index():
    all_tickets = api.mojo.get_tickets()
    jobs = api.comet.get_jobs()
    jobs_statuses = api.comet.get_jobs_status(jobs)
    device_counts = get_cache('comet/counts.json', timedelta(minutes = 10), api.comet.counts)
    ruon_agents = get_cache('ruon/agents.json', timedelta(minutes = 1), api.ruon.get_agents)

    open_tickets = []
    unassigned_tickets = []
    hd_tickets = []
    project_tickets = []
    internalproject_tickets = []
    activehd_tickets = []
    
    created_7d = 0
    closed_7d = 0

    for ticket in all_tickets.values():
        if ticket['status_id'] < 60:
            open_tickets.append(ticket)

            if not ticket['assigned_to_id']:
                unassigned_tickets.append(ticket)

            if ticket['ticket_queue_id'] == 162232:
                hd_tickets.append(ticket)
                if ticket['status_id'] == 10:
                    activehd_tickets.append(ticket)

            if ticket['ticket_queue_id'] == 175427:
                project_tickets.append(ticket)

            if ticket['ticket_queue_id'] == 173389:
                internalproject_tickets.append(ticket)

        # if ticket was created in the last week
        if (datetime.now(timezone.utc) - datetime.fromisoformat(ticket['created_on'] or '1970-01-01T12:00:00Z')) < timedelta(days=7):
            created_7d += 1
        # if ticket was closed in the last week
        if (datetime.now(timezone.utc) - datetime.fromisoformat(ticket['closed_on'] or '1970-01-01T12:00:00Z')) < timedelta(days=7):
            closed_7d += 1

    try:
        kill_ratio = round(closed_7d/created_7d, 2)
    except:
        kill_ratio = closed_7d

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
            # date = datetime.fromisoformat(incident['closed_at'] or '1970-01-01T12:00:00Z')
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
        ruon_agent_status = ruon_agents[agent]['Severity']
        ruon_statuses[ruon_agent_status] += 1

    dnsfilter_numbers_2h = get_cache('dnsfilter/total_stats_2.json', timedelta(minutes=10), api.dnsfilter._get_total_stats, (2))
    dnsfilter_numbers_24h = get_cache('dnsfilter/total_stats_24.json', timedelta(minutes=10), api.dnsfilter._get_total_stats, (24))
    dnsfilter_top5_2h = api.dnsfilter.get_most_threats(5, 2)
    dnsfilter_top5_24h = api.dnsfilter.get_most_threats(5, 24)

    return render_template("html/index.html",
        open_tickets=len(open_tickets),
        unassigned_tickets=len(unassigned_tickets),
        hd_tickets=len(hd_tickets),
        project_tickets=len(project_tickets),
        internalproject_tickets=len(internalproject_tickets),
        activehd_tickets=len(activehd_tickets),
        kill_ratio=kill_ratio,
        all_agents=json.dumps(agents),
        inactive_agents=len(inactive_agents),
        ood_agents=len(ood_agents),
        critical_agents=len(critical_agents),
        recent_alarms=len(recent_alarms),
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
    app.run(host="0.0.0.0", port="5000", debug=True)