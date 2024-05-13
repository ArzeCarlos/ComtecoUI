import subprocess
import time
import random
from paho.mqtt import client as mqtt_client_module

#---------------CONEXION MQTT
broker = 'localhost'
port = 1883
topic = "conexion"
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'admin'
password = 'public'
#---------------FIN CONEXION MQTT

def connect_mqtt() -> mqtt_client_module.Client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client_module.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def check_connection(hostname):
    try:
        ping_process = subprocess.Popen(['ping', '-n', '1', hostname], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = ping_process.communicate()
        if "Tiempo de espera agotado para esta solicitud." in output:
            return 0
        elif "Host de destino inaccesible" in output:
            return 0
        else:
            return 1
    except Exception as e:
        print(f"Error: {e}")
        return 0

if __name__ == "__main__":
    mqtt_client = connect_mqtt()
    mqtt_client.loop_start()  # Inicia el loop de MQTTv

    hostname = "192.168.3.38"  # Cambia esto a la IP que deseas comprobar
    while True:
        respuesta = check_connection(hostname)
        print("[{}]".format(respuesta))
        mqtt_client.publish(topic, payload="[{}]".format(respuesta))
        time.sleep(2)  # Espera 2 segundos antes de realizar el próximo ping
