"""
Program all system
Create by Arif Ramadhan
"""

import time
from datetime import datetime
from paho.mqtt import client as mqtt
from pyModbusTCP.client import ModbusClient
import json
import numpy as np
from scipy.io import loadmat
import threading
import os
import csv

csv_file = "data_hasiltest.csv"  # Nama file csv untuk simpan data

# Buat file CSV jika belum ada dan tulis header
if not os.path.isfile(csv_file):
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "timestamp",
                "exhaust_gas_temp",
                "main_bearing_temp",
                "rotary_speed",
                "prob_normal",
                "prob_warning",
                "prob_berbahaya",
                "predicted_label",
            ]
        )


# Komunikasi ke PLC
slave_address = "192.168.1.15"
port_modbus = 502
unit_id = 1
modbusclient = ModbusClient(
    host=slave_address, port=port_modbus, unit_id=unit_id, auto_open=True
)

# Fungsi ANN
try:
    data_bobot = loadmat("bobot3.mat")
    struktur = data_bobot["struktur"]

    mIW = struktur["IW"][0, 0][0, 0]  # (10,3)
    mLW1 = struktur["LW"][0, 0][1, 0]  # (3,10)
    mLW2 = struktur["LW"][0, 0][2, 1]  # (3,3)

    mBi = struktur["b"][0, 0][0, 0].reshape(-1, 1)  # (10x1)
    mBL1 = struktur["b"][0, 0][1, 0].reshape(-1, 1)  # (3x1)
    mBL2 = struktur["b"][0, 0][2, 0].reshape(-1, 1)  # (3x1)
except FileNotFoundError:
    print(
        "Error: File 'bobot3.mat' tidak ditemukan. Pastikan file berada di direktori yang sama."
    )
    exit()


def tansig(x):
    return 2 / (1 + np.exp(-2 * x)) - 1


def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)


# Fungsi MQTT
broker = "broker.emqx.io"  # 127.0.0.1/192.168.1.20
port_mqtt = 1883
topic = "mesin_kapal/all"
client_id = "mqttx_4a67a0f0"
connected_event = threading.Event()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Berhasil terhubung ke Broker MQTT!")
        client.subscribe(topic)
        connected_event.set()
    else:
        print(f"Gagal terhubung, kode status: {reason_code}")
        connected_event.set()


def on_message(client, userdata, msg):
    pesan_diterima = msg.payload.decode()
    print(f"Pesan diterima dari topik '{msg.topic}': '{pesan_diterima}'")


def main_function(
    exhaust_gas_temp, main_bearing_temp, rotary_speed, predicted_class, predicted_label
):
    print("-" * 20)
    print(f"Temp 1: {exhaust_gas_temp:.2f} C")
    print(f"Temp 2: {main_bearing_temp:.2f} C")
    print(f"rotary_speed   : {rotary_speed}")
    print(f"Status: {predicted_label}")
    print("-" * 20)

    payload = json.dumps(
        {
            "timestamp": datetime.now().isoformat(),
            "exhaust_gas_temp": round(exhaust_gas_temp, 2),
            "main_bearing_temp": round(main_bearing_temp, 2),
            "rotary_speed": rotary_speed,
            "prediction_class": predicted_class,
            "prediction_label": predicted_label,
        }
    )
    client.publish("mesin_kapal/exhaust_gas_temp", exhaust_gas_temp, qos=0)
    client.publish("mesin_kapal/main_bearing_temp", main_bearing_temp, qos=0)
    client.publish("mesin_kapal/rotary_speed", rotary_speed, qos=0)
    client.publish("mesin_kapal/prediction_class", predicted_class, qos=0)

    result = client.publish(topic, payload, qos=0)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"Data berhasil dikirim ke topik `{topic}`")
    else:
        print(f"Gagal mengirim pesan ke topik `{topic}`")


def modbus_koneksi():
    print("Koneksi Modbus terputus. Mencoba menghubungkan kembali...")
    modbusclient.close()
    while not modbusclient.is_open:
        if modbusclient.open():
            print("Koneksi Modbus berhasil disambungkan kembali.")
            break
        else:
            print("Gagal menyambung, mencoba lagi dalam 5 detik...")
            time.sleep(5)


# --- Inisialisasi MQTT Client ---
# client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
# client.on_message = on_message
client.connect(broker, port_mqtt)
client.loop_start()

# --- Blok Penunggu Koneksi ---
print("Menunggu koneksi ke Broker MQTT...")
if not connected_event.wait(timeout=15):  # Menunggu maksimal 15 detik
    print("Gagal terhubung ke MQTT setelah 15 detik. Program berhenti.")
    client.loop_stop()
    exit()

print("\nKoneksi berhasil. Memulai loop utama...\n" + "=" * 50)

try:
    last_save_time = time.time()
    while True:
        if not modbusclient.is_open:
            modbus_koneksi()
            continue

        read_Tempe = modbusclient.read_holding_registers(250, 2)
        read_rotary_speed = modbusclient.read_holding_registers(7, 1)

        if not (read_Tempe and read_rotary_speed):
            print("Gagal membaca data dari Modbus.")
            modbus_koneksi()
            continue

        exhaust_gas_temp = read_Tempe[0] / 100
        main_bearing_temp = (read_Tempe[1] / 100) * 4
        rotary_speed = read_rotary_speed[0] * 60
        data_ann = np.array(
            [exhaust_gas_temp, main_bearing_temp, rotary_speed]
        ).reshape(-1, 1)

        class_labels = [
            "Normal",
            "Warning",
            "Berbahaya",
            "Mati",
        ]  # Tambahkan label "Mati" untuk konsistensi

        if rotary_speed <= 10:
            client.publish(
                "mesin_kapal/status_mesin", "OFF", qos=0
            )  # Logika terbalik, <= 10 harusnya OFF
            predicted_class = 3  # Kelas 3 untuk kondisi Mesin Mati
            predicted_label = class_labels[
                predicted_class
            ]  # Sekarang ini valid -> "Mati"
            probabilities = np.array(
                [[0], [0], [0]]
            )  # Probabilitas nol saat mesin mati

            # Kirim probabilitas nol
            for i in range(3):
                topic_prob = f"mesin_kapal/probabilitas_{i+1}"
                client.publish(topic_prob, 0, qos=0)

        else:
            client.publish("mesin_kapal/status_mesin", "ON", qos=0)

            # -> Proses Feedforward ANN <- #
            nH1 = np.dot(mIW, data_ann) + mBi
            aH1 = tansig(nH1)
            nH2 = np.dot(mLW1, aH1) + mBL1
            aH2 = tansig(nH2)
            nOut = np.dot(mLW2, aH2) + mBL2
            probabilities = softmax(nOut)

            predicted_class = int(np.argmax(probabilities))
            predicted_label = class_labels[predicted_class]

            # Kirim probabilitas hasil perhitungan
            for i, prob in enumerate(probabilities):
                topic_prob = f"mesin_kapal/probabilitas_{i+1}"
                # Mengirim nilai float dari array numpy
                client.publish(topic_prob, float(round(prob,4)), qos=0)

        # Kirim data ke %MW20 PLC (nilai 0, 1, 2, atau 3)
        modbusclient.write_single_register(20, predicted_class)
        # Panggil fungsi untuk mengirim data utama via MQTT
        main_function(
            exhaust_gas_temp,
            round(main_bearing_temp, 2),
            rotary_speed,
            predicted_class,
            predicted_label,
        )

        if time.time() - last_save_time >= 5:
            print("--- Waktunya menyimpan data ke CSV... ---")
            with open(csv_file, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        datetime.now().isoformat(),
                        round(exhaust_gas_temp, 2),
                        round(main_bearing_temp, 2),
                        rotary_speed,
                        round(probabilities[0, 0], 4),
                        round(probabilities[1, 0], 4),
                        round(probabilities[2, 0], 4),
                        predicted_label,
                    ]
                )

            last_save_time = time.time()

        # Cetak detail probabilitas (opsional)
        print("\nDetail probabilitas:")
        print(f"  - Normal    : {probabilities[0,0]:.4f}")
        print(f"  - Warning   : {probabilities[1,0]:.4f}")
        print(f"  - Berbahaya : {probabilities[2,0]:.4f}\n")

        # Jeda sebelum iterasi berikutnya
        time.sleep(1)

except KeyboardInterrupt:
    print("\nProgram dihentikan oleh pengguna.")

except Exception as e:
    print(f"\nTerjadi error yang tidak terduga: {e}")

finally:
    print("Membersihkan dan menutup koneksi MQTT...")
    if modbusclient.is_open:
        modbusclient.close()
    client.loop_stop()
    client.disconnect()
