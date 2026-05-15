import network
import time

print("Conectando ao Wi-Fi virtual do Wokwi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Wokwi-GUEST', '')

while not wlan.isconnected():
    time.sleep(0.5)
    print(".", end="")

print("\nConectado com sucesso!")
print("Configuração de rede:", wlan.ifconfig())