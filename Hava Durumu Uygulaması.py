import tkinter as tk
from tkinter import messagebox, ttk
import requests
import matplotlib.pyplot as plt
import folium
import webbrowser
import os

API_KEY = "bf55ccaf026ee0388f596a30af09e38e"

# 🌍 Hava durumu bilgisini çek
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&lang=tr&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        main = data["main"]
        weather = data["weather"][0]
        wind = data["wind"]
        coord = data["coord"]
        return {
            "city": city,
            "temp": main["temp"],
            "feels_like": main["feels_like"],
            "description": weather["description"],
            "wind": wind["speed"],
            "lat": coord["lat"],
            "lon": coord["lon"]
        }
    else:
        return None

# 📅 5 günlük hava tahmini al
def get_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&lang=tr&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temps = [item["main"]["temp"] for item in data["list"]]
        times = [item["dt_txt"] for item in data["list"]]
        return times, temps
    else:
        return None, None

# 🔹 Tek şehir için sonucu göster
def show_weather():
    city = city_var.get()
    weather = get_weather(city)
    if weather:
        result_text.set(
            f"🌍 Şehir: {weather['city']}\n"
            f"🌡️ Sıcaklık: {weather['temp']}°C\n"
            f"🤒 Hissedilen: {weather['feels_like']}°C\n"
            f"☁️ Durum: {weather['description']}\n"
            f"💨 Rüzgar: {weather['wind']} m/s"
        )
    else:
        messagebox.showerror("Hata", "Şehir bulunamadı veya API hatası!")

# 🔹 Birden fazla şehri alıp karşılaştırma grafiği çiz
def compare_cities():
    cities = city_entry.get().split(",")
    temps = []
    names = []

    for c in cities:
        c = c.strip()
        weather = get_weather(c)
        if weather:
            names.append(weather["city"])
            temps.append(weather["temp"])
        else:
            messagebox.showerror("Hata", f"{c} bulunamadı!")

    if temps:
        plt.figure(figsize=(7,5))
        plt.bar(names, temps, color="orange")
        plt.title("Şehirlerin Sıcaklık Karşılaştırması (°C)")
        plt.xlabel("Şehirler")
        plt.ylabel("Sıcaklık (°C)")
        plt.show()

# 🔹 5 günlük hava tahmini çiz
def forecast_chart():
    city = city_var.get()
    times, temps = get_forecast(city)
    if temps:
        plt.figure(figsize=(10,5))
        plt.plot(times[:10], temps[:10], marker="o", color="blue")
        plt.xticks(rotation=45)
        plt.title(f"{city} - 5 Günlük Tahmin")
        plt.xlabel("Tarih/Saat")
        plt.ylabel("Sıcaklık (°C)")
        plt.tight_layout()
        plt.show()
    else:
        messagebox.showerror("Hata", "Tahmin verisi alınamadı!")

# 🔹 Harita üzerinde şehir işaretle
def show_map():
    city = city_var.get()
    weather = get_weather(city)
    if weather:
        m = folium.Map(location=[weather["lat"], weather["lon"]], zoom_start=8)
        folium.Marker([weather["lat"], weather["lon"]],
                      popup=f"{weather['city']} - {weather['temp']}°C").add_to(m)
        file_path = os.path.abspath("map.html")
        m.save(file_path)
        webbrowser.open(f"file://{file_path}")
    else:
        messagebox.showerror("Hata", "Şehir bulunamadı!")

# 🎨 Tkinter Arayüz
root = tk.Tk()
root.title("Gelişmiş Hava Durumu Uygulaması")
root.geometry("450x400")

# Dropdown şehir seçimi
tk.Label(root, text="Bir şehir seçin:").pack(pady=5)
city_var = tk.StringVar()
cities_list = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Berlin", "Paris", "London", "New York"]
city_dropdown = ttk.Combobox(root, textvariable=city_var, values=cities_list)
city_dropdown.pack(pady=5)
city_dropdown.current(0)

# Çoklu şehir karşılaştırma textbox
tk.Label(root, text="Birden fazla şehir girin (virgül ile ayır):").pack(pady=5)
city_entry = tk.Entry(root, width=40)
city_entry.pack(pady=5)

# Butonlar
tk.Button(root, text="Tek Şehir Hava Durumu", command=show_weather).pack(pady=5)
tk.Button(root, text="Şehirleri Karşılaştır (Grafik)", command=compare_cities).pack(pady=5)
tk.Button(root, text="5 Günlük Tahmin (Grafik)", command=forecast_chart).pack(pady=5)
tk.Button(root, text="Haritada Göster", command=show_map).pack(pady=5)

# Sonuç alanı
result_text = tk.StringVar()
tk.Label(root, textvariable=result_text, justify="left", font=("Arial", 12)).pack(pady=10)

root.mainloop()
