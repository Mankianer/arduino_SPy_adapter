from __future__ import annotations
from traceback import print_exception

import serial
import serial.tools.list_ports
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Optional

from pydub import AudioSegment
import simpleaudio as sa

DEFAULT_SONG: Path = Path("sound.mp3")
READY_SOUND: Path = Path("ready.mp3")
TEAM_SOUND: Path = Path("team_#t#.mp3")


# single, reusable worker-pool → kein Thread-Spam
_executor: ThreadPoolExecutor | None = None

def _get_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None or _executor._shutdown:
        _executor = ThreadPoolExecutor(
            max_workers=4,              # parallel Streams ≙ max Threads
            thread_name_prefix="sound"
        )
    return _executor

def _decode_and_play(file: Path, block: bool = True) -> sa.PlayObject:
    """Lädt eine Audiodatei (alle FFmpeg-Formate) und spielt sie ab."""
    seg = AudioSegment.from_file(file)           # dekodieren → PCM
    play_obj = sa.play_buffer(
        seg.raw_data,
        num_channels=seg.channels,
        bytes_per_sample=seg.sample_width,
        sample_rate=seg.frame_rate,
    )
    if block:
        play_obj.wait_done()                     # optionale Blockade
    return play_obj

def play_sound(file: Path, wait: bool = False) -> Future | sa.PlayObject:
    """
    Spielt *file* asynchron.
    - Ist `wait=True`, wird *blocking* im aktuellen Thread abgespielt.
    - Sonst wird der Job im Pool ausgeführt und es gibt sofort ein `Future`
      zurück; Exceptions landen sauber in `future.result()`.
    """
    if wait:
        return _decode_and_play(file, block=True)
    # Fire-and-forget im Worker-Thread
    return _get_executor().submit(_decode_and_play, file, False)


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

