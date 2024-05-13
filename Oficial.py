import tkinter as tk
import subprocess
import sys
import os
import json
import time
import random
import threading
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta
from paho.mqtt import client as mqtt_client
from pythonping import ping
"""MQTT Parameters"""
broker = 'broker.emqx.io'
port = 1883
client_id = f'python-mqtt-1'
username = 'Luis Perez1'
password = 'SisComIII'
''' Variables globales'''
x=0
ip=0
last_update_time = ""  
last_topic1_row_index = None  
topic_list = []
subscribed_topics = []
table_data = []
topic1_active = False
def connect_mqtt() -> mqtt_client:
    """Se realiza la conexión al BROKER MQTT,posteriormente realiza 
    la lectura de un archivo JSON para la subscripción a los tópicos.
    
    Args:None
    
    Returns:None
    """
    global topic_list 
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            topics_to_subscribe = load_table_data_from_json()
            if topics_to_subscribe:
                for item in topics_to_subscribe:
                    topic = item.get('Tópicos')
                    if topic:
                        if topic not in topic_list:
                            topic_list.append(topic)
                        client.subscribe(topic)
                        print(f"Subscribed to {topic}")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client.Client(client_id)
    ##client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def check_connection(hostname):
    ''' Realiza ping periodicamente hacia una 
    IP especificada en el parámetro hostname
    
    Args:String: Contiene la IP del hostname
    
    Returns:Bool: Retorna True/False dependiendo del estado del ping
    
    '''
    try:
        response = ping(hostname, count=1)
        if response and response.success():
            return True
        else:
            return False
    except Exception as e:
        return False
def update_values(t,time,ip,alarm):
    for child in t.get_children():
        topic = t.item(child)['values'][4]  # Obtener el valor de la columna de tópicos
        if 'topic/1' in topic:
            found_topic1_row = child
            current_values = t.item(found_topic1_row)['values']
            current_values[1] = time  # Actualiza con la hora actual
            current_values[5] = ip
            time_difference = current_time - last_update_time
            if time_difference.total_seconds() > 10:
                current_values[6] = "Inactivo"
            else:
                current_values[6] = "Activo"
            t.item(found_topic1_row, values=current_values) 
            if alarm == "alarma":
                current_values[3] = "Activada"
                t.tag_configure("Red.Row", background="red")
                t.item(found_topic1_row, tags=("Red.Row",), values=current_values)
            else:
                current_values[3] = "Desactivada"
                t.tag_configure("Normal.Row", background="white")
                t.item(found_topic1_row, tags=("Normal.Row",),values=current_values)

def subscribe(client: mqtt_client):
    ''' Realiza la recepción y almacenamiento de valores, dependiendo
    del tópico
    
    Args:Type: Objeto de la clase mqtt_client
    
    Returns:None
    
    '''
    def on_message(client, userdata, msg):
        global last_topic1_row_index, topic1_active
        global last_update_time, current_time
        global last_update_time_topic2
        global last_topic2_row_index
        global x
        y = msg.payload.decode()
        if msg.topic == 'topic/1':
            y1 = json.loads(y)
            x = y1.get("ALAR", x)
            ip=y1["IP"]
            topic1_active = True
            last_update_time_str = time.strftime('%Y-%m-%d %H:%M:%S')
            last_update_time = datetime.strptime(last_update_time_str, '%Y-%m-%d %H:%M:%S')
            # Sumar 10 segundos al tiempo actual
            last_update_time += timedelta(seconds=10)
            # Obtener el tiempo actual
            current_time = datetime.now()
            found_topic1_row = None 
            root.after(1000, lambda: update_values(tree,last_update_time_str, ip,x)) 
        elif msg.topic == 'topic/2':
            y1 = json.loads(y)
            x = y1.get("ALAR", x)
            ip=y1["IP"]
            last_update_time_topic2 = time.strftime('%Y-%m-%d %H:%M:%S')
            found_topic2_row = None
        elif msg.topic == 'topic/3':
            y1 = json.loads(y)
            x = y1.get("ALAR", x)
        elif msg.topic == 'topic/4':
            y1 = json.loads(y)
            x = y1.get("ALAR", x)
    for topic in topic_list:
        client.subscribe(topic)
    client.on_message = on_message
def connect_and_subscribe(client: mqtt_client, topics_to_subscribe):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            for topic in topics_to_subscribe:
                client.subscribe(topic)
                print(f"Subscribed to {topic}")
        else:
            print("Failed to connect, return code %d\n", rc)
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
root = tk.Tk()
root.title("Tabla de Alarmas")
root.geometry("900x600")
background_image = tk.PhotoImage(file="Comteco.png")
background_label = tk.Label(root, image=background_image)
background_label.place(relwidth=1, relheight=1)
logo_image = tk.PhotoImage(file="Comteco1.png")
logo_label = tk.Label(root, image=logo_image)
logo_label.place(relx=0, rely=0, anchor='nw')
univalle_image = tk.PhotoImage(file="UNIVALLE.png")
univalle_image_resized = univalle_image.subsample(19, 19)
univalle_label = tk.Label(root, image=univalle_image_resized)
univalle_label.place(relx=1, rely=0, anchor='ne')
frame = tk.Frame(root, bg='white', bd=2)
frame.place(relx=0.5, rely=0.2, relwidth=0.8, relheight=0.6, anchor='n')
columns = ('ID', 'Hora y Fecha', 'Nombre', 'Estado de Alarma', 'Tópicos', 'IP ESP32', 'Conexión ESP32')
tree = ttk.Treeview(frame, columns=columns, show='headings')
tree.column('Hora y Fecha', width=1000)

def topic_already_exists(topic_to_check):
    for child in tree.get_children():
        topic = tree.item(child)['values'][4]
        if topic_to_check in topic:
            return True
    return False
def reconnect_and_subscribe():
        client.disconnect()
        client.reconnect()
        connect_and_subscribe(client, topic_list)
def open_add_window():
    add_window = tk.Toplevel(root)
    add_window.title("Añadir elemento")

    label_name = tk.Label(add_window, text="Nombre")
    label_name.pack()
    entry_name = tk.Entry(add_window)
    entry_name.pack()

    label_topics = tk.Label(add_window, text="Selecciona hasta 5 tópicos:")
    label_topics.pack()
    topics = ['topic/1', 'topic/2', 'topic/3', 'topic/4', 'topic/5']
    selected_topics = [] 
    def add_topic():
        selected_topic = topic_var.get()
        if len(selected_topics) < 5:
            if selected_topic in selected_topics:
                messagebox.showinfo("Alerta", f"El tópico '{selected_topic}' ya está en la lista.")
            elif any(topic == selected_topic for topic in selected_topics) or topic_already_exists(selected_topic):
                messagebox.showinfo("Alerta", f"El tópico '{selected_topic}' ya está en la lista.")
            else:
                selected_topics.append(selected_topic)
                update_listbox()
        else:
            messagebox.showinfo("Alerta", "Ya has seleccionado el máximo de tópicos permitidos.")
    def remove_topic():
        if selected_topic_listbox.curselection():
            index = selected_topic_listbox.curselection()[0]
        removed_topic = selected_topics.pop(index)
        update_listbox()

        if removed_topic in topic_list:
            topic_list.remove(removed_topic)
            print(f"El tema {removed_topic} fue eliminado de topic_list")


    def update_listbox():
        selected_topic_listbox.delete(0, tk.END)
        for topic in selected_topics:
            selected_topic_listbox.insert(tk.END, topic)

    topic_var = tk.StringVar(add_window)
    topic_var.set("Seleccionar Tópico")
    topic_dropdown = tk.OptionMenu(add_window, topic_var, *topics)
    topic_dropdown.pack()

    add_topic_button = tk.Button(add_window, text="Agregar Tópico", command=add_topic)
    add_topic_button.pack()

    remove_topic_button = tk.Button(add_window, text="Eliminar Tópico", command=remove_topic)
    remove_topic_button.pack()

    selected_topic_listbox = tk.Listbox(add_window, selectmode=tk.MULTIPLE)
    selected_topic_listbox.pack()

    add_button = tk.Button(
        add_window,
        text="Añadir",
        command=lambda: add_item(add_window, entry_name.get(), selected_topics)
    )
    add_button.pack()

def update_table_data():
    ''' Actualiza los datos de la tabla en caso de que se tenga un cambio
    
    Args:None
    
    Returns:None
    
    '''
    global table_data
    table_data = []
    for child in tree.get_children():
        values = tree.item(child)['values']
        item_data = {
            "ID": values[0],
            "Hora y Fecha": values[1],
            "Nombre": values[2],
            "Estado de Alarma": values[3],
            "Tópicos": values[4],
            "IP ESP32": values[5],
            "Conexión ESP32": values[6]
        }
        table_data.append(item_data)

def save_table_data_to_json():
    with open("table_data.json", "w") as file:
        json.dump(table_data, file)
def load_table_data_from_json():
    table_data = []
    try:
        with open("table_data.json", "r") as file:
            table_data = json.load(file)
    except FileNotFoundError:
        print("No se encontró el archivo 'table_data.json'.")
    return table_data
table_data = load_table_data_from_json()

def add_item(window, name, topics):
    global last_item_id
    if "Tópico 1" in topics and topic_already_exists("Tópico 1"):
        messagebox.showinfo("Alerta", "El 'Tópico 1' ya existe en la tabla.")
        window.destroy()
        return
    last_item_id += 1
    timestamp = "Fecha y Hora" 
    tree.insert("", "end", values=[last_item_id, timestamp, name, "", ', '.join(topics), "", "", ""])
    print("topics recibidos:", topics)
    print("topic_list ahora ", topic_list)
    for topic in topics:
        if topic not in topic_list:
            topic_list.append(topic)
            print("topic_list modificada ", topic_list)
            #print("topic", topic_list1)
        connect_and_subscribe(client, topic_list) #---comentar----**************************
        update_table_data()
    save_table_data_to_json()
    window.destroy()
def delete_item():
    if not tree.selection():
        messagebox.showinfo("Alerta", "No has seleccionado ningún elemento.")
        return

    selected_item = tree.selection()[0]
    topic_to_remove = tree.item(selected_item)['values'][4]  # Obtener el tópico asociado a la fila

    # Eliminar la fila del Treeview
    tree.delete(selected_item)

    # Eliminar el tópico específico de la lista topic_list
    if topic_to_remove in topic_list:
        topic_list.remove(topic_to_remove)
        print("Tópico eliminado:", topic_to_remove)
    else:
        print("El tópico no está en la lista:", topic_to_remove)
    
    update_table_data()
    save_table_data_to_json()

def open_edit_window():
    global edit_window

    if not tree.selection():
        messagebox.showinfo("Alerta", "No has seleccionado ningún elemento para editar.")
        return

    edit_window = tk.Toplevel(root)
    edit_window.title("Editar elemento")

    selected_item = tree.selection()[0]
    item_values = tree.item(selected_item)['values']

    label_name = tk.Label(edit_window, text="Nombre")
    label_name.pack()
    entry_name = tk.Entry(edit_window)
    entry_name.pack()
    entry_name.insert(0, item_values[2])

    label_topics = tk.Label(edit_window, text="Selecciona hasta 5 tópicos:")
    label_topics.pack()

    topics = ['topic/1', 'topic/2', 'topic/3', 'topic/4', 'topic/5']
    selected_topics = []
    def add_topic():
        selected_topic = topic_var.get()
        if len(selected_topics) < 5:
            if selected_topic in selected_topics:
                messagebox.showinfo("Alerta", f"El tópico '{selected_topic}' ya está en la lista.")
            elif any(topic == selected_topic for topic in selected_topics) or topic_already_exists(selected_topic):
                messagebox.showinfo("Alerta", f"El tópico '{selected_topic}' ya está en la lista.")
            else:
                selected_topics.append(selected_topic)
                update_listbox()
        else:
            messagebox.showinfo("Alerta", "Ya has seleccionado el máximo de tópicos permitidos.")
    def remove_topic():
        if selected_topic_listbox.curselection():
            index = selected_topic_listbox.curselection()[0]
            selected_topics.pop(index)
            update_listbox()
    def update_listbox():
        selected_topic_listbox.delete(0, tk.END)
        for topic in selected_topics:
            selected_topic_listbox.insert(tk.END, topic)

    topic_var = tk.StringVar(edit_window)
    topic_var.set("Seleccionar Tópico")
    topic_dropdown = tk.OptionMenu(edit_window, topic_var, *topics)
    topic_dropdown.pack()
    add_topic_button = tk.Button(edit_window, text="Agregar Tópico", command=add_topic)
    add_topic_button.pack()
    remove_topic_button = tk.Button(edit_window, text="Eliminar Tópico", command=remove_topic)
    remove_topic_button.pack()
    selected_topic_listbox = tk.Listbox(edit_window, selectmode=tk.MULTIPLE)
    selected_topic_listbox.pack()

    def on_select(event):
        widget = event.widget
        selected = widget.curselection()
        selected_topics.clear()
        for index in selected:
            selected_topics.append(widget.get(index))
        update_listbox()

    selected_topic_listbox.bind("<<ListboxSelect>>", on_select)
        
    def save_changes():
        new_name = entry_name.get()
        new_topics = selected_topics
    
    # Obtener los valores actuales en el elemento seleccionado
        current_values = tree.item(selected_item)['values']
    
    # Crear una lista con los valores actuales de la fila
        updated_values = list(current_values)
        updated_values[2] = new_name
    # Modificar solo la columna de tópicos
        updated_values[4] = ', '.join(new_topics)
    
        tree.item(selected_item, values=updated_values)  # Actualizar solo la fila del Treeview
        #2323
        for topic in new_topics:
            if topic not in topic_list:
                topic_list.append(topic)
        update_table_data()
        save_table_data_to_json()
        edit_window.destroy()  # Cerrar la ventana de edición después de guardar los cambios


    save_button = tk.Button(
        edit_window,
        text="Guardar cambios",
        command=save_changes
    )
    save_button.pack()


def search_item():
    search_term = search_entry.get().lower()
    if search_term:
        found = False
        for item in tree.get_children():
            values = tree.item(item, 'values')
            if any(search_term in str(value).lower() for value in values):
                tree.selection_set(item)
                tree.focus(item)
                found = True
                break
        if not found:
            messagebox.showinfo("Alerta", f"No se encontró '{search_term}' en la tabla.")
    else:
        messagebox.showinfo("Alerta", "Ingresa un nombre para buscar.")

primer_click = True
def abrir_programa(topic):
    global primer_click
    if not primer_click:
        try:
            with open("table_data.json", "r") as file:
                table_data = json.load(file)
                cargar_datos_en_tabla(table_data)
                # ...
        except FileNotFoundError:
            print("Archivo JSON no encontrado.")      
        if topic == 'topic/1':
            subprocess.Popen(["python", "main.py"])
            root.destroy()
            sys.exit()
        elif topic == 'topic/2':
            subprocess.Popen(["python", "main.py"])
        elif topic == 'topic/3':
            subprocess.Popen(["python", "main.py"])
        elif topic == 'topic/4':
            subprocess.Popen(["python", "main.py"])
    else:
        primer_click = False
def cargar_datos_en_tabla(table_data):
    for item in table_data:
        tree.insert("", "end", values=(
            item["ID"],
            item["Hora y Fecha"],
            item["Nombre"],
            item["Estado de Alarma"],
            item["Tópicos"],
            item["IP ESP32"],
            item["Conexión ESP32"]
        ))
def on_tree_click(event):
    item = tree.item(tree.focus())
    topic = item['values'][4]  
    print(topic)
    abrir_programa(topic)

table_data = load_table_data_from_json()
cargar_datos_en_tabla(table_data)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

tree.pack(side="left", fill="y")

tree_scroll = tk.Scrollbar(frame, orient="vertical", command=tree.yview)
tree_scroll.pack(side="right", fill="y")

tree.configure(yscrollcommand=tree_scroll.set)

tree.bind("<ButtonRelease-1>", on_tree_click)

add_button = tk.Button(root, text="Añadir Nodo", command=open_add_window)
add_button.place(relx=0.2, rely=0.9, relwidth=0.15, relheight=0.07)

delete_button = tk.Button(root, text="Eliminar", command=delete_item)
delete_button.place(relx=0.4, rely=0.9, relwidth=0.15, relheight=0.07)

edit_button = tk.Button(root, text="Editar", command=open_edit_window)
edit_button.place(relx=0.6, rely=0.9, relwidth=0.15, relheight=0.07)

search_entry = tk.Entry(root)
search_entry.place(relx=0.7, rely=0.14, relwidth=0.15, relheight=0.05)

search_button = tk.Button(root, text="Buscar por Nombre", command=search_item)
search_button.place(relx=0.55, rely=0.14, relwidth=0.15, relheight=0.05)


'''ping_thread = threading.Thread(target=check_connection, args=("192.168.3.38",),daemon=True)
ping_thread.start()'''
client = connect_mqtt()
subscribe(client)
if __name__ == "__main__":
    
    while(1):
        client.loop_start()
        root.mainloop()
        client.loop_stop()