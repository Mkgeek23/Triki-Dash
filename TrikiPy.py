import asyncio
import struct
from dataclasses import dataclass
from bleak import BleakScanner, BleakClient


@dataclass
class TrikiData:
    ax: int
    ay: int
    az: int
    gx: int
    gy: int
    gz: int


class TrikiDevice:
    # Stałe protokołu
    _DATA_HEADER = 0x22       # ramka IMU
    _BUTTON_HEADER = 0x21     # ramka przycisku
    _DATA_LEN = 14            # 2 (nagłówek+status) + 6*int16
    _BUTTON_LEN = 5

    def __init__(self, BTName: str = "Triki", literal: bool = False):
        self.BTName = BTName
        self.literal = literal
        self._FirmwareVersion = None
        self._RXUUID = None
        self._TXUUID = None
        self._Name = None
        self._BATTERY_UUID = "00002a19-0000-1000-8000-00805f9b34fb"
        self._client = None
        self._data_buffer = bytearray()
        self._data_queue = asyncio.Queue()
        self._is_streaming = False
        self._button_pressed = False

    async def connectTriki(self, timeout: float = 10.0) -> bool:
        try:
            devices = await BleakScanner.discover(timeout=timeout)
            target_device = None

            for device in devices:
                if device.name:
                    if self.literal and device.name == self.BTName:
                        target_device = device
                        break
                    elif not self.literal and device.name.startswith(self.BTName):
                        target_device = device
                        break

            if not target_device:
                return False

            self._client = BleakClient(target_device.address)
            await self._client.connect()

            if not self._client.is_connected:
                return False

            for service in self._client.services:
                for char in service.characteristics:
                    if char.uuid.startswith("00002a00"):
                        val = await self._client.read_gatt_char(char.uuid)
                        self._Name = val.decode('utf-8', errors='ignore')
                    elif char.uuid.startswith("00002a26"):
                        val = await self._client.read_gatt_char(char.uuid)
                        self._FirmwareVersion = val.decode('utf-8', errors='ignore')
                    elif char.uuid.startswith("6e400002"):
                        self._RXUUID = char.uuid
                    elif char.uuid.startswith("6e400003"):
                        self._TXUUID = char.uuid

            return True

        except Exception as e:
            print(f"[Error connecting]: {e}")
            return False

    def _notification_handler(self, sender, data):
        # Dokładamy nowe bajty do bufora strumieniowego
        self._data_buffer.extend(data)

        # Ramkujemy WYŁĄCZNIE po nagłówku + długości.
        # NIE odrzucamy ramki IMU na podstawie drugiego bajtu — to bajt
        # statusu/flag (zawiera m.in. stan przycisku), który bywa != 0x00.
        max_iter = 32
        iterations = 0
        while self._data_buffer and iterations < max_iter:
            iterations += 1
            head = self._data_buffer[0]

            if head == self._DATA_HEADER:
                if len(self._data_buffer) < self._DATA_LEN:
                    break  # czekamy na resztę ramki

                packet = self._data_buffer[:self._DATA_LEN]

                # packet[1] = bajt statusu/flag. Najmłodszy bit traktujemy
                # jako stan przycisku, aby nie gubić go między ramkami 0x21.
                self._button_pressed = bool(packet[1] & 0x01)

                ax, ay, az, gx, gy, gz = struct.unpack('<hhhhhh', packet[2:14])
                self._data_queue.put_nowait(TrikiData(ax, ay, az, gx, gy, gz))

                del self._data_buffer[:self._DATA_LEN]

            elif head == self._BUTTON_HEADER:
                if len(self._data_buffer) < self._BUTTON_LEN:
                    break  # czekamy na resztę ramki

                packet = self._data_buffer[:self._BUTTON_LEN]
                self._button_pressed = bool(packet[2])

                del self._data_buffer[:self._BUTTON_LEN]

            else:
                # Nieznany bajt — przesuwamy się o 1, żeby zresynchronizować.
                self._data_buffer.pop(0)

    def isButtonPressed(self) -> bool:
        return self._button_pressed

    async def startTriki(self) -> bool:
        if not self._client or not self._client.is_connected:
            return False
        if not self._RXUUID or not self._TXUUID:
            return False

        try:
            # Czyścimy bufor, żeby nie zaczynać od resztek poprzedniej sesji
            self._data_buffer.clear()
            await self._client.start_notify(self._TXUUID, self._notification_handler)
            wake_command = b'\x20\x10\x00\xd0\x07\x34\x00\x03'
            await self._client.write_gatt_char(self._RXUUID, wake_command, response=False)
            self._is_streaming = True
            return True
        except Exception:
            return False

    async def getTrikiData(self, timeout: float = 5.0) -> TrikiData:
        if not self._is_streaming:
            raise RuntimeError("Triki is not started. Call startTriki() first.")
        return await asyncio.wait_for(self._data_queue.get(), timeout=timeout)

    async def stopTriki(self) -> bool:
        if not self._client or not self._client.is_connected:
            return False
        try:
            if self._RXUUID:
                sleep_command = b'\x20\x00\x00\x00\x00\x00\x00'
                await self._client.write_gatt_char(self._RXUUID, sleep_command, response=False)
            await asyncio.sleep(0.5)
            if self._TXUUID and self._is_streaming:
                await self._client.stop_notify(self._TXUUID)
            await self._client.disconnect()
            self._is_streaming = False
            self._button_pressed = False
            self._data_buffer.clear()
            return True
        except Exception:
            return False

    def getName(self) -> str:
        return self._Name

    def getFirmwareVersion(self) -> str:
        return self._FirmwareVersion

    async def getBatteryLevel(self) -> int:
        if not self._client or not self._client.is_connected:
            return -1
        try:
            val = await self._client.read_gatt_char(self._BATTERY_UUID)
            return int(val[0])
        except Exception:
            return -1
