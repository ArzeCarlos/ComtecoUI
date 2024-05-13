import tkinter
import tkinter.messagebox
import json
import random
import sys
import os
import customtkinter
import webbrowser
import subprocess
from paho.mqtt import client as mqtt_client
"""MQTT Parameters"""
broker = '192.168.3.101'
port = 1883
topic = "topic/1"
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'Luis Perez'
password = 'SisComIII'
x1=0
x2=0
x3=0
x4=0
x5=0
x6=0
x7=0
x8=0
x9=0
x10=0
x0=0
"""MQTT CONNECT"""
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    #client.subscribe("testtopic/1", qos=0, retain=False)
    return client
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global x1,x2,x3,x4,x5,x6,x7,x8,x9,x10, x0, ip1
        y=msg.payload.decode()
        print(y)
        y1=json.loads(y)
        '''x1=round(float(y1["VAC1"]),2)
        x2=round(float(y1["VAC2"]),2)
        x3=round(float(y1["VDC1"]),2)
        x4=round(float(y1["VDC2"]),2)
        x5=round(float(y1["TEMP"]),2)
        x6=round(float(y1["HUM"]),2)
        x7=y1["DOOR1"]
        x8=y1["DOOR2"]
        x9=y1["ALAR"]
        x10=y1["AL_Bocina"]'''

        x1=y1["VAC1"]
        x2=y1["VAC2"]
        x3=y1["VDC1"]
        x4=y1["VDC2"]
        x5=y1["TEMP"]
        x6=y1["HUM"]
        x7=y1["DOOR1"]
        x8=y1["DOOR2"]
        x9=y1["ALAR"]
        x10=y1["AL_Bocina"]
        x0=y1["EA"]
        ip1=y1["IP"]
        print(x1)
        print(x2)
        print(x3)
        print(x4)
        print(x5)
        print(x6)
        print(x7)
        print(x8)
        print(x9)
        print(x10)
        print(x0)
        print(ip1)
    client.subscribe(topic)
    client.on_message = on_message

customtkinter.set_appearance_mode("#025480")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"
'''Function'''
def publish():
        client = connect_mqtt()
        msg_count=appentry.get()
        result = client.publish(topic, msg_count)
        status = result[0]
        if status == 0:
            print(f"Send `{msg_count}` to topic `{topic}`")
            restart_program()
        else:
            print(f"Failed to send message to topic {topic}")  
def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, * sys.argv)
def appchange_appearance_mode_event(app, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

#CamaraIp
def abrir_CamIP():
    IPAddressCam=appentry2.get()
    webbrowser.open("http://"+IPAddressCam)

#Abrir Menu
def abrir_programa_secundario(programa):
    subprocess.Popen(["py", programa], shell=True)
    #root.withdraw()
    app.destroy()
    sys.exit()

app = customtkinter.CTk()
app.title("Communications systems III")
app.geometry(f"{1100}x{580}")
app.grid_columnconfigure(1, weight=1)
app.grid_columnconfigure((2, 3), weight=1)
app.grid_rowconfigure((0, 1, 2), weight=1)
appsidebar_frame = customtkinter.CTkFrame(app, width=20, corner_radius=0)
appsidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
appsidebar_frame.grid_rowconfigure(4, weight=1)
applogo_label = customtkinter.CTkLabel(appsidebar_frame, text="Wireless Monitoring", font=customtkinter.CTkFont(size=20, weight="bold"))
applogo_label.grid(row=0, column=0, padx=10, pady=(0,0))
applogo_label2 = customtkinter.CTkLabel(appsidebar_frame, text="Base Station", font=customtkinter.CTkFont(size=20, weight="bold"))
applogo_label2.grid(row=1, column=0, padx=10, pady=(0, 0))
appentry = customtkinter.CTkEntry(app, placeholder_text="Command:")
appentry.grid(row=0, column=0, padx=10, pady=(0, 0))

appentry2 = customtkinter.CTkEntry(app, placeholder_text="Direccion camara IP")
appentry2.grid(row=1,column=0, padx=10, pady=(3,0))

#appentry2 = customtkinter.CTkEntry(app, placeholder_text="Direccion camara IP")
#appentry2.grid(row=1,column=0, padx=10, pady=(3,0))
#applbl10 = customtkinter.CTkLabel(app, text="ALARMA",font=customtkinter.CTkFont(size=20, weight="bold"))
#applbl10.grid(row=2, column=0, padx=10, pady=(6, 0), sticky="nsew")

appsidebar_button_1 = customtkinter.CTkButton(appsidebar_frame,text="Send", command=publish)
appsidebar_button_1.grid(row=6, column=0, padx=10, pady=(0, 0))
applbl1 = customtkinter.CTkLabel(app, text="VAC1", font=customtkinter.CTkFont(size=20, weight="bold"))
applbl1.grid(row=0, column=1, padx=(3, 0), pady=(3, 0), sticky="nsew")
applbl2 = customtkinter.CTkLabel(app, text="VAC2",font=customtkinter.CTkFont(size=20, weight="bold"),)
applbl2.grid(row=0, column=2, padx=(3, 0), pady=(3, 0), sticky="nsew")
applbl3 = customtkinter.CTkLabel(app, text="VDC1", font=customtkinter.CTkFont(size=20, weight="bold"))
applbl3.grid(row=0, column=3, padx=(3, 0), pady=(3, 0), sticky="nsew")
applbl4 = customtkinter.CTkLabel(app, text="VDC2", font=customtkinter.CTkFont(size=20, weight="bold"))
applbl4.grid(row=1, column=1, padx=(3, 0), pady=(3, 0), sticky="nsew")
applbl5 = customtkinter.CTkLabel(app, text="Temp",font=customtkinter.CTkFont(size=20, weight="bold"))
applbl5.grid(row=1, column=2, padx=(3, 0), pady=(3, 0), sticky="nsew")
applbl6 = customtkinter.CTkLabel(app, text="Hum",font=customtkinter.CTkFont(size=20, weight="bold"))
applbl6.grid(row=1, column=3, padx=(3, 0), pady=(3, 0), sticky="nsew")
applbl7 = customtkinter.CTkLabel(app, text="Door1",font=customtkinter.CTkFont(size=20, weight="bold"))
applbl7.grid(row=2, column=1, padx=(3, 0), pady=(3, 0), sticky="nsew")
applbl8 = customtkinter.CTkLabel(app, text="Door2",font=customtkinter.CTkFont(size=20, weight="bold"))
applbl8.grid(row=2, column=2, padx=(3, 0), pady=(3, 0), sticky="nsew")
applbl9 = customtkinter.CTkLabel(app, text="AL_Bocina",font=customtkinter.CTkFont(size=20, weight="bold"))
applbl9.grid(row=2, column=3, padx=(3, 0), pady=(3, 0), sticky="nsew")
applbl10 = customtkinter.CTkLabel(app, text="EA",font=customtkinter.CTkFont(size=20, weight="bold"))
applbl10.grid(row=3, column=1, padx=(3, 0), pady=(3, 0), sticky="nsew")

boton_IP = customtkinter.CTkButton(app, text="Abrir Camara IP", command=abrir_CamIP)
boton_IP.grid(row=3,column=2, padx=1, pady=(3, 0))

volver_menu = customtkinter.CTkButton(app, text="Volver Menu", command=lambda: abrir_programa_secundario("Oficial.py"))
volver_menu.grid(row=3,column=3, padx=1, pady=(4, 0))


client = connect_mqtt()
subscribe(client)
if __name__ == "__main__":
        while(1):
            client.loop_start()
            app.update()
            applbl1.configure(text=f"VAC1: {x1}[V]")
            applbl2.configure(text=f"VAC2: {x2}[V]")
            applbl3.configure(text=f"VDC1: {x3}[V]")
            applbl4.configure(text=f"VDC2: {x4}[V]")
            applbl5.configure(text=f"TEMP: {x5}°C")
            applbl6.configure(text=f"HUM: {x6}%")
            applbl7.configure(text=f"DOOR1:{x7}")
            applbl8.configure(text=f"DOOR2:{x8}")
            applbl9.configure(text=f"AL_Bocina:{x10}")
            applbl10.configure(text=f"EA:{x0}")
            client.loop_stop()
            
            