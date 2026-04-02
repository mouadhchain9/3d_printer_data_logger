import octoprint.plugin
import paho.mqtt.publish as publish
import json

class MotionMqttPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.TemplatePlugin
):

    def on_after_startup(self):
        self._logger.info("Motion MQTT Plugin started")
        self.last = {"x": 0, "y": 0, "z": 0, "e": 0, "f": 0, "cmdIndex": 0}
        self.cmd_index = 0

    def gcode_sent(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        # We only count motion commands to match the Digital Shadow's parsed move list
        # We must count the EXACT same commands as GCodeLoader.js to keep pointers in sync
        # Indexable commands: G0, G1, G2, G3, G4, G28, G92
        if cmd.startswith(("G0", "G1", "G2", "G3", "G4", "G28", "G92")):
            self.cmd_index += 1
            self.last["cmdIndex"] = self.cmd_index
            self.last["is_extruding"] = ("E" in cmd and (cmd.startswith("G1") or "X" in cmd or "Y" in cmd))

        # ==========================
        # HANDLE EXTRUSION RESET (G92 E...)
        # ==========================
        if cmd.startswith("G92") and "E" in cmd:
            try:
                for p in cmd.split():
                    if p.startswith("E"):
                        self.last["e"] = float(p[1:])
                        self._logger.info(f"E RESET → {self.last['e']}")
            except:
                pass
            return

        # ==========================
        # ONLY HANDLE MOVEMENT
        # ==========================
        if not (cmd.startswith("G1") or cmd.startswith("G0")):
            return

        parts = cmd.split()
        updated = False

        for p in parts:
            try:
                if p.startswith("X"):
                    self.last["x"] = float(p[1:])
                    updated = True
                elif p.startswith("Y"):
                    self.last["y"] = float(p[1:])
                    updated = True
                elif p.startswith("Z"):
                    self.last["z"] = float(p[1:])
                    updated = True
                elif p.startswith("E"):
                    self.last["e"] = float(p[1:])
                    updated = True
                elif p.startswith("F"):
                    self.last["f"] = float(p[1:])
                    updated = True
            except:
                pass

        # ==========================
        # PUBLISH
        # ==========================
        if updated:
            try:
                publish.single(
                    "octoPrint/motion",
                    json.dumps(self.last),
                    hostname="localhost",
                    port=1883
                )
            except Exception as e:
                self._logger.error(f"MQTT publish failed: {e}")


__plugin_name__ = "Motion MQTT Plugin"
__plugin_implementation__ = MotionMqttPlugin()

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = MotionMqttPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.comm.protocol.gcode.sent": __plugin_implementation__.gcode_sent
    }
