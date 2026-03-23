import sqlite3
import json
import time
import paho.mqtt.client as mqtt

# ==========================
# DB SETUP
# ==========================
conn = sqlite3.connect("telemetry.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL,
    x REAL, y REAL, z REAL, e REAL, f REAL,
    nozzle_actual REAL, nozzle_target REAL,
    bed_actual REAL, bed_target REAL,
    progress REAL,
    state TEXT
)
""")

conn.commit()

# ==========================
# STATE CACHE (merge data)
# ==========================
state = {
    "x": None, "y": None, "z": None, "e": None, "f": None,
    "nozzle_actual": None, "nozzle_target": None,
    "bed_actual": None, "bed_target": None,
    "progress": None,
    "state": None
}

# ==========================
# MQTT CALLBACK
# ==========================
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT")
    client.subscribe("octoPrint/#")

def on_message(client, userdata, msg):
    global state

    try:
        data = json.loads(msg.payload.decode())
    except:
        return

    topic = msg.topic

    # ======================
    # UPDATE STATE
    # ======================
    if topic == "octoPrint/motion":
        state.update({
            "x": data.get("x"),
            "y": data.get("y"),
            "z": data.get("z"),
            "e": data.get("e"),
            "f": data.get("f"),
        })

    elif topic == "octoPrint/temperature/tool0":
        state.update({
            "nozzle_actual": data.get("actual"),
            "nozzle_target": data.get("target"),
        })

    elif topic == "octoPrint/temperature/bed":
        state.update({
            "bed_actual": data.get("actual"),
            "bed_target": data.get("target"),
        })

    elif topic == "octoPrint/progress/printing":
        state["progress"] = data.get("progress")

    elif topic == "octoPrint/event/PrinterStateChanged":
        state["state"] = data.get("state_string")

    # ======================
    # STORE SNAPSHOT
    # ======================
    cursor.execute("""
        INSERT INTO telemetry (
            timestamp,
            x, y, z, e, f,
            nozzle_actual, nozzle_target,
            bed_actual, bed_target,
            progress, state
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        time.time(),
        state["x"], state["y"], state["z"], state["e"], state["f"],
        state["nozzle_actual"], state["nozzle_target"],
        state["bed_actual"], state["bed_target"],
        state["progress"], state["state"]
    ))

    conn.commit()

    print("Saved:", state)


# ==========================
# MQTT CLIENT
# ==========================
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_forever()
