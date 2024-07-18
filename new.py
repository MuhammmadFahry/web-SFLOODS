import json
import requests
import streamlit as st

# Fungsi mengatur latar belakang
def set_bg(url: str):
    '''
    URL: Link atau alamat website untuk gambar latar belakang
    '''
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url({url});
             background-size: cover;
             background-repeat: no-repeat;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )
    return
    
set_bg("https://images.unsplash.com/photo-1534274988757-a28bf1a57c17?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8N3x8cmFpbnxlbnwwfHwwfHx8MA%3D%3D") # Gambar

# Fungsi rekomendasi
def get_recommendation(temp):
    if temp <= 0:
        return "Pakai pakaian yang sangat tebal, seperti jaket tebal dan lapisan pakaian berlapis."
    elif 0 < temp <= 10:
        return "Gunakan jaket atau sweater yang hangat dan mungkin topi serta sarung tangan."
    elif 10 < temp <= 20:
        return "Pakai jaket ringan atau sweater, dan pastikan tetap nyaman."
    elif 20 < temp <= 30:
        return "Kenakan pakaian ringan dan nyaman, seperti kaos dan celana pendek."
    elif 30 < temp:
        return "Gunakan pakaian yang sangat ringan dan tetap terhidrasi. Hindari sinar matahari langsung."
    else:
        return "Tidak ada rekomendasi yang tersedia."

# REQUESTS
r = requests.Session()

# Streamlit
st.title("SFLOODS")
tab1, tab2 = st.tabs(["Laporan Cuaca", "Prediksi Banjir"])

st.markdown(
    """
    <style>
    .weather-list {
        font-size: 14px;
    }
    .weather-list-item {
        margin-bottom: 10px;
    }
    .weather-icon {
        margin-right: 10px;
        vertical-align: middle;
    }
    .custom-column {
        border: 2px solid #b0b5bb;
        border-radius: 2%;
        padding: 10px;
        margin: 5px;
        text-align: center; /* Pusatkan teks */
        background-color: rgba(0, 0, 0, 0.8); /* Tambahkan background putih transparan untuk meningkatkan keterbacaan */
    }
    .stApp {
        color: white; /* Ganti warna teks menjadi putih untuk kontras yang lebih baik */
    }
    </style>
    """,
    unsafe_allow_html=True
)

with tab1:
    _con_cuaca = st.container()
    _con_cuaca.header("Laporan Cuaca")

    kota = _con_cuaca.text_input("Masukkan nama kota", value="Pekanbaru", key="cuaca")

    # OpenWeather
    API = "a0cb4aad9823a209a6512bc72ad21633"

    url = f"https://api.openweathermap.org/data/2.5/weather?q={kota.replace(' ', '+')}&appid={API}&units=metric&lang=id"
    t_hour = f"https://api.openweathermap.org/data/2.5/forecast?q={kota.replace(' ', '+')}&cnt=3&appid={API}&units=metric&lang=id"

    # Reqp
    geturl = r.get(url)
    thur = r.get(t_hour)
    statuscode = geturl.status_code

    # Check status code
    if statuscode == 200:
        js = json.loads(geturl.content)
        suhu = float(js["main"]["temp"])
        awan = [js['weather'][0]['main'], js['weather'][0]['description']]
        awan_string = ", ".join(awan)
        kota = str(js["name"]).replace("+", " ")
        
        # Menarik data yang diinginkan
        extracted_data = []
        if 'list' not in js:
            js = json.loads(thur.content)
        for entry in js['list']:
            temp = entry['main']['temp']
            humidity = entry['main']['humidity']
            weather_main = entry['weather'][0]['main']
            weather_description = entry['weather'][0]['description']
            dt_txt = entry['dt_txt']
            rain = entry['rain']['3h'] if 'rain' in entry and '3h' in entry['rain'] else 0  # Jika data hujan tidak ada, set 0
            
            extracted_data.append({
                'temp': temp,
                'humidity': humidity,
                'weather_main': weather_main,
                'weather_description': weather_description,
                'dt_txt': dt_txt,
                'rain': rain
            })
            
        tanda = f"""Suhu: {suhu} C\nJenis awan: {awan_string}"""

        _con_cuaca.text_area("Cuaca di " + kota + " Saat ini", tanda)
        _con_cuaca.text_area(label="Saran", value=f"Rekomendasi berdasarkan cuaca hari ini, {get_recommendation(suhu)}")
        _con_cuaca.subheader("Prediksi 3 jam")

        col = _con_cuaca.columns(3, gap="small")
        
        if extracted_data:
            for i, item in enumerate(extracted_data):
                with col[i % 3]:  # Distribute across 3 columns
                    if item['weather_main'] == "Rain":
                        icon = "☔"
                    elif item['weather_main'] == "Clouds":
                        icon = "🌥️"
                    else:
                        icon = "☁️"

                    col[i % 3].markdown(f"""
                        <div class=custom-column>
                        <div class=weather-list>
                        <div class=weather-icon>{icon}</div>
                        <div class=weather-list-item>Waktu: {item['dt_txt']}
                        <br>Suhu: {item['temp']}°C
                        <br>Kelembapan: {item['humidity']}%
                        <br>Cuaca: {item['weather_main']}
                        <br>Deskripsi: {item['weather_description']}
                        <br>Curah Hujan: {item['rain']} mm</div>
                        </div>
                        </div>""", unsafe_allow_html=True)
    else:
        st.warning("Tidak ada data terkait kota")
 
with tab2:
    _pred_banjir = st.container()
    _pred_banjir.subheader("Prediksi Banjir")
    col_banj = _pred_banjir.columns(3, gap="small")
    expander_banjir = _pred_banjir.expander("Rumus perhitungan")
    
    with expander_banjir:
        st.latex("\\%R = (H\\times 0.4) + (C\\times 0.5) + (W\\times 0.1)")
        st.write("""H: Kelembapan\n\n C: Curah Hujan\n\n W: Kondisi Cuaca (Jika kondisi adalah "Clear", W = 0
                    Jika kondisi adalah "Clouds", W = 0.3
                    Jika kondisi adalah "Rain", W = 1)""")
    try:
        if extracted_data:
            for i, item in enumerate(extracted_data):
                with col_banj[i % 3]:  # Distribute across 3 columns
                    if item['weather_main'] == "Rain":
                        icon = "☔"
                        W = 1
                    elif item['weather_main'] == "Clouds":
                        icon = "🌥️"
                        W = 0.3
                    else:
                        icon = "☁️"
                        W = 0
                    
                    rumus = (float(item['humidity'])*0.4) + (float(item['rain'])*0.5) + (W*0.1)
                    form_rumus = f"{rumus:.2f}"
                    
                    col_banj[i % 3].markdown(f"""
                        <div class=custom-column>
                        <div class=weather-list>
                        <div class=weather-icon>{icon}</div>
                        <div class=weather-list-item>Waktu: {item['dt_txt']}
                        <br>Persentase banjir: {form_rumus}%
                        </div>
                        </div>""", unsafe_allow_html=True)
    except NameError as e:
        st.warning("Tidak ada data terkait kota")
