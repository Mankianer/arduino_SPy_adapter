from traceback import print_exception

import serial
import serial.tools.list_ports
import time
from pathlib import Path
import play_sounds

DEFAULT_SONG: Path = Path("sound.mp3")

def play_sound():
    # playsound.playsound('sound.mp3')
    play_sounds.play_file(DEFAULT_SONG)


def find_arduino_port():
    """
    Durchsucht alle verfügbaren Ports nach Hinweisen auf einen Arduino.
    Auf Windows taucht oft "Arduino" in der Beschreibung auf.
    Unter macOS können auch Geräte mit 'tty.usbmodem' oder 'tty.usbserial' vorkommen.
    """
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Prüfe, ob "Arduino" in der Beschreibung vorkommt
        if "Arduino" in port.description or "Serielles" in port.description:
            return port.device
        # Zusätzliche Prüfungen für macOS:
        if "tty.usbmodem" in port.device or "tty.usbserial" in port.device:
            return port.device
    return None

def main():
    # Stelle sicher, dass der richtige Port und die Baudrate eingestellt sind
    # Windows: z.B. 'COM3', Linux: z.B. '/dev/ttyACM0'
    success = False
    while not success:
        print("Suche nach Arduino...")
        ardo_port = find_arduino_port()
        if ardo_port is None:
            print("Arduino nicht gefunden. Überprüfe die Verbindung... Versuche es gleich erneut.")
            time.sleep(3)
            continue
        try:
            ser = serial.Serial(ardo_port, 9600, timeout=1)
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
                time.sleep(10)
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

