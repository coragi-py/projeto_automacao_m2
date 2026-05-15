import machine
import dht
import time
import ssd1306

# --- Configuração dos Pinos ---
# Sensores (Entradas)
sensor_dht = dht.DHT22(machine.Pin(15))

sensor_ldr = machine.ADC(machine.Pin(34))
sensor_ldr.init(atten=machine.ADC.ATTN_11DB) 

sensor_pir = machine.Pin(13, machine.Pin.IN)

sensor_pot = machine.ADC(machine.Pin(35))
sensor_pot.init(atten=machine.ADC.ATTN_11DB)

# Atuadores (Saídas)
led = machine.Pin(2, machine.Pin.OUT)
rele = machine.Pin(4, machine.Pin.OUT)
servo = machine.PWM(machine.Pin(18), freq=50) # Servo opera em 50Hz

# Configuração do Display OLED (Comunicação I2C)
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# --- Funções Auxiliares ---
def mover_servo(angulo):
    """Converte o ângulo (0-180) para o duty cycle do servo."""
    duty = int(((angulo / 180) * 75) + 40)
    servo.duty(duty)

def atualizar_display(temp, umid, luz, movimento):
    """Atualiza o painel OLED com os dados em tempo real."""
    oled.fill(0) # Limpa a tela (fundo preto)
    oled.text("Automacao M2", 16, 0)
    oled.text("----------------", 0, 10)
    oled.text(f"Temp: {temp}C", 0, 22)
    oled.text(f"Umid: {umid}%", 0, 32)
    oled.text(f"Luz:  {luz}", 0, 42)
    
    status_mov = "ALERTA!" if movimento else "Seguro"
    oled.text(f"Mov:  {status_mov}", 0, 52)
    
    oled.show() # Renderiza as informações na tela

print("Iniciando loop de leitura e controle local...")

while True:
    try:
        # 1. Leitura dos Sensores
        sensor_dht.measure()
        temp = sensor_dht.temperature()
        umid = sensor_dht.humidity()
        
        luz = sensor_ldr.read()
        nivel = sensor_pot.read()
        mov = sensor_pir.value()

        # Print no terminal para debug
        print(f"Temp: {temp}°C | Umid: {umid}% | Luz: {luz} | Nível: {nivel} | Mov: {mov}")

        # 2. Atualiza o painel OLED
        atualizar_display(temp, umid, luz, mov)

        # 3. Teste Condicional dos Atuadores
        if luz > 2000:
            led.value(1)
        else:
            led.value(0)

        if mov == 1:
            rele.value(1)
            mover_servo(90)
        else:
            rele.value(0)
            mover_servo(0)

        time.sleep(2)

    except OSError as e:
        print("Erro na leitura do sensor:", e)
        time.sleep(2)