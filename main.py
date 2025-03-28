from traceback import print_exception

import serial
import vlc
import time


# VLC-Instanz erstellen und Player konfigurieren
instance = vlc.Instance()

# media = instance.media_new('sound.ogg')  # Pfad zur Sounddatei anpassen
# player.set_media(media)

def play_sound():
    player = vlc.MediaPlayer('file:///sound.ogg')
    player.play()

    time.sleep(5)

def find_arduino_port():
    """
    Durchsucht alle verfügbaren seriellen Ports und gibt den Port zurück, der höchstwahrscheinlich
    zu einem Arduino gehört.
    """
    return "COM3"
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        # Print port info
        print(port.device, port.name, port.description)
        # Prüfe, ob "Arduino" in der Beschreibung enthalten ist oder typische Portnamen vorliegen.
        if "Arduino" in port.description or "ttyACM" in port.device or "ttyUSB" in port.device:
            return port.device
    return None

def main():
    # Stelle sicher, dass der richtige Port und die Baudrate eingestellt sind
    # Windows: z.B. 'COM3', Linux: z.B. '/dev/ttyACM0'
    success = False
    while not success:
        ardo_port = find_arduino_port()
        if ardo_port is None:
            print("Arduino nicht gefunden. Überprüfe die Verbindung... Versuche es gleich erneut.")
            time.sleep(3)
            continue
        try:
            ser = serial.Serial('COM3', 9600, timeout=1)
            success = True
        except serial.SerialException:
            print(f"Arduino(${ardo_port}) Verbindungsfehler. Überprüfe die Verbindung... Versuche es gleich erneut.")
            success = False
        if not success:
            time.sleep(3)


    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            print("Arduino sagt:", line)
            # Beispielbedingung: Bei "play_sound" wird der Sound abgespielt
            if "play_sound" in line:
                play_sound()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            print("Kritischer Fehler:", e)
            print("starte neu...")
            time.sleep(1)

    # player = vlc.MediaPlayer('file:///sound.ogg')
    # state = player.get_state()
    # print("Player state:", state)
    # player.play()
    # time.sleep(1)
    # player = vlc.MediaPlayer('file:///sound.ogg')
    # player.play()
    # time.sleep(1)
    # state = player.get_state()
    # print("Player state:", state, player.is_playing())

