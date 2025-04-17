import streamlit as st
import pandas as pd
import random
import re
import os
import base64
import time
from datetime import datetime
import streamlit.components.v1 as components

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Aplikasi Pengkondisian Stres",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS for consistent styling
st.markdown("""
<style>
    .big-font {
        font-size: 24px !important;
        font-weight: bold !important;
    }
    .medium-font {
        font-size: 20px !important;
    }
    .small-font {
        font-size: 16px !important;
    }
    .stButton>button {
        width: 100%;
        padding: 10px 0;
        font-size: 18px;
    }
    .stProgress > div > div > div {
        background-color: #4CAF50;
    }
    .stRadio > div {
        padding: 10px;
        border-radius: 5px;
        background-color: #f0f2f6;
    }
    .stTextArea textarea {
        font-size: 16px;
    }
    .stNumberInput input {
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# APP CONSTANTS
# ============================================
DASS21_OPTIONS = [
    "Tidak sesuai dengan saya sama sekali",
    "Sesuai dengan saya sampai tingkat tertentu atau dalam waktu tertentu",
    "Sesuai dengan saya pada tingkat yang cukup atau sering", 
    "Sangat sesuai dengan saya atau sering sekali"
]

ACUTE_STRESS_OPTIONS = [
    "Tidak sama sekali",
    "Sedikit",
    "Sedang",
    "Cukup banyak",
    "Sangat banyak"
]

DASS21_QUESTIONS = [
    "Saya merasa sulit untuk bersantai",
    "Saya cenderung bereaksi berlebihan terhadap situasi",
    "Saya merasa sangat gugup",
    "Saya merasa gelisah",
    "Saya merasa sulit untuk tenang",
    "Saya sulit untuk sabar dalam menghadapi gangguan terhadap hal yang sedang saya lakukan",
    "Saya merasa bahwa saya mudah tersinggung",
    "Saya merasa takut tanpa alasan yang jelas",
    "Saya merasa sedih dan tertekan",
    "Saya merasa tidak berharga",
    "Saya merasa bahwa hidup tidak bermanfaat",
    "Saya merasa sulit untuk berinisiatif dalam melakukan sesuatu",
    "Saya merasa gemetar (misalnya pada tangan)",
    "Saya merasa khawatir dengan situasi saat saya mungkin menjadi panik dan mempermalukan diri sendiri",
    "Saya merasa bahwa saya tidak memiliki harapan untuk masa depan",
    "Saya menemukan diri saya menjadi tidak sabar",
    "Saya merasa bahwa saya sangat sensitif",
    "Saya merasa ketakutan",
    "Saya mengalami kesulitan dalam menelan",
    "Saya tidak dapat merasakan perasaan positif",
    "Saya kesulitan mendapatkan semangat untuk melakukan sesuatu",
]

ACUTE_STRESS_QUESTIONS = [
    "Seberapa stres yang Anda rasakan saat ini?",
    "Seberapa tegang atau gelisah yang Anda rasakan saat ini?",
    "Seberapa cemas yang Anda rasakan saat ini?",
    "Seberapa nyaman yang Anda rasakan dengan situasi Anda saat ini?",
    "Saya merasa jantung saya berdetak lebih cepat",
    "Saya merasa telapak tangan saya berkeringat",
    "Saya merasa sulit berkonsentrasi saat ini",
    "Saya merasa khawatir tentang performa saya dalam tugas yang diberikan",
    "Saya merasa mampu menghadapi tantangan yang ada saat ini",
    "Saya merasa terganggu dengan pikiran-pikiran yang tidak relevan"
]

PRESENTATION_TOPICS = [
    "Manfaat Menjaga Pola Tidur yang Baik dan Sehat",
    "Manfaat Membaca Buku dalam Pengembangan Diri",
    "Pentingnya Berolahraga Secara Teratur untuk Kesehatan",
    "Peran Musik dalam Kehidupan Sehari-hari",
    "Pentingnya Memiliki Hobi di Luar Pekerjaan",
    "Pentingnya Meluangkan Waktu untuk Bersantai dan Melepas Penat",
    "Bagaimana Cara Mengatur Prioritas dalam Kehidupan",
    "Pentingnya Keberagaman dalam Kehidupan Sosial",
    "Cara Menghadapi Tantangan dengan Pikiran Positif",
    "Manfaat Menjaga Hubungan Sosial yang Sehat"
]

predefined_stories = [
    {
        "judul": "Hari yang Biasa",
        "isi": "Pagi hari, matahari belum terlalu tinggi. Cahaya dari balik tirai jatuh ke lantai dalam garis-garis samar. Udara di dalam kamar cukup sejuk. Tidak terlalu dingin, tidak juga hangat. Tidak ada suara bising dari luar, hanya suara samar kipas angin yang berputar perlahan di langit-langit..."
    },
    {
        "judul": "Hari di Toko Alat Tulis", 
        "isi": "Pintu toko terbuka dengan suara lonceng kecil. Hana, perempuan berambut sebahu dengan kemeja abu-gray, sudah berada di balik meja kasir sejak pukul sembilan. Ia menekan tombol pada mesin kasir untuk mengecek saldo awal. Jumlahnya sesuai catatan. Tidak kurang, tidak lebih..."
    }
]

# ============================================
# UTILITY FUNCTIONS
# ============================================
def get_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download Data CSV</a>'
    return href

def extract_stories_from_docx(file_path):
    try:
        if not os.path.exists(file_path):
            return predefined_stories
            
        doc = docx.Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        
        titles_pattern1 = re.findall(r'## (.*?)(?=\n|$)', '\n'.join(paragraphs))
        
        titles_pattern2 = []
        story_start_indices = []
        
        for i, para in enumerate(paragraphs):
            if any(title in para for title in [
                "Hari yang Biasa", "Hari di Toko Alat Tulis", "Hari di Rumah Penyewaan Buku",
                "Hari di Taman Kota", "Kedai Kopi", "Di Toko Bunga", "Di Stasiun Kereta",
                "Di Kelas", "Di Pantai", "Di Ruang Kepala Sekolah", "Di Kolong Jembatan",
                "Di Dalam Laboratorium"
            ]):
                titles_pattern2.append(para.strip())
                story_start_indices.append(i)
                
        if titles_pattern1:
            titles = titles_pattern1
            content = '\n'.join(paragraphs)
            stories = []
            for i in range(len(titles)):
                if i < len(titles) - 1:
                    story_content = content.split(f"## {titles[i]}\n")[1].split(f"## {titles[i+1]}")[0].strip()
                else:
                    story_content = content.split(f"## {titles[i]}\n")[1].strip()
                stories.append({"judul": titles[i], "isi": story_content})
                
        elif titles_pattern2:
            titles = titles_pattern2
            stories = []
            for i in range(len(story_start_indices)):
                judul = titles[i]
                start_idx = story_start_indices[i] + 1
                end_idx = story_start_indices[i + 1] if i < len(story_start_indices) - 1 else len(paragraphs)
                isi = "\n\n".join(paragraphs[start_idx:end_idx])
                stories.append({"judul": judul, "isi": isi})
        else:
            return predefined_stories
        
        return stories if stories else predefined_stories
    except Exception as e:
        return predefined_stories

# ============================================
# SCORE CALCULATION FUNCTIONS
# ============================================
def calculate_dass21_scores(responses):
    scores = {"Depresi": 0, "Kecemasan": 0, "Stres": 0}
    
    depresi_idx = [8, 9, 10, 11, 14, 19, 20]
    kecemasan_idx = [2, 3, 7, 13, 17, 18, 19]
    stres_idx = [0, 1, 4, 5, 6, 15, 16]
    
    for i, response in responses.items():
        score = DASS21_OPTIONS.index(response)
        if i in depresi_idx: scores["Depresi"] += score
        if i in kecemasan_idx: scores["Kecemasan"] += score
        if i in stres_idx: scores["Stres"] += score
    
    return scores

def calculate_acute_stress_score(responses):
    score = 0
    for i, response in responses.items():
        points = ACUTE_STRESS_OPTIONS.index(response)
        if i in [3, 8]: score += 4 - points
        else: score += points
    return score

def categorize_dass21(scores):
    categories = {}
    
    # Stress categories
    if scores["Stres"] <= 7: categories["Stres"] = "Rendah"
    elif scores["Stres"] <= 14: categories["Stres"] = "Sedang"
    else: categories["Stres"] = "Tinggi"
    
    # Depression categories
    if scores["Depresi"] <= 4: categories["Depresi"] = "Normal"
    elif scores["Depresi"] <= 6: categories["Depresi"] = "Ringan"
    elif scores["Depresi"] <= 10: categories["Depresi"] = "Sedang"
    elif scores["Depresi"] <= 13: categories["Depresi"] = "Parah"
    else: categories["Depresi"] = "Sangat Parah"
    
    # Anxiety categories
    if scores["Kecemasan"] <= 3: categories["Kecemasan"] = "Normal"
    elif scores["Kecemasan"] <= 5: categories["Kecemasan"] = "Ringan"
    elif scores["Kecemasan"] <= 7: categories["Kecemasan"] = "Sedang"
    elif scores["Kecemasan"] <= 9: categories["Kecemasan"] = "Parah"
    else: categories["Kecemasan"] = "Sangat Parah"
    
    return categories

def categorize_acute_stress(score):
    if score <= 13: return "Rendah"
    elif score <= 26: return "Sedang"
    else: return "Tinggi"

def save_session_results(condition):
    dass21_scores = calculate_dass21_scores(st.session_state.dass21_responses)
    acute_stress_score = calculate_acute_stress_score(st.session_state.acute_stress_responses)
    categories_dass21 = categorize_dass21(dass21_scores)
    category_acute = categorize_acute_stress(acute_stress_score)
    
    result_data = {
        **st.session_state.data_diri,
        "Kondisi": condition,
        "Skor DASS21 - Depresi": dass21_scores["Depresi"],
        "Kategori DASS21 - Depresi": categories_dass21["Depresi"],
        "Skor DASS21 - Kecemasan": dass21_scores["Kecemasan"],
        "Kategori DASS21 - Kecemasan": categories_dass21["Kecemasan"],
        "Skor DASS21 - Stres": dass21_scores["Stres"],
        "Kategori DASS21 - Stres": categories_dass21["Stres"],
        "Skor Respons Stres Akut": acute_stress_score,
        "Kategori Respons Stres Akut": category_acute,
        "Waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    for i, question in enumerate(DASS21_QUESTIONS):
        result_data[f"DASS21_Q{i+1}"] = st.session_state.dass21_responses.get(i, "")
    
    for i, question in enumerate(ACUTE_STRESS_QUESTIONS):
        result_data[f"Acute_Q{i+1}"] = st.session_state.acute_stress_responses.get(i, "")
    
    if condition == "Tahap 2":
        result_data["Topik Presentasi"] = st.session_state.get("selected_topic", "")
        result_data["Catatan Presentasi"] = st.session_state.get("presentation_notes", "")
        
        if 'answers' in st.session_state:
            for i, answer in enumerate(st.session_state.answers):
                result_data[f"Tugas_Aritmatika_{i+1}_Soal"] = answer['problem']
                result_data[f"Tugas_Aritmatika_{i+1}_Jawaban"] = answer['user_answer']
                result_data[f"Tugas_Aritmatika_{i+1}_Benar"] = answer['is_correct']
    
    if condition == "Tahap 3":
        result_data["Topik Presentasi"] = st.session_state.get("high_presentation_topic", "")
        result_data["Catatan Presentasi"] = st.session_state.get("high_presentation_notes", "")
        result_data["Jumlah Percobaan Aritmatika"] = st.session_state.get("high_arithmetic_attempts", 0)
        result_data["Jawaban Benar Berturut-turut"] = st.session_state.get("high_arithmetic_correct_count", 0)
        
        if 'high_arithmetic_history' in st.session_state:
            for i, item in enumerate(st.session_state.high_arithmetic_history):
                result_data[f"Tugas_Aritmatika_{i+1}_Soal"] = item['question']
                result_data[f"Tugas_Aritmatika_{i+1}_Jawaban"] = item['user_answer']
                result_data[f"Tugas_Aritmatika_{i+1}_Benar"] = item['correct']
                if not item['correct']:
                    result_data[f"Tugas_Aritmatika_{i+1}_Jawaban_Benar"] = item.get('correct_answer', '')
    
    if 'results' not in st.session_state:
        st.session_state.results = []
    st.session_state.results.append(result_data)
    
    if 'completed_conditions' not in st.session_state:
        st.session_state.completed_conditions = []
    st.session_state.completed_conditions.append(condition)

# ============================================
# APPLICATION PAGES
# ============================================
def data_diri_page():
    st.title("📝 Data Diri")
    st.markdown("---")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Informasi Pribadi")
            nama = st.text_input("Nama Lengkap", key="nama")
            umur = st.number_input("Umur", min_value=0, max_value=120, step=1, key="umur")
            gender = st.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"], key="gender")
        
        with col2:
            st.markdown("### Data Fisik")
            bb = st.number_input("Berat Badan (kg)", min_value=0.0, max_value=300.0, step=0.1, key="bb")
            tb = st.number_input("Tinggi Badan (cm)", min_value=0.0, max_value=300.0, step=0.1, key="tb")
    
    st.markdown("---")
    col_btn = st.columns([1, 3, 1])
    with col_btn[1]:
        if st.button("✅ Simpan dan Lanjut ke Tahap 1", use_container_width=True, key="save_personal_data"):
            if not nama or umur <= 0 or bb <= 0 or tb <= 0:
                st.error("Mohon lengkapi semua data dengan benar!")
            else:
                st.session_state.data_diri = {
                    "Nama": nama, "Umur": umur, "Jenis Kelamin": gender,
                    "Berat Badan (kg)": bb, "Tinggi Badan (cm)": tb,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.page = "tahap1"
                st.rerun()

def tahap1_page():
    st.title("📖 Tahap 1 - Membaca Materi Netral")
    st.markdown("---")
    
    st.markdown("""
    <div class='medium-font'>
    <b>Instruksi:</b><br>
    Anda akan membaca materi netral selama 5-10 menit. 
    Silakan tekan tombol di bawah untuk memulai.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("▶️ Mulai Tahap 1", key="start_tahap1"):
            st.session_state.current_condition = "Tahap 1"
            st.session_state.page = "cerita_setup"
            st.rerun()

def tahap2_page():
    st.title("📝 Tahap 2 - Presentasi Topik Netral")
    st.markdown("---")
    
    st.markdown("""
    <div class='medium-font'>
    <b>Instruksi:</b><br>
    1. Anda akan mempersiapkan presentasi tentang topik netral selama 5 menit<br>
    2. Presentasikan di depan evaluator<br>
    3. Dilanjutkan dengan tugas aritmatika sederhana
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("▶️ Mulai Tahap 2", key="start_tahap2"):
            st.session_state.current_condition = "Tahap 2"
            st.session_state.page = "cerita_setup"
            st.rerun()

def tahap3_page():
    st.title("🎤 Tahap 3 - Presentasi Kelemahan Diri")
    st.markdown("---")
    
    st.markdown("""
    <div class='medium-font'>
    <b>Instruksi:</b><br>
    1. Anda akan mempersiapkan presentasi tentang "kelemahan diri" selama 5 menit<br>
    2. Presentasikan di depan evaluator<br>
    3. Dilanjutkan dengan tugas aritmatika sulit (pengurangan serial 13 dari 1022)
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("▶️ Mulai Tahap 3", key="start_tahap3"):
            st.session_state.current_condition = "Tahap 3"
            st.session_state.page = "high_prep"
            st.rerun()

def high_prep_page():
    st.title("📝 Persiapan Presentasi - Tahap 3")
    st.markdown("---")
    
    if 'high_prep_start_time' not in st.session_state:
        st.session_state.high_prep_start_time = time.time()
    
    elapsed = time.time() - st.session_state.high_prep_start_time
    prep_time_left = max(0, 3 - elapsed)
    
    if 'high_presentation_topic' not in st.session_state:
        st.session_state.high_presentation_topic = random.choice(["Kelemahan Anda", "Mengapa Anda cocok untuk pekerjaan"])
    
    st.markdown("### Topik Presentasi Anda:")
    st.markdown(f"<div style='padding:10px; background-color:#ffcccb; border-radius:5px; color:#ff0000; font-size:24px; font-weight:bold;'>{st.session_state.high_presentation_topic}</div>", unsafe_allow_html=True)
    
    minutes, seconds = divmod(int(prep_time_left), 60)
    st.markdown(f"### Waktu Persiapan: {minutes:02d}:{seconds:02d}")
    
    st.markdown("### Catatan Persiapan Anda:")
    if 'high_presentation_notes' not in st.session_state:
        st.session_state.high_presentation_notes = ""
    
    st.session_state.high_presentation_notes = st.text_area(
        "Tulis catatan presentasi Anda di sini:",
        value=st.session_state.high_presentation_notes,
        height=300,
        key="high_prep_notes",
        label_visibility="collapsed"
    )
    
    if prep_time_left <= 0:
        col_btn = st.columns([1, 2, 1])
        with col_btn[1]:
            if st.button("➡️ Lanjut ke Presentasi", key="proceed_to_high_presentation"):
                st.session_state.high_presentation_start_time = time.time()
                st.session_state.page = "high_presentation"
                st.rerun()
    else:
        time.sleep(0.1)
        st.rerun()

def high_presentation_page():
    st.title("🎤 Presentasi - Tahap 3")
    st.markdown("---")
    
    if 'high_presentation_start_time' not in st.session_state:
        st.session_state.high_presentation_start_time = time.time()
    
    elapsed = time.time() - st.session_state.high_presentation_start_time
    presentation_time_left = max(0, 3 - elapsed)
    
    st.markdown("### Topik Presentasi Anda:")
    st.markdown(f"<div style='padding:10px; background-color:#ffcccb; border-radius:5px; color:#ff0000; font-size:24px; font-weight:bold;'>{st.session_state.high_presentation_topic}</div>", unsafe_allow_html=True)
    
    minutes, seconds = divmod(int(presentation_time_left), 60)
    st.markdown(f"### Waktu Presentasi: {minutes:02d}:{seconds:02d}")
    
    st.markdown("### Catatan Persiapan Anda:")
    st.write(st.session_state.high_presentation_notes)
    
    if presentation_time_left <= 0:
        col_btn = st.columns([1, 2, 1])
        with col_btn[1]:
            if st.button("➡️ Lanjut ke Tugas Aritmatika", key="finish_high_presentation"):
                st.session_state.page = "high_arithmetic"
                st.rerun()
    else:
        time.sleep(0.1)
        st.rerun()

def high_arithmetic_page():
    if 'show_arithmetic_instructions' not in st.session_state:
        st.session_state.show_arithmetic_instructions = True
    
    if st.session_state.show_arithmetic_instructions:
        st.title("🧮 Instruksi Tugas Aritmatika - Tahap 3")
        st.markdown("---")
        
        st.markdown("""
        <div class='medium-font'>
        <b>Instruksi:</b><br>
        1. Hitung pengurangan serial mulai dari 1022 dengan pengurangan 13<br>
        2. Anda memiliki waktu 5 menit<br>
        3. Jika salah, Anda harus memulai kembali dari 1022
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        col_btn = st.columns([1, 2, 1])
        with col_btn[1]:
            if st.button("▶️ Mulai Tugas", key="start_arithmetic"):
                st.session_state.show_arithmetic_instructions = False
                st.session_state.arithmetic_start_time = time.time()
                st.rerun()
        return
    
    st.title("⏱️ Tugas Aritmatika - Tahap 3")
    st.markdown("---")
    
    elapsed = time.time() - st.session_state.arithmetic_start_time
    time_left = max(0, 3 - elapsed)
    
    minutes, seconds = divmod(int(time_left), 60)
    st.markdown(f"### Waktu Tersisa: {minutes:02d}:{seconds:02d}")
    
    progress = min(elapsed / 3, 1.0)
    st.progress(progress)
    
    if time_left <= 0:
        st.success("Waktu tugas aritmatika telah habis!")
        col_btn = st.columns([1, 2, 1])
        with col_btn[1]:
            if st.button("➡️ Lanjut ke Kuesioner", key="finish_high_arithmetic"):
                st.session_state.page = "dass21"
                st.rerun()
    else:
        time.sleep(1)
        st.rerun()

def cerita_setup_page():
    st.title(f"⚙️ Pengaturan - {st.session_state.current_condition}")
    st.markdown("---")
    
    if st.session_state.current_condition == "Tahap 2":
        st.markdown("### Persiapan Presentasi")
        
        if 'selected_topic' not in st.session_state:
            st.session_state.selected_topic = random.choice(PRESENTATION_TOPICS)
        
        st.markdown("#### Topik Presentasi Anda:")
        st.markdown(f"<div style='padding:10px; background-color:#cce5ff; border-radius:5px; font-size:24px; font-weight:bold;'>{st.session_state.selected_topic}</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class='medium-font'>
        <b>Instruksi:</b><br>
        1. Siapkan presentasi singkat tentang topik di atas<br>
        2. Presentasikan secara jelas dan terstruktur<br>
        3. Siapkan poin-poin utama yang ingin disampaikan
        </div>
        """, unsafe_allow_html=True)
        
        col_btn = st.columns([1, 2, 1])
        with col_btn[1]:
            if st.button("▶️ Mulai Persiapan Presentasi", key="start_presentation"):
                st.session_state.page = "presentation_prep"
                st.rerun()
        
        return
    
    st.markdown("### Pengaturan Tampilan Teks")
    col1, col2 = st.columns(2)
    
    with col1:
        # Initialize font_size in session_state if it doesn't exist
        if 'font_size' not in st.session_state:
            st.session_state.font_size = 16
            
        # Use the session_state value as the default for the slider
        font_size = st.slider(
            "Ukuran Font", 
            12, 24, 
            st.session_state.font_size,  # Use current value as default
            key="font_size_slider"  # Different key from the session_state variable
        )
        # Update session_state only if the slider value changes
        if font_size != st.session_state.font_size:
            st.session_state.font_size = font_size
    
    with col2:
        # Initialize auto_scroll in session_state if it doesn't exist
        if 'auto_scroll' not in st.session_state:
            st.session_state.auto_scroll = False
            
        auto_scroll = st.checkbox(
            "Auto-Scroll", 
            st.session_state.auto_scroll,  # Use current value as default
            key="auto_scroll_checkbox"  # Different key from the session_state variable
        )
        # Update session_state only if the checkbox value changes
        if auto_scroll != st.session_state.auto_scroll:
            st.session_state.auto_scroll = auto_scroll
            
        if st.session_state.auto_scroll:
            # Initialize scroll_speed in session_state if it doesn't exist
            if 'scroll_speed' not in st.session_state:
                st.session_state.scroll_speed = 1.0
                
            scroll_speed = st.slider(
                "Kecepatan Scroll", 
                0.5, 5.0, 
                st.session_state.scroll_speed,  # Use current value as default
                step=0.5, 
                key="scroll_speed_slider"  # Different key from the session_state variable
            )
            # Update session_state only if the slider value changes
            if scroll_speed != st.session_state.scroll_speed:
                st.session_state.scroll_speed = scroll_speed
    
    st.markdown("### Mulai Pembacaan Cerita")
    if 'stories_loaded' not in st.session_state:
        st.session_state.stories = extract_stories_from_docx("Kumpulan Cerita.docx")
        st.session_state.stories_loaded = True
    
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("🔀 Acak Cerita dan Mulai Membaca", key="start_reading"):
            if st.session_state.stories:
                st.session_state.selected_story = random.choice(st.session_state.stories)
                st.session_state.page = "cerita"
                st.rerun()

def presentation_prep_page():
    st.title("📝 Persiapan Presentasi - Tahap 2")
    st.markdown("---")
    
    if 'prep_start_time' not in st.session_state:
        st.session_state.prep_start_time = time.time()
    
    elapsed = time.time() - st.session_state.prep_start_time
    time_left = max(0, 3 - elapsed)

    st.markdown("### Topik Presentasi Anda:")
    st.markdown(f"<div style='padding:10px; background-color:#cce5ff; border-radius:5px; font-size:24px; font-weight:bold;'>{st.session_state.selected_topic}</div>", unsafe_allow_html=True)
    
    minutes, seconds = divmod(int(time_left), 60)
    st.markdown(f"### Waktu Persiapan: {minutes:02d}:{seconds:02d}")
    
    st.markdown("### Catatan Persiapan Anda:")
    if 'presentation_notes' not in st.session_state:
        st.session_state.presentation_notes = ""
    
    st.session_state.presentation_notes = st.text_area(
        "Tulis catatan presentasi Anda di sini:",
        value=st.session_state.presentation_notes,
        height=300,
        key="presentation_notes_area",
        label_visibility="collapsed"
    )
    
    if time_left <= 0:
        col_btn = st.columns([1, 2, 1])
        with col_btn[1]:
            if st.button("➡️ Lanjut ke Presentasi", key="proceed_to_presentation"):
                st.session_state.page = "presentation"
                st.rerun()
    else:
        time.sleep(0.1)
        st.rerun()

def presentation_page():
    st.title("🎤 Presentasi - Tahap 2")
    st.markdown("---")
    
    st.markdown("### Topik Presentasi Anda:")
    st.markdown(f"<div style='padding:10px; background-color:#cce5ff; border-radius:5px; font-size:24px; font-weight:bold;'>{st.session_state.selected_topic}</div>", unsafe_allow_html=True)
    st.markdown("### Catatan Persiapan Anda:")
    st.write(st.session_state.presentation_notes)
    
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("➡️ Lanjut ke Tugas Aritmatika", key="finish_presentation"):
            st.session_state.page = "arithmetic_task"
            st.rerun()

def arithmetic_task_page():
    st.title("🧮 Tugas Aritmatika - Tahap 2")
    st.markdown("---")
    
    st.markdown("""
    <div class='medium-font'>
    <b>Instruksi:</b><br>
    1. Selesaikan soal pengurangan/pembagian berikut<br>
    2. Jawab dengan benar untuk melanjutkan ke soal berikutnya<br>
    3. Total ada 5 soal yang harus diselesaikan
    </div>
    """, unsafe_allow_html=True)
    
    if 'arithmetic_problems' not in st.session_state:
        st.session_state.arithmetic_problems = []
        st.session_state.current_problem = 0
        st.session_state.answers = []
        st.session_state.task_completed = False
        
        for _ in range(5):
            if random.random() > 0.5:
                a = random.randint(50, 100)
                b = random.randint(1, 49)
                st.session_state.arithmetic_problems.append({
                    'type': 'pengurangan',
                    'question': f"{a} - {b} = ?",
                    'answer': a - b
                })
            else:
                b = random.randint(2, 10)
                answer = random.randint(5, 12)
                a = b * answer
                st.session_state.arithmetic_problems.append({
                    'type': 'pembagian',
                    'question': f"{a} ÷ {b} = ?",
                    'answer': answer
                })

    if not st.session_state.task_completed:
        problem = st.session_state.arithmetic_problems[st.session_state.current_problem]
        
        st.markdown(f"### Soal {st.session_state.current_problem + 1}/5")
        st.markdown(f"<div class='big-font'>{problem['question']}</div>", unsafe_allow_html=True)
        
        user_answer = st.number_input("Jawaban Anda:", key=f"answer", step=1)
        
        if st.button("✅ Submit Jawaban"):
            is_correct = (user_answer == problem['answer'])
            
            st.session_state.answers.append({
                'problem': problem['question'],
                'user_answer': user_answer,
                'is_correct': is_correct,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
            
            if is_correct:
                st.success("✅ Jawaban benar! Lanjut ke soal berikutnya.")
                st.session_state.current_problem += 1
                
                if st.session_state.current_problem >= 5:
                    st.session_state.task_completed = True
            else:
                st.error("❌ Jawaban salah. Silakan coba lagi.")
            
            st.rerun()
        
        st.progress((st.session_state.current_problem)/5)
        
        if st.session_state.answers:
            st.markdown("#### Riwayat Percobaan:")
            for i, answer in enumerate(st.session_state.answers[-3:]):
                status = "✅ Benar" if answer['is_correct'] else "❌ Salah"
                st.write(f"Soal {i+1}: {answer['problem']} - {status}")
    else:
        st.success("🎉 Anda telah menyelesaikan semua soal aritmatika!")
        
        correct_count = sum(1 for ans in st.session_state.answers if ans['is_correct'])
        st.markdown(f"### Total Jawaban Benar: {correct_count}/5")
        
        if st.session_state.answers:
            st.markdown("#### Riwayat Percobaan:")
            for i, answer in enumerate(st.session_state.answers[-5:]):
                status = "✅ Benar" if answer['is_correct'] else "❌ Salah"
                st.write(f"Soal {i+1}: {answer['problem']} - {status}")
        
        col_btn = st.columns([1, 2, 1])
        with col_btn[1]:
            if st.button("➡️ Lanjut ke Kuesioner", key="proceed_to_questionnaire"):
                st.session_state.page = "dass21"
                st.rerun()

def cerita_page():
    if st.button("⬅️ Kembali ke Pengaturan", key="back_button"):
        st.session_state.page = "cerita_setup"
        st.rerun()
    
    if 'reading_start_time' not in st.session_state:
        st.session_state.reading_start_time = time.time()
        st.session_state.reading_time_up = False
    
    elapsed = time.time() - st.session_state.reading_start_time
    time_left = max(0, 3 - elapsed)
    
    selected_story = st.session_state.selected_story
    
    minutes, seconds = divmod(int(time_left), 60)
    st.markdown(f"### Waktu Membaca: {minutes:02d}:{seconds:02d}")
    
    auto_scroll_css = ""
    if st.session_state.auto_scroll:
        auto_scroll_css = f"""
        @keyframes autoscroll {{
            from {{ transform: translateY(0); }}
            to {{ transform: translateY(-100%); }}
        }}
        .gdocs-text {{
            animation: autoscroll {100/st.session_state.scroll_speed}s linear forwards;
            animation-delay: 1s;
            padding-bottom: 100vh !important;
        }}
        .scroll-container {{
            height: 80vh;
            overflow: hidden;
            position: relative;
        }}
        """
    
    st.markdown(f"""
    <style>
    .gdocs-text {{
        font-family: 'Arial', sans-serif;
        font-size: {st.session_state.font_size}px;
        line-height: 1.6;
        color: #333;
        max-width: 800px;
        margin: 0 auto;
        padding: 40px 30px;
        background-color: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        border-radius: 4px;
    }}
    .gdocs-text p {{
        margin-bottom: 1.2em;
        text-align: justify;
        font-size: {st.session_state.font_size}px;
    }}
    .gdocs-title {{
        font-family: 'Arial', sans-serif;
        font-size: {st.session_state.font_size + 10}px;
        font-weight: 600;
        color: #333;
        margin-bottom: 30px;
        text-align: center;
    }}
    {auto_scroll_css}
    </style>
    """, unsafe_allow_html=True)
    
    paragraphs = selected_story['isi'].split('\n\n')
    formatted_text = ""
    for para in paragraphs:
        if para.strip():
            formatted_text += f"<p>{para}</p>"
    
    st.markdown(f'<div class="gdocs-title">{selected_story["judul"]}</div>', unsafe_allow_html=True)
    
    if st.session_state.auto_scroll:
        st.markdown(f"""
        <div class="scroll-container">
            <div class="gdocs-text">{formatted_text}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="gdocs-text">{formatted_text}</div>', unsafe_allow_html=True)
    
    if time_left <= 0 and not st.session_state.reading_time_up:
        st.session_state.reading_time_up = True
        st.rerun()
    
    if st.session_state.reading_time_up:
        col_btn = st.columns([1, 2, 1])
        with col_btn[1]:
            if st.button("➡️ Lanjut ke Kuesioner", key="next_button"):
                st.session_state.page = "dass21"
                st.rerun()
    else:
        time.sleep(0.1)
        st.rerun()

def dass21_page():
    st.title(f"📋 Kuesioner DASS-21 ({st.session_state.current_condition})")
    st.markdown("---")
    
    st.markdown("""
    <div class='medium-font'>
    Silakan pilih kesesuaian pernyataan berikut dengan kondisi Anda selama seminggu terakhir
    </div>
    """, unsafe_allow_html=True)
    
    if 'dass21_responses' not in st.session_state:
        st.session_state.dass21_responses = {}
    
    for i, question in enumerate(DASS21_QUESTIONS):
        st.markdown(f"#### {i+1}. {question}")
        st.session_state.dass21_responses[i] = st.radio(
            f"q{i}",
            DASS21_OPTIONS,
            key=f"dass21_{i}",
            index=None,
            label_visibility="collapsed"
        )
        st.markdown("---")
    
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("➡️ Simpan Jawaban dan Lanjut", key="save_dass21"):
            if None in st.session_state.dass21_responses.values():
                st.error("Mohon jawab semua pertanyaan!")
            else:
                st.session_state.page = "acute_stress"
                st.rerun()

def acute_stress_page():
    st.title(f"📋 Kuesioner Stres Akut ({st.session_state.current_condition})")
    st.markdown("---")
    
    st.markdown("""
    <div class='medium-font'>
    Silakan jawab pertanyaan berikut berdasarkan apa yang Anda rasakan SAAT INI
    </div>
    """, unsafe_allow_html=True)
    
    if 'acute_stress_responses' not in st.session_state:
        st.session_state.acute_stress_responses = {}
    
    for i, question in enumerate(ACUTE_STRESS_QUESTIONS):
        st.markdown(f"#### {i+1}. {question}")
        st.session_state.acute_stress_responses[i] = st.radio(
            f"aq{i}",
            ACUTE_STRESS_OPTIONS,
            key=f"acute_{i}",
            index=None,
            label_visibility="collapsed"
        )
        st.markdown("---")
    
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("✅ Simpan Jawaban", key="save_acute"):
            if None in st.session_state.acute_stress_responses.values():
                st.error("Mohon jawab semua pertanyaan!")
            else:
                save_session_results(st.session_state.current_condition)
                
                conditions = ["Tahap 1", "Tahap 2", "Tahap 3"]
                current_index = conditions.index(st.session_state.current_condition)
                
                if current_index < len(conditions) - 1:
                    next_condition = conditions[current_index + 1]
                    st.session_state.page = next_condition.lower().replace(" ", "")
                else:
                    st.session_state.page = "hasil"
                
                if 'dass21_responses' in st.session_state:
                    del st.session_state.dass21_responses
                if 'acute_stress_responses' in st.session_state:
                    del st.session_state.acute_stress_responses
                
                st.rerun()

def hasil_page():
    st.title("📊 Hasil Semua Tahap")
    st.markdown("---")
    
    if 'results' in st.session_state and st.session_state.results:
        df = pd.DataFrame(st.session_state.results)
        
        st.markdown("### Ringkasan Hasil")
        
        conditions = ["Tahap 1", "Tahap 2", "Tahap 3"]
        for condition in conditions:
            condition_results = [r for r in st.session_state.results if condition in r["Kondisi"]]
            if condition_results:
                result = condition_results[0]
                with st.expander(f"Hasil {condition}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Informasi Peserta:**")
                        st.write(f"- Nama: {result['Nama']}")
                        st.write(f"- Umur: {result['Umur']}")
                        st.write(f"- Jenis Kelamin: {result['Jenis Kelamin']}")
                    with col2:
                        st.markdown("**Hasil Tes:**")
                        st.write(f"- Depresi: {result['Skor DASS21 - Depresi']} ({result['Kategori DASS21 - Depresi']})")
                        st.write(f"- Kecemasan: {result['Skor DASS21 - Kecemasan']} ({result['Kategori DASS21 - Kecemasan']})")
                        st.write(f"- Stres: {result['Skor DASS21 - Stres']} ({result['Kategori DASS21 - Stres']})")
                        st.write(f"- Stres Akut: {result['Skor Respons Stres Akut']} ({result['Kategori Respons Stres Akut']})")
        
        st.markdown("### Data Lengkap")
        st.dataframe(df)
        
        filename = f"hasil_stres_{st.session_state.data_diri['Nama']}"
        st.markdown(get_download_link(df, filename), unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("🔄 Mulai Kuesioner Baru", key="restart"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.page = "data_diri"
            st.rerun()
    else:
        st.warning("Belum ada data hasil. Silakan lengkapi semua tahap terlebih dahulu.")

# ============================================
# MAIN APP
# ============================================
def main():
    if 'page' not in st.session_state:
        st.session_state.page = "data_diri"
    
    # Initialize these variables if they don't exist
    if 'font_size' not in st.session_state:
        st.session_state.font_size = 16
    
    if 'auto_scroll' not in st.session_state:
        st.session_state.auto_scroll = False
        
    if 'scroll_speed' not in st.session_state:
        st.session_state.scroll_speed = 1.0
    
    pages = {
        "data_diri": data_diri_page,
        "tahap1": tahap1_page,
        "tahap2": tahap2_page,
        "tahap3": tahap3_page,
        "high_prep": high_prep_page,
        "high_presentation": high_presentation_page,
        "high_arithmetic": high_arithmetic_page,
        "cerita_setup": cerita_setup_page,
        "cerita": cerita_page,
        "presentation_prep": presentation_prep_page,
        "presentation": presentation_page,
        "arithmetic_task": arithmetic_task_page,
        "dass21": dass21_page,
        "acute_stress": acute_stress_page,
        "hasil": hasil_page
    }
    
    pages[st.session_state.page]()

if __name__ == "__main__":
    try:
        import docx
    except ImportError:
        st.error("Modul python-docx tidak terinstall. Silakan install dengan 'pip install python-docx'")
    
    main()
