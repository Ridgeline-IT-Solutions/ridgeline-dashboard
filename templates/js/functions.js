const states = [
    { name: 'Alabama', abbrev: 'AL' },
    { name: 'Alaska', abbrev: 'AK' },
    { name: 'Arizona', abbrev: 'AZ' },
    { name: 'Arkansas', abbrev: 'AR' },
    { name: 'California', abbrev: 'CA' },
    { name: 'Colorado', abbrev: 'CO' },
    { name: 'Connecticut', abbrev: 'CT' },
    { name: 'Delaware', abbrev: 'DE' },
    { name: 'Florida', abbrev: 'FL' },
    { name: 'Georgia', abbrev: 'GA' },
    { name: 'Hawaii', abbrev: 'HI' },
    { name: 'Idaho', abbrev: 'ID' },
    { name: 'Illinois', abbrev: 'IL' },
    { name: 'Indiana', abbrev: 'IN' },
    { name: 'Iowa', abbrev: 'IA' },
    { name: 'Kansas', abbrev: 'KS' },
    { name: 'Kentucky', abbrev: 'KY' },
    { name: 'Louisiana', abbrev: 'LA' },
    { name: 'Maine', abbrev: 'ME' },
    { name: 'Maryland', abbrev: 'MD' },
    { name: 'Massachusetts', abbrev: 'MA' },
    { name: 'Michigan', abbrev: 'MI' },
    { name: 'Minnesota', abbrev: 'MN' },
    { name: 'Mississippi', abbrev: 'MS' },
    { name: 'Missouri', abbrev: 'MO' },
    { name: 'Montana', abbrev: 'MT' },
    { name: 'Nebraska', abbrev: 'NE' },
    { name: 'Nevada', abbrev: 'NV' },
    { name: 'New Hampshire', abbrev: 'NH' },
    { name: 'New Jersey', abbrev: 'NJ' },
    { name: 'New Mexico', abbrev: 'NM' },
    { name: 'New York', abbrev: 'NY' },
    { name: 'North Carolina', abbrev: 'NC' },
    { name: 'North Dakota', abbrev: 'ND' },
    { name: 'Ohio', abbrev: 'OH' },
    { name: 'Oklahoma', abbrev: 'OK' },
    { name: 'Oregon', abbrev: 'OR' },
    { name: 'Pennsylvania', abbrev: 'PA' },
    { name: 'Rhode Island', abbrev: 'RI' },
    { name: 'South Carolina', abbrev: 'SC' },
    { name: 'South Dakota', abbrev: 'SD' },
    { name: 'Tennessee', abbrev: 'TN' },
    { name: 'Texas', abbrev: 'TX' },
    { name: 'Utah', abbrev: 'UT' },
    { name: 'Vermont', abbrev: 'VT' },
    { name: 'Virginia', abbrev: 'VA' },
    { name: 'Washington', abbrev: 'WA' },
    { name: 'West Virginia', abbrev: 'WV' },
    { name: 'Wisconsin', abbrev: 'WI' },
    { name: 'Wyoming', abbrev: 'WY' }
];

class Client extends HTMLTableRowElement {
    idBlock = document.createElement('td');

    nameBlock = document.createElement('td');
    nameSpan = document.createElement('span');
    nameInput = document.createElement('input');

    addressBlock = document.createElement('td');
    addressSpan = document.createElement('span');
    addressInput = document.createElement('input');

    cityBlock = document.createElement('td');
    citySpan = document.createElement('span');
    cityInput = document.createElement('input');

    stateBlock = document.createElement('td');
    stateSpan = document.createElement('span');
    stateInput = document.createElement('select');

    zipBlock = document.createElement('td');
    zipSpan = document.createElement('span');
    zipInput = document.createElement('input');

    coordinatesBlock = document.createElement('td');
    coordinatesSpan = document.createElement('span');
    coordinatesInput = document.createElement('span');
    latInput = document.createElement('input');
    lonInput = document.createElement('input');

    serverBlock = document.createElement('td');
    serverSpan = document.createElement('span');
    serverInput = document.createElement('input');
    
    ipv4Block = document.createElement('td');
    ipv4Span = document.createElement('span');
    ipv4Input = document.createElement('input');

    toolsBlock = document.createElement('td');
    editButton = document.createElement('button');
    saveButton = document.createElement('button');
    deleteButton = document.createElement('button');

    constructor(id, name, address, city, state, zip_code, latitude = 0, longitude = 0, server = null, ipv4 = "") {
        super();

        this.id = id
        this.name = name
        this.address = address
        this.city = city
        this.state = state
        this.zip_code = zip_code
        this.latitude = latitude
        this.longitude = longitude
        this.server = server
        this.ipv4 = ipv4

        this.idBlock.textContent = id

        this.appendChild(this.idBlock);

        this.nameInput.style = "display: none;";
        this.nameInput.classList.add('table-input');

        this.nameBlock.appendChild(this.nameSpan);
        this.nameBlock.appendChild(this.nameInput);
        this.appendChild(this.nameBlock);

        this.addressInput.style = "display: none;";
        this.addressInput.classList.add('table-input');

        this.addressBlock.appendChild(this.addressSpan);
        this.addressBlock.appendChild(this.addressInput);
        this.appendChild(this.addressBlock);

        this.cityInput.style = "display: none;";
        this.cityInput.classList.add('table-input');

        this.cityBlock.appendChild(this.citySpan);
        this.cityBlock.appendChild(this.cityInput);
        this.appendChild(this.cityBlock);

        this.stateInput.style = "display: none;";
        this.stateInput.classList.add('table-input');

        this.stateBlock.appendChild(this.stateSpan);
        this.stateBlock.appendChild(this.stateInput);
        this.appendChild(this.stateBlock);

        for (var state of states) {
            var state_option = document.createElement('option')
            state_option.value = state['abbrev']
            state_option.textContent = state['name']
            this.stateInput.appendChild(state_option)
        }

        this.zipInput.style = "display: none;";
        this.zipInput.classList.add('table-input');
        this.zipInput.type = "number";

        this.zipBlock.appendChild(this.zipSpan);
        this.zipBlock.appendChild(this.zipInput);
        this.appendChild(this.zipBlock);

        this.coordinatesBlock.appendChild(this.coordinatesSpan);

        this.coordinatesInput.style = "display: none;";

        this.latInput.type = "number";
        this.lonInput.type = "number";
        this.latInput.classList.add('table-input');
        this.lonInput.classList.add('table-input');

        this.coordinatesInput.appendChild(this.latInput);

        var northing = document.createElement('span')
        northing.textContent = "°N"
        this.coordinatesInput.appendChild(northing)

        this.coordinatesInput.appendChild(document.createElement('br'))

        this.coordinatesInput.appendChild(this.lonInput);

        var easting = document.createElement('span')
        easting.textContent = "°E"
        this.coordinatesInput.appendChild(easting)

        this.coordinatesBlock.appendChild(this.coordinatesInput);

        this.appendChild(this.coordinatesBlock);

        this.serverInput.style = "display: none;";
        this.serverInput.classList.add('table-input');
        this.serverInput.type = "number";

        this.serverBlock.appendChild(this.serverSpan);
        this.serverBlock.appendChild(this.serverInput);
        this.appendChild(this.serverBlock);

        this.ipv4Input.style = "display: none;";
        this.ipv4Input.classList.add('table-input');

        this.ipv4Block.appendChild(this.ipv4Span);
        this.ipv4Block.appendChild(this.ipv4Input);
        this.appendChild(this.ipv4Block);

        this.editButton.classList.add('btn-edit');
        this.editButton.textContent = "Edit";
        this.editButton.onclick = this.edit;

        this.saveButton.classList.add('btn-edit');
        this.saveButton.textContent = "Save";
        this.saveButton.onclick = this.save;
        this.saveButton.style = "display: none;";

        this.deleteButton.classList.add('btn-delete');
        this.deleteButton.textContent = "Delete";
        this.deleteButton.onclick = this.delete;

        this.toolsBlock.appendChild(this.editButton);
        this.toolsBlock.appendChild(this.saveButton);
        this.toolsBlock.appendChild(this.deleteButton);

        this.toolsBlock.classList.add('td-buttons');

        this.appendChild(this.toolsBlock);

        this.updateDisplayedValues();
    }

    updateDisplayedValues() {
        this.nameSpan.textContent = this.name;
        this.addressSpan.textContent = this.address;
        this.citySpan.textContent = this.city;
        this.stateSpan.textContent = this.state;
        this.zipSpan.textContent = this.zip_code;
        var coordsset = this.latitude != "" && this.longitude != ""
        this.coordinatesSpan.textContent = coordsset ? (this.latitude + ", " + this.longitude) : "Unset";
        this.serverSpan.textContent = this.server;
        this.ipv4Span.textContent = (this.ipv4 != "") ? this.ipv4 : "000.000.000.000";
    }

    edit() {
        const client = this.parentElement.parentElement

        client.nameSpan.style = "display: none;";
        client.nameInput.style = "";
        client.addressSpan.style = "display: none;";
        client.addressInput.style = "";
        client.citySpan.style = "display: none;";
        client.cityInput.style = "";
        client.stateSpan.style = "display: none;";
        client.stateInput.style = "";
        client.zipSpan.style = "display: none;";
        client.zipInput.style = "";
        client.coordinatesSpan.style = "display: none;";
        client.coordinatesInput.style = "";
        client.serverSpan.style = "display: none;";
        client.serverInput.style = "";
        client.ipv4Span.style = "display: none;";
        client.ipv4Input.style = "";
        client.editButton.style = "display: none;";
        client.saveButton.style = "";

        client.nameInput.value = client.name;
        client.addressInput.value = client.address;
        client.cityInput.value = client.city;
        client.stateInput.value = client.state;
        client.zipInput.value = client.zip_code;
        client.latInput.value = client.latitude;
        client.lonInput.value = client.longitude;
        client.serverInput.value = client.server;
        client.ipv4Input.value = client.ipv4;
    }

    save() {
        const client = this.parentElement.parentElement

        client.nameSpan.style = "";
        client.nameInput.style = "display: none;";
        client.addressSpan.style = "";
        client.addressInput.style = "display: none;";
        client.citySpan.style = "";
        client.cityInput.style = "display: none;";
        client.stateSpan.style = "";
        client.stateInput.style = "display: none;";
        client.zipSpan.style = "";
        client.zipInput.style = "display: none;";
        client.coordinatesSpan.style = "";
        client.coordinatesInput.style = "display: none;";
        client.serverSpan.style = "";
        client.serverInput.style = "display: none;";
        client.ipv4Span.style = "";
        client.ipv4Input.style = "display: none;";
        client.editButton.style = "";
        client.saveButton.style = "display: none;";
        client.editButton.style = "";
        client.saveButton.style = "display: none;";

        if (
            client.name != client.nameInput.value ||
            client.address != client.addressInput.value ||
            client.city != client.cityInput.value ||
            client.state != client.stateInput.value ||
            client.zip_code != client.zipInput.value ||
            client.latitude != client.latInput.value ||
            client.longitude != client.lonInput.value ||
            client.server != client.serverInput.value ||
            client.ipv4 != client.ipv4Input.value
        ) {
            // only make request if either of the values actually changed
            fetch('{{ url_for("edit_client") }}', {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "id": client.id,
                    "name": client.nameInput.value,
                    "address": client.addressInput.value,
                    "city": client.cityInput.value,
                    "state": client.stateInput.value,
                    "zip_code": client.zipInput.value,
                    "latitude": client.latInput.value,
                    "longitude": client.lonInput.value,
                    "server": client.serverInput.value,
                    "ipv4": client.ipv4Input.value
                })
            })
        }

        client.name = client.nameInput.value;
        client.address = client.addressInput.value;
        client.city = client.cityInput.value;
        client.state = client.stateInput.value;
        client.zip_code = client.zipInput.value;
        client.latitude = client.latInput.value;
        client.longitude = client.lonInput.value;
        client.server = client.serverInput.value;
        client.ipv4 = client.ipv4Input.value;
        client.updateDisplayedValues();
    }

    delete() {
        const client = this.parentElement.parentElement

        if (confirm('Are you sure you wish to DELETE this client? This is irreversible!')) {
            fetch('{{ url_for("delete_client") }}', {
                method: 'DELETE',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "abbreviation": client.id
                })
            })
            knownClients.delete(client.id);
            client.remove();
        }
    }
}

customElements.define("client-tr", Client, { extends: "tr" });

const knownClients = new Map()

async function updateClients() {
    const response = await fetch('{{ url_for("get_clients") }}', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    });

    const clients = await response.json()

    for (var client of clients) {
        c = knownClients.get(client['abbreviation'])
        if (c) {
            c.name = client['name']
            c.address = client['address']
            c.city = client['city']
            c.state = client['state']
            c.zip = client['zip_code']
            c.lat = client['latitude'] ?? 0
            c.lon = client['longitude'] ?? 0
            c.server = client['server'] ?? null
            c.ipv4 = client['ipv4'] ?? ""
            c.updateDisplayedValues();
        } else {
            c = new Client(client['abbreviation'], client['name'], client['address'], client['city'], client['state'], client['zip_code'], client['latitude'] ?? 0, client['longitude'] ?? 0, client['server'] ?? null, client['ipv4'] ?? "")
            document.getElementById('client-table').appendChild(c);
            knownClients.set(client['abbreviation'], c)
        }
    }

    var deleteQueue = [];

    for (var client of knownClients) {
        if (!clients.find(c => c.abbreviation === client[0])) {
            deleteQueue.push(client[0])
            client[1].remove()
        }
    }

    for (var val of deleteQueue) {
        knownClients.delete(val);
    }

    setTimeout(updateClients, 5000);
}

// https://leafletjs.com/reference.html#icon 
outageIcon = L.icon({
    iconUrl: '{{url_for('static', filename='marker-bad.png')}}',
    iconSize: [48, 48],
    iconAnchor: [24, 45],
    popupAnchor: [0, -18]
    
});
goodIcon = L.icon({
    iconUrl: '{{url_for('static', filename='marker-good.png')}}',
    iconSize: [32, 32],
    iconAnchor: [16, 30],
    popupAnchor: [0, -12]
    
});
// https://leafletjs.com/reference.html#marker
function createMarker(coords, icon = 0) {
    if (icon == -1) {
        icon = outageIcon
    } else {
        icon = goodIcon
    }

    return L.marker(coords, {icon: icon})
}

const clientMarkers = new Map()

async function updateMap() {
    const response = await fetch('{{ url_for("check_alerts") }}', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    });

    const alerts = await response.json()
    console.log(alerts)
    for (var client of knownClients.values()) {
        m = clientMarkers.get(client.id)
        if (m) {
            map.removeLayer(m)
        }
        if (alerts[client.id]) {
            marker = createMarker([client.latitude, client.longitude], -1)
            marker.addTo(map)
            marker.bindPopup(client.name + "<br><b>" + alerts[client.id] + "</b><br><br>" + client.address + "<br>" + client.city + ", " + client.state + " " + client.zip_code)
            marker.openPopup()
            clientMarkers.set(client.id, marker)
        } else {
            marker = createMarker([client.latitude, client.longitude])
            marker.addTo(map)
            marker.bindPopup(client.name + "<br><b>No Outages</b><br><br>" + client.address + "<br>" + client.city + ", " + client.state + " " + client.zip_code)
            clientMarkers.set(client.id, marker)
        }
    }
    
    for (var marker of clientMarkers) {
        if (!knownClients.get(marker[0])) {
            console.log('Deleting ' + marker[0] + ' marker')
            clientMarkers.delete(marker[0])
            map.removeLayer(marker[1])
        }
    }

    setTimeout(updateMap, 15000);
}

async function submitClient() {
    var abbrev = document.getElementById('new-client-abbrev').value
    var name = document.getElementById('new-client-name').value
    var address = document.getElementById('new-client-address').value
    var city = document.getElementById('new-client-city').value
    var state = document.getElementById('new-client-state').value
    var zip = document.getElementById('new-client-zip').value
    var lat = document.getElementById('new-client-lat').value
    var lon = document.getElementById('new-client-lon').value
    var server = document.getElementById('new-client-server').value
    var ipv4 = document.getElementById('new-client-ipv4').value

    const response = await fetch('{{ url_for("new_client") }}', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "abbreviation": abbrev,
            "name": name,
            "address": address,
            "city": city,
            "state": state,
            "zip_code": zip,
            "latitude": lat,
            "longitude": lon,
            "server": server,
            "ipv4": ipv4
        })
    });
    if (response.status != 200) {
        alert("Error (" + response.status + ")!\n" + response.text)
    } else {
        c = new Client(abbrev, name, address, city, state, zip, lat ?? 0, lon ?? 0, server ?? 0, ipv4)
        document.getElementById('client-table').appendChild(c);
        knownClients.set(abbrev, c)
    }
}