import machine
import dht
import time
import ujson
import ssd1306
from umqttsimple import MQTTClient
import dotenv

# Load do .env
env = dotenv.load()

# --- Configurações MQTT ---
MQTT_CLIENT_ID = env.get("MQTT_CLIENT_ID", "esp32_simulador_m2")
MQTT_BROKER    = env.get("MQTT_BROKER", "broker.hivemq.com")
MQTT_USER      = env.get("MQTT_USER", "admin")
MQTT_PASSWORD  = env.get("MQTT_PASSWORD", "password")
MQTT_PORT      = 8883

TOPIC_PUB_SENSORES  = b"projeto_m2/coragi/sensores"
TOPIC_SUB_ATUADORES = b"projeto_m2/coragi/atuadores/#"

# --- Configuração dos Pinos ---
sensor_dht = dht.DHT22(machine.Pin(15))
sensor_ldr = machine.ADC(machine.Pin(34))
sensor_ldr.init(atten=machine.ADC.ATTN_11DB)
sensor_pir = machine.Pin(13, machine.Pin.IN)
sensor_pot = machine.ADC(machine.Pin(35))
sensor_pot.init(atten=machine.ADC.ATTN_11DB)

led = machine.Pin(2, machine.Pin.OUT)
rele = machine.Pin(4, machine.Pin.OUT)
servo = machine.PWM(machine.Pin(18), freq=50)

i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# --- Funções Auxiliares ---
def mover_servo(angulo):
    duty = int(((angulo / 180) * 75) + 40)
    servo.duty(duty)

def atualizar_display(temp, umid, luz, movimento):
    oled.fill(0)
    oled.text("Automacao M2", 16, 0)
    oled.text("----------------", 0, 10)
    oled.text(f"Temp: {temp}C", 0, 22)
    oled.text(f"Umid: {umid}%", 0, 32)
    oled.text(f"Luz:  {luz}", 0, 42)
    status_mov = "ALERTA!" if movimento else "Seguro"
    oled.text(f"Mov:  {status_mov}", 0, 52)
    oled.show()

# --- Callback MQTT (Recebimento de Mensagens) ---
def sub_cb(topic, msg):
    print((b"Mensagem recebida no topico %s: %s" % (topic, msg)).decode('utf-8'))
    
    # Decodifica a mensagem para string
    t = topic.decode('utf-8')
    m = msg.decode('utf-8')

    # Lógica de acionamento independente
    if t == "projeto_m2/coragi/atuadores/led":
        led.value(1 if m == "ON" else 0)
    elif t == "projeto_m2/coragi/atuadores/rele":
        rele.value(1 if m == "ON" else 0)
    elif t == "projeto_m2/coragi/atuadores/servo":
        mover_servo(90 if m == "OPEN" else 0)

# --- Conexão MQTT ---
def conectar_mqtt():
    print(f"Conectando ao cluster HiveMQ Cloud em {MQTT_BROKER}...")
    
    client = MQTTClient(
        client_id=MQTT_CLIENT_ID, 
        server=MQTT_BROKER, 
        port=MQTT_PORT, 
        user=MQTT_USER, 
        password=MQTT_PASSWORD, 
        keepalive=60,
        ssl=True, 
        ssl_params={'server_hostname': MQTT_BROKER}
    )
    
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(TOPIC_SUB_ATUADORES)
    print("Conexão segura estabelecida com sucesso!")
    return client

# Inicializa Cliente MQTT
try:
    client = conectar_mqtt()
except OSError as e:
    print("Falha ao conectar no MQTT. Reiniciando...", e)
    machine.reset()

print("Iniciando loop principal...")

ultimo_envio = time.ticks_ms()
intervalo_envio = 5000  # Envia dados a cada 5 segundos para não floodar o broker

while True:
    try:
        # Verifica se há mensagens novas no tópico assinado de forma não-bloqueante
        client.check_msg()

        # Controle de tempo para leitura e publicação
        if time.ticks_diff(time.ticks_ms(), ultimo_envio) > intervalo_envio:
            sensor_dht.measure()
            temp = sensor_dht.temperature()
            umid = sensor_dht.humidity()
            luz = sensor_ldr.read()
            nivel = sensor_pot.read()
            mov = sensor_pir.value()

            atualizar_display(temp, umid, luz, mov)

            # Monta o payload JSON
            payload = ujson.dumps({
                "temperatura": temp,
                "umidade": umid,
                "luminosidade": luz,
                "nivel": nivel,
                "movimento": mov
            })

            # Publica no broker
            print(f"Publicando sensores: {payload}")
            client.publish(TOPIC_PUB_SENSORES, payload)
            
            ultimo_envio = time.ticks_ms()

        time.sleep(0.1) # Pequeno delay para aliviar a CPU

    except OSError as e:
        print("Erro no loop principal:", e)
        time.sleep(2)