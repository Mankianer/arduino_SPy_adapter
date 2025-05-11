from traceback import print_exception

import serial
import serial.tools.list_ports
import threading
import time
from pathlib import Path
import play_sounds

DEFAULT_SONG: Path = Path("sound.mp3")
READY_SOUND: Path = Path("ready.mp3")
TEAM_SOUND: Path = Path("team_#t#.mp3")

# ⇢ optional Cache, damit die Thread-Objekte nicht vom GC gefressen werden
_play_threads: list[threading.Thread] = []


def play_sound(file: Path) -> threading.Thread:
    """
    Plays the given sound *asynchronously* in a background daemon thread
    and returns immediately.

    Parameters
    ----------
    file : Path
        Path to the audio file.

    Returns
    -------
    threading.Thread
        The thread that runs ``play_sounds.play_file`` – useful if you ever
        want to ``join()`` it or inspect ``exc_info()``.

    Notes
    -----
    * Because the thread is started with ``daemon=True``, it won’t prevent
      your program from exiting.
    * If you need to wait later, just keep the returned object:
        >>> t = play_sound(READY_SOUND)
        >>> # … do other work …
        >>> t.join()          # blocks until playback is done
    """
    t = threading.Thread(
        target=play_sounds.play_file,
        args=(file,),
        name=f"sound-player-{len(_play_threads)}",
        daemon=True,
    )
    t.start()
    _play_threads.append(t)           # keep a reference, optional
    return t


def find_arduino_port():
    """
    Durchsucht alle verfügbaren Ports nach Hinweisen auf einen Arduino.
    Auf Windows taucht oft "Arduino" in der Beschreibung auf.
    Unter macOS können auch Geräte mit 'tty.usbmodem' oder 'tty.usbserial' vorkommen.
    """
    # return 'COM6'
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Prüfe, ob "Arduino" in der Beschreibung vorkommt
        print("prüfe ob USB Geräte passt:", port.device, port.description)
        if "Arduino" in port.description or "Serielles" in port.description or "SERIAL" in port.description:
            print("Arduino gefunden:", port.device)
            return port.device
        # Zusätzliche Prüfungen für macOS:
        if "tty.usbmodem" in port.device or "tty.usbserial" in port.device:
            print("Arduino gefunden:", port.device)
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
            ser = serial.Serial(ardo_port, 115200, timeout=1)
            success = True
        except serial.SerialException:
            print(f"Arduino(${ardo_port}) Verbindungsfehler. Überprüfe die Verbindung... Versuche es gleich erneut.")
            success = False
        if not success:
            time.sleep(3)


    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            print("==>", line)
            # Beispielbedingung: Bei bestimmten Befehlen wird der entsprechende Sound abgespielt
            if "Play Ready Sound" in line:
                play_sound(READY_SOUND)
                print("\tReady")
            elif "Play Team Sound#" in line:
                # Extrahiere den String nach "Play Team Sound#" und vor dem nächsten '#'
                team_name = line.split('#')[1]
                team_sound = Path(str(TEAM_SOUND).replace("#t#", team_name))
                play_sound(team_sound)
                print("\tSpieler:", team_name)



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

