import asyncio
import sys
import signal
from TrikiPy import TrikiDevice

running = True

def signal_handler():
    global running
    running = False

async def main():
    global running

    triki = TrikiDevice(BTName="Triki", literal=False)

    print("Szukam kontrolera Triki...")
    success = await triki.connectTriki()
    if not success:
        print("Nie znaleziono kontrolera Triki.")
        print("Upewnij się, że:")
        print("  1. Triki jest włączony (naciśnij środek obudowy)")
        print("  2. Bluetooth jest włączony")
        print("  3. Triki nie jest połączony z telefonem")
        return

    print(f"Połączono z: {triki.getName()}")
    print(f"Wersja firmware: {triki.getFirmwareVersion()}")
    print(f"Poziom baterii: {await triki.getBatteryLevel()}%")

    if not await triki.startTriki():
        print("Nie udało się uruchomić strumienia danych.")
        return

    print("\n--- Odbieram dane z Triki ---")
    print("          AKCELEROMETR          |         ŻYROSKOP")
    print("   X      Y      Z     siła     |   X      Y      Z")
    print("-" * 55)

    try:
        while running:
            data = await triki.getTrikiData()

            ax_g = data.ax / 8192.0
            ay_g = data.ay / 8192.0
            az_g = data.az / 8192.0
            accel_force = (data.ax**2 + data.ay**2 + data.az**2) ** 0.5

            gx_dps = data.gx / 65.5
            gy_dps = data.gy / 65.5
            gz_dps = data.gz / 65.5

            print(
                f"{data.ax:6d} {data.ay:6d} {data.az:6d} {accel_force:7.0f}  |"
                f" {data.gx:6d} {data.gy:6d} {data.gz:6d}   "
                f"| {accel_force:5.0f}", end="")

            if accel_force > 20000:
                print("  POTRZĄSANIE!", end="")
            elif accel_force > 12000:
                print("  ruch dynamiczny", end="")
            elif abs(data.az) > 10000:
                print("  obrót Z", end="")
            elif abs(data.ax) > 8000 or abs(data.ay) > 8000:
                print("  przechylenie", end="")

            print()

    except asyncio.CancelledError:
        pass
    finally:
        print("\nZatrzymuję...")
        await triki.stopTriki()
        print("Rozłączono.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
