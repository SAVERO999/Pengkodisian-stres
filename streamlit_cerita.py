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
# KONFIGURASI HALAMAN
# ============================================
st.set_page_config(
    page_title="Aplikasi Pengkondisian Stres",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS untuk styling konsisten
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
    /* Auto scroll to top */
    .reportview-container {
        overflow: auto;
    }
    .custom-card {
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# KONSTANTA APLIKASI
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
# FUNGSI UTILITAS
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
# FUNGSI PERHITUNGAN SKOR
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
                
            # Tambahkan statistik ringkasan untuk 30 soal
            all_answers = st.session_state.answers
            correct_answers = sum(1 for a in all_answers if a['is_correct'])
            result_data["Total_Soal_Aritmatika"] = len(all_answers)
            result_data["Total_Jawaban_Benar"] = correct_answers
            result_data["Persentase_Jawaban_Benar"] = round((correct_answers / len(all_answers)) * 100, 2) if all_answers else 0
    
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
    
    if condition == "Tahap 4":
        result_data["Jenis_Relaksasi"] = "PMR dan Musik"
        result_data["Durasi_Relaksasi"] = "9 menit 12 detik"
    
    if 'results' not in st.session_state:
        st.session_state.results = []
    st.session_state.results.append(result_data)
    
    if 'completed_conditions' not in st.session_state:
        st.session_state.completed_conditions = []
    st.session_state.completed_conditions.append(condition)

# ============================================
# HALAMAN APLIKASI
# ============================================
def data_diri_page():
    st.title("📝 Data Diri")
    st.markdown("---")
    
    # Reset riwayat jika nama berubah
    if 'previous_nama' not in st.session_state:
        st.session_state.previous_nama = ""
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Informasi Pribadi")
            nama = st.text_input("Nama Lengkap", key="nama")
            
            # Cek jika nama berubah dan hapus riwayat
            if nama != st.session_state.previous_nama and nama.strip() != "":
                if 'results' in st.session_state:
                    del st.session_state.results
                if 'completed_conditions' in st.session_state:
                    del st.session_state.completed_conditions
                st.session_state.previous_nama = nama
            
            umur = st.number_input("Umur", min_value=0, max_value=120, step=1, key="umur")
            gender = st.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"], key="gender")
        
        with col2:
            st.markdown("### Data Fisik")
            bb = st.number_input("Berat Badan (kg)", min_value=0.0, max_value=300.0, step=0.1, key="bb")
            tb = st.number_input("Tinggi Badan (cm)", min_value=0.0, max_value=300.0, step=0.1, key="tb")
    
    st.markdown("---")
    st.markdown("### Kebiasaan Sehari-hari")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            # Pertanyaan tentang konsumsi kopi dengan penjelasan tambahan
            st.markdown("""
            <div style='margin-bottom: 10px;'>
                <p><b>Berapa jam yang lalu terakhir minum kopi?</b></p>
                <p style='font-size: 14px; color: #666; margin-top: -5px;'>
                    * Jika Anda tidak minum kopi sama sekali, masukkan angka 0<br>
                    * Jika Anda minum kopi, masukkan berapa jam yang lalu (contoh: 2 untuk 2 jam yang lalu)
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            kopi_jam = st.number_input(
                "Jam terakhir konsumsi kopi", 
                min_value=0, 
                max_value=72, 
                step=1,
                help="Untuk pengukuran stres yang akurat, disarankan tidak minum kopi minimal 1 jam sebelum tes. Masukkan 0 jika tidak minum kopi.",
                label_visibility="collapsed"
            )
            
        with col2:
            # Pertanyaan tentang durasi tidur
            durasi_tidur = st.number_input(
                "Berapa jam Anda tidur tadi malam?", 
                min_value=0, 
                max_value=12, 
                step=1,
                help="Durasi tidur mempengaruhi tingkat stres"
            )
    
    st.markdown("---")
    col_btn = st.columns([1, 3, 1])
    with col_btn[1]:
        if st.button("✅ Simpan dan Lanjut ke Tahap 1", use_container_width=True, key="save_personal_data"):
            if not nama or umur <= 0 or bb <= 0 or tb <= 0:
                st.error("Mohon lengkapi semua data dengan benar!")
            elif kopi_jam < 1 and kopi_jam != 0:  # Memeriksa jika minum kopi < 1 jam yang lalu dan bukan 0 (tidak minum)
                st.warning("Untuk hasil pengukuran stres yang akurat, disarankan tidak minum kopi minimal 1 jam sebelum tes. Anda bisa melanjutkan, tetapi hasil mungkin terpengaruh.")
                st.session_state.data_diri = {
                    "Nama": nama, "Umur": umur, "Jenis Kelamin": gender,
                    "Berat Badan (kg)": bb, "Tinggi Badan (cm)": tb,
                    "Terakhir Minum Kopi (jam)": "Tidak minum kopi" if kopi_jam == 0 else f"{kopi_jam} jam yang lalu",
                    "Durasi Tidur (jam)": durasi_tidur,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Pastikan riwayat kosong saat memulai
                if 'results' not in st.session_state:
                    st.session_state.results = []
                if 'completed_conditions' not in st.session_state:
                    st.session_state.completed_conditions = []
                    
                st.session_state.page = "tahap1"
                st.rerun()
            else:
                st.session_state.data_diri = {
                    "Nama": nama, "Umur": umur, "Jenis Kelamin": gender,
                    "Berat Badan (kg)": bb, "Tinggi Badan (cm)": tb,
                    "Terakhir Minum Kopi (jam)": "Tidak minum kopi" if kopi_jam == 0 else f"{kopi_jam} jam yang lalu",
                    "Durasi Tidur (jam)": durasi_tidur,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Pastikan riwayat kosong saat memulai
                if 'results' not in st.session_state:
                    st.session_state.results = []
                if 'completed_conditions' not in st.session_state:
                    st.session_state.completed_conditions = []
                    
                st.session_state.page = "tahap1"
                st.rerun()
def rest_timer_page():
    # First, clear any remaining arithmetic history when entering this page
    if 'answers' in st.session_state:
        del st.session_state.answers
    
    # Clear the page completely
    st.empty()
    
    st.title("⏳ Waktu Istirahat")
    st.markdown("---")
    
    # Initialize timer state
    if 'rest_start_time' not in st.session_state:
        st.session_state.rest_start_time = time.time()
        st.session_state.timer_finished = False
    
    # Calculate remaining time
    current_time = time.time()
    elapsed = current_time - st.session_state.rest_start_time
    time_left = max(0, 60 - elapsed)  
    
    st.markdown("""
    <div class='medium-font'>
    Silakan beristirahat sejenak sebelum melanjutkan ke tahap berikutnya.
    </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    progress = min(elapsed / 60, 1.0)  
    st.progress(progress)
    
    # Display remaining time
    minutes = int(time_left // 60)
    seconds = int(time_left % 60)
    time_display = st.empty()
    time_display.markdown(f"### Waktu Istirahat Tersisa: {minutes:02d}:{seconds:02d}")
    
    # Container for the button - will only be filled when timer is done
    button_container = st.empty()
    
    if time_left <= 0:
        # Clear all arithmetic-related state
        keys_to_clear = [
            'arithmetic_problems', 
            'current_problem', 
            'answers', 
            'task_completed',
            'arithmetic_history'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        st.session_state.timer_finished = True
        time_display.markdown("### Waktu istirahat telah habis!")
        
        # Only now we add the button to the container
        with button_container.container():
            col_btn = st.columns([1, 2, 1])
            with col_btn[1]:
                if st.button("➡️ Lanjut ke Tahap Berikutnya", key="next_after_rest"):
                    # Clear timer state
                    keys_to_clear = ['rest_start_time', 'timer_finished']
                    for key in keys_to_clear:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    # Determine next page based on current condition
                    if st.session_state.current_condition == "Tahap 1":
                        st.session_state.page = "dass21"
                    elif st.session_state.current_condition == "Tahap 2":
                        st.session_state.page = "dass21"
                    elif st.session_state.current_condition == "Tahap 3":
                        st.session_state.page = "dass21"
                    elif st.session_state.current_condition == "Tahap 4":
                        st.session_state.page = "dass21"
                    st.rerun()
    else:
        # Don't add anything to the button container when timer is running
        # This ensures no button will appear
        time.sleep(0.1)
        st.rerun()
        
def tahap1_page():
    st.title("📖 Tahap 1 - Membaca Materi Netral")
    st.markdown("---")
    
    st.markdown("""
    <div class='medium-font'>
    <b>Instruksi:</b><br>
    Anda akan membaca materi netral selama 5 menit. 
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
    1. Anda akan mempersiapkan presentasi tentang topik netral selama 3 menit<br>
    2. Presentasikan di depan evaluator selama 5 menit<br>
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
    1. Anda akan mempersiapkan presentasi tentang "kelemahan diri" selama 3 menit<br>
    2. Presentasikan di depan evaluator selama 5 menit<br>
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

def tahap4_page():
    st.title("🧘 Tahap 4 - Relaksasi")
    st.markdown("---")
    
    st.markdown("""
    <div class='medium-font'>
    <b>Instruksi:</b><br>
    Anda akan melalui 3 sesi relaksasi:<br>
    1. Progressive Muscle Relaxation (PMR)>
    2. Mendengarkan musik menenangkan<br>
    3. Evaluasi perasaan setelah relaksasi <br><br>
    Tekan tombol di bawah untuk memulai.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("▶️ Mulai Sesi Relaksasi", key="start_relaxation"):
            st.session_state.current_condition = "Tahap 4"
            st.session_state.page = "pmr_session"
            st.rerun()

def pmr_session_page():
    if 'pmr_stage' not in st.session_state:
        st.session_state.pmr_stage = "instructions"
        st.session_state.pmr_start_time = None
    
    if st.session_state.pmr_stage == "instructions":
        st.title("🧘 Instruksi Progressive Muscle Relaxation (PMR)")
        st.markdown("---")
        
        st.markdown("""
        <div class='medium-font'>
        <b>Instruksi PMR:</b><br>
        1. Anda akan menonton video panduan PMR <br>
        2. Klik tombol play pada video untuk memulai sesi PMR<br>
        3. Ikuti semua instruksi yang diberikan dalam video<br>        
        4. Cari posisi yang nyaman sebelum memulai<br>
    
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        col_btn = st.columns([1, 2, 1])
        with col_btn[1]:
            if st.button("▶️ Mulai Sesi PMR", key="start_pmr_session"):
                st.session_state.pmr_stage = "session"
                st.rerun()
    
    elif st.session_state.pmr_stage == "session":
        st.title("🧘 Progressive Muscle Relaxation (PMR)")
        st.markdown("---")
        
        # YouTube Video Embed
        st.markdown("""
        <div style="display: flex; justify-content: center; margin: 20px 0;">
            <iframe width="560" height="315" 
            src="https://www.youtube.com/embed/4G--3DHybhM?autoplay=1&rel=0" 
            frameborder="0" 
            allowfullscreen>
            </iframe>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize PMR session timer
        if st.session_state.pmr_start_time is None:
            st.session_state.pmr_start_time = time.time()
        
        elapsed = time.time() - st.session_state.pmr_start_time
        time_left = max(0, 270 - elapsed)  # 4 menit 30 detik = 270 detik
        
        # Progress bar
        st.progress(min(elapsed/270, 1.0))
        st.markdown(f"### Waktu PMR Tersisa: {int(time_left//60):02d}:{int(time_left%60):02d}")
        
        if time_left <= 0:
            col_btn = st.columns([1, 2, 1])
            with col_btn[1]:
                if st.button("➡️ Lanjut ke Sesi Musik", key="next_to_music"):
                    st.session_state.page = "music_instructions"
                    st.rerun()
        else:
            time.sleep(1)
            st.rerun()

def music_instructions_page():
    st.title("🎵 Instruksi Musik Menenangkan")
    st.markdown("---")
    
    st.markdown("""
    <div class='medium-font'>
    <b>Instruksi:</b><br>
    1. Anda akan mendengarkan musik relaksasi selama 5 menit<br>
    2. Klik tombol play pada musik untuk memulai sesi PMR<br>            
    3. Fokus pada pernapasan dan relaksasi<br>
    4. Tutup mata jika membantu Anda lebih rileks<br><br>

    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("▶️ Mulai Sesi Musik", key="start_music_session"):
            st.session_state.page = "music_session"
            st.rerun()

def music_session_page():
    st.title("🎵 Sesi Musik Menenangkan")
    st.markdown("---")
    
    if 'music_start_time' not in st.session_state:
        st.session_state.music_start_time = time.time()
    
    # Audio player dengan musik The Blue Danube
    audio_file = open('the-blue-danube-op-314-johann-strauss-ii-arranged-for-solo-piano-212208 (mp3cut.net)mp3', 'rb')
    audio_bytes = audio_file.read()
    
    st.audio(audio_bytes, format='audio/mp3', start_time=0)
    
    elapsed = time.time() - st.session_state.music_start_time
    time_left = max(0, 330 - elapsed)  # 5 menit = 300 detik
    
    # Progress bar
    st.progress(min(elapsed/330, 1.0))
    st.markdown(f"### Waktu Musik Tersisa: {int(time_left//60):02d}:{int(time_left%60):02d}")
    
    if time_left <= 0:
        col_btn = st.columns([1, 2, 1])
        with col_btn[1]:
            if st.button("➡️ Lanjut ke Evaluasi Perasaan", key="next_to_feeling_eval"):
                st.session_state.page = "feeling_evaluation"
                st.rerun()
    else:
        time.sleep(1)
        st.rerun()

def feeling_evaluation_page():
    st.title("💭 Evaluasi Perasaan Setelah Relaksasi")
    st.markdown("---")
    
    # Initialize all session state variables
    if 'feeling_stage' not in st.session_state:
        st.session_state.feeling_stage = "preparation"
        st.session_state.feeling_response = ""
        st.session_state.prep_start_time = time.time()
        st.session_state.presentation_start_time = None
        st.session_state.feeling_completed = False
        st.session_state.show_continue_button = False
    
    # Preparation Stage
    if st.session_state.feeling_stage == "preparation":
        st.markdown("""
        <div class='medium-font'>
        <b>Instruksi Persiapan (1 menit):</b><br>
        1. Pikirkan perubahan emosi yang Anda rasakan<br>
        2. Presentasikan secara jelas dan terstruktur<br>
        3. Siapkan poin-poin utama yang ingin disampaikan <br>
        4. Anda akan presentasikan selama 3 menit
        </div>
        """, unsafe_allow_html=True)
        
        elapsed = time.time() - st.session_state.prep_start_time
        prep_time_left = max(0, 60 - elapsed)
        
        st.progress(min(elapsed/60, 1.0))
        st.markdown(f"### Waktu Persiapan Tersisa: {int(prep_time_left//60):02d}:{int(prep_time_left%60):02d}")
        
        st.session_state.feeling_response = st.text_area(
            "Tulis evaluasi perasaan Anda:",
            value=st.session_state.feeling_response,
            height=200,
            key="feeling_prep_input"
        )
        
        # Only allow continue after time is up
        if prep_time_left <= 0:
            st.session_state.show_continue_button = True
        
        if st.session_state.show_continue_button:
            col_btn = st.columns([1, 2, 1])
            with col_btn[1]:
                if st.button("🎤 Lanjut ke Presentasi", key="continue_to_presentation"):
                    st.session_state.feeling_stage = "presentation"
                    st.session_state.presentation_start_time = time.time()
                    st.session_state.show_continue_button = False
                    st.rerun()
        else:
            time.sleep(0.1)
            st.rerun()
    
    # Presentation Stage
    elif st.session_state.feeling_stage == "presentation":
        st.markdown("### Silakan sampaikan evaluasi Anda kepada evaluator")
        
        elapsed = time.time() - st.session_state.presentation_start_time
        presentation_time_left = max(0, 180 - elapsed)
        
        st.progress(min(elapsed/180, 1.0))
        st.markdown(f"### Waktu Presentasi Tersisa: {int(presentation_time_left//60):02d}:{int(presentation_time_left%60):02d}")
        
        st.markdown("#### Catatan Anda:")
        st.markdown(f'<div class="custom-card">{st.session_state.feeling_response}</div>', unsafe_allow_html=True)
        
        # Only allow continue after time is up
        if presentation_time_left <= 0:
            st.session_state.feeling_completed = True
            st.session_state.show_continue_button = True
        
        if st.session_state.show_continue_button:
            col_btn = st.columns([1, 2, 1])
            with col_btn[1]:
                if st.button("➡️ Lanjut ke Istirahat", key="proceed_to_rest"):
                    # Save response
                    if 'relaxation_responses' not in st.session_state:
                        st.session_state.relaxation_responses = []
                    st.session_state.relaxation_responses.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "response": st.session_state.feeling_response
                    })
                    
                    # Clear state
                    keys_to_clear = [
                        'feeling_stage', 'feeling_response', 
                        'prep_start_time', 'presentation_start_time',
                        'feeling_completed', 'show_continue_button'
                    ]
                    for key in keys_to_clear:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    st.session_state.page = "rest_timer"
                    st.rerun()
        else:
            time.sleep(0.1)
            st.rerun()

def high_prep_page():
    st.title("📝 Persiapan Presentasi - Tahap 3")
    st.markdown("---")
    
    if 'high_prep_start_time' not in st.session_state:
        st.session_state.high_prep_start_time = time.time()
    
    elapsed = time.time() - st.session_state.high_prep_start_time
    prep_time_left = max(0, 180 - elapsed)
    
    if 'high_presentation_topic' not in st.session_state:
        st.session_state.high_presentation_topic = random.choice(["Kelemahan Anda"])
    
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
    presentation_time_left = max(0, 300 - elapsed)
    
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
    time_left = max(0, 300 - elapsed)
    
    minutes, seconds = divmod(int(time_left), 60)
    st.markdown(f"### Waktu Tersisa: {minutes:02d}:{seconds:02d}")
    
    progress = min(elapsed / 300, 1.0)
    st.progress(progress)
    
    if time_left <= 0:
        st.success("Waktu tugas aritmatika telah habis!")
        col_btn = st.columns([1, 2, 1])
        with col_btn[1]:
            if st.button("➡️ Lanjut ke Istirahat", key="finish_high_arithmetic"):
                st.session_state.page = "rest_timer"
                st.rerun()
    else:
        time.sleep(1)
        st.rerun()

import time
import streamlit as st

def presentation_page():
    st.title("🎤 Presentasi - Tahap 2")
    st.markdown("---")
    
    st.markdown("### Topik Presentasi Anda:")
    st.markdown(f"<div style='padding:10px; background-color:#cce5ff; border-radius:5px; font-size:24px; font-weight:bold;'>{st.session_state.selected_topic}</div>", unsafe_allow_html=True)
    st.markdown("### Catatan Persiapan Anda:")
    st.write(st.session_state.presentation_notes)
    
    # Timer section
    st.markdown("---")
    st.markdown("### ⏳ Timer Presentasi (5 menit)")
    
    # Initialize timer only once
    if 'timer_started' not in st.session_state:
        st.session_state.timer_started = True
        st.session_state.start_time = time.time()
        st.session_state.timer_expired = False
    
    # Calculate remaining time
    current_time = time.time()
    elapsed_time = current_time - st.session_state.start_time
    remaining_time = max(300 - elapsed_time, 0)  # 5 minutes = 300 seconds
    
    # Display timer
    if remaining_time > 0 and not st.session_state.timer_expired:
        minutes, seconds = divmod(int(remaining_time), 60)
        timer_text = f"⏱️ Waktu tersisa: {minutes:02d}:{seconds:02d}"
        progress = remaining_time / 300
        st.progress(progress)
        
        # Placeholder untuk timer yang terus update
        timer_placeholder = st.empty()
        timer_placeholder.markdown(f"<h3 style='text-align:center; color:red;'>{timer_text}</h3>", unsafe_allow_html=True)
        
        # Auto-rerun untuk update timer
        if remaining_time > 0:
            st.rerun()
    else:
        st.session_state.timer_expired = True
        st.progress(0)
        st.markdown("<h3 style='text-align:center; color:red;'>⏰ Waktu presentasi habis!</h3>", unsafe_allow_html=True)
        
        # Tombol hanya muncul ketika timer habis
        col_btn = st.columns([1, 2, 1])
        with col_btn[1]:
            if st.button("➡️ Lanjut ke Tugas Aritmatika", key="finish_presentation"):
                st.session_state.page = "arithmetic_task"
                st.rerun()
def presentation_prep_page():
    st.title("📝 Persiapan Presentasi - Tahap 2")
    st.markdown("---")
    
    if 'prep_start_time' not in st.session_state:
        st.session_state.prep_start_time = time.time()
    
    elapsed = time.time() - st.session_state.prep_start_time
    time_left = max(0, 180 - elapsed)

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
    
    # Timer section
    st.markdown("---")
    st.markdown("### ⏳ Timer Presentasi (5 menit)")
    
    if 'start_time' not in st.session_state:
        st.session_state.start_time = time.time()
        st.session_state.timer_expired = False
    
    current_time = time.time()
    elapsed_time = current_time - st.session_state.start_time
    remaining_time = max(300 - elapsed_time, 0)  # 5 minutes = 300 seconds
    
    if remaining_time > 0 and not st.session_state.timer_expired:
        minutes, seconds = divmod(int(remaining_time), 60)
        timer_text = f"⏱️ Waktu tersisa: {minutes:02d}:{seconds:02d}"
        st.progress(remaining_time / 300)
        st.markdown(f"<h3 style='text-align:center; color:red;'>{timer_text}</h3>", unsafe_allow_html=True)
    else:
        st.session_state.timer_expired = True
        st.markdown("<h3 style='text-align:center; color:red;'>⏰ Waktu presentasi habis!</h3>", unsafe_allow_html=True)
        
        # Tombol hanya muncul ketika timer habis
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
    3. Total ada 10 soal yang harus diselesaikan
    </div>
    """, unsafe_allow_html=True)
    
    # Inisialisasi masalah aritmatika
    if 'arithmetic_problems' not in st.session_state:
        st.session_state.arithmetic_problems = []
        st.session_state.current_problem = 0
        st.session_state.answers = []
        st.session_state.task_completed = False
        
        # Meningkatkan jumlah soal menjadi 30 dengan angka ratusan (3 digit)
        for _ in range(10):
            if random.random() > 0.5:
                # Pengurangan dengan angka 3 digit (ratusan)
                a = random.randint(500, 999)  # 3 digit (ratusan)
                b = random.randint(100, 499)  # 3 digit (ratusan), lebih kecil dari a
                st.session_state.arithmetic_problems.append({
                    'type': 'pengurangan',
                    'question': f"{a} - {b} = ?",
                    'answer': a - b
                })
            else:
                # Pembagian yang menggunakan angka ratusan
                b = random.randint(10, 99)  # divisor 2 digit
                answer = random.randint(10, 99)  # hasil pembagian 2 digit
                a = b * answer  # hasil perkalian minimal 3 digit (ratusan)
                
                # Pastikan a adalah angka ratusan (3 digit)
                while a < 100 or a > 999:
                    b = random.randint(10, 99)
                    answer = random.randint(10, 99)
                    a = b * answer
                
                st.session_state.arithmetic_problems.append({
                    'type': 'pembagian',
                    'question': f"{a} ÷ {b} = ?",
                    'answer': answer
                })

    if not st.session_state.task_completed:
        problem = st.session_state.arithmetic_problems[st.session_state.current_problem]
        
        st.markdown(f"### Soal {st.session_state.current_problem + 1}/10")
        st.markdown(f"<div class='big-font'>{problem['question']}</div>", unsafe_allow_html=True)
        
        # Gunakan key unik untuk setiap soal
        answer_key = f"answer_{st.session_state.current_problem}"
        user_answer = st.number_input(
            "Jawaban Anda:", 
            key=answer_key,
            step=1,
            value=None  # Nilai awal kosong
        )
        
        if st.button("✅ Submit Jawaban", key=f"submit_{st.session_state.current_problem}"):
            if user_answer is None:
                st.error("Mohon masukkan jawaban!")
            else:
                is_correct = (user_answer == problem['answer'])
                
                st.session_state.answers.append({
                    'problem': problem['question'],
                    'user_answer': user_answer,
                    'is_correct': is_correct,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
                
                if is_correct:
                    st.session_state.current_problem += 1
                    
                    if st.session_state.current_problem >= 10:  # Diubah dari 5 menjadi 30
                        st.session_state.task_completed = True
                    st.rerun()  # Refresh untuk soal baru
                else:
                    st.rerun()
        
        st.progress((st.session_state.current_problem)/10)  # Diubah dari 5 menjadi 30
    else:
        st.success("🎉 Anda telah menyelesaikan semua soal aritmatika!")
        
        col_btn = st.columns([1, 2, 1])
        with col_btn[1]:
            if st.button("➡️ Lanjut ke Istirahat", key="proceed_to_rest"):
                # Bersihkan state aritmatika
                keys_to_clear = ['arithmetic_problems', 'current_problem', 
                               'answers', 'task_completed']
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.page = "rest_timer"
                st.rerun()

def presentation_page():
    st.title("🎤 Presentasi - Tahap 2")
    st.markdown("---")
    
    # Initialize session state variables if they don't exist
    if 'selected_topic' not in st.session_state:
        st.session_state.selected_topic = "Topik belum dipilih"
    if 'presentation_notes' not in st.session_state:
        st.session_state.presentation_notes = "Catatan belum dibuat"
    
    st.markdown("### Topik Presentasi Anda:")
    st.markdown(f"<div style='padding:10px; background-color:#cce5ff; border-radius:5px; font-size:24px; font-weight:bold;'>{st.session_state.selected_topic}</div>", unsafe_allow_html=True)
    st.markdown("### Catatan Persiapan Anda:")
    st.write(st.session_state.presentation_notes)
    
    # Timer section
    st.markdown("---")
    st.markdown("### ⏳ Timer Presentasi (5 menit)")
    
    # Initialize timer state
    if 'timer_started' not in st.session_state:
        st.session_state.timer_started = True
        st.session_state.start_time = time.time()
        st.session_state.timer_expired = False
    
    # Calculate remaining time
    current_time = time.time()
    elapsed_time = current_time - st.session_state.start_time
    remaining_time = max(300 - elapsed_time, 0)  # 5 minutes = 300 seconds
    
    # Create timer display placeholder
    timer_placeholder = st.empty()
    progress_bar = st.progress(0)
    
    if remaining_time > 0 and not st.session_state.timer_expired:
        minutes, seconds = divmod(int(remaining_time), 60)
        timer_text = f"⏱️ Waktu tersisa: {minutes:02d}:{seconds:02d}"
        progress = remaining_time / 300
        
        # Update display
        progress_bar.progress(progress)
        timer_placeholder.markdown(f"<h3 style='text-align:center; color:red;'>{timer_text}</h3>", unsafe_allow_html=True)
        
        # Auto-rerun for countdown effect
        time.sleep(1)
        st.rerun()
    else:
        st.session_state.timer_expired = True
        progress_bar.progress(0)
        timer_placeholder.markdown("<h3 style='text-align:center; color:red;'>⏰ Waktu presentasi habis!</h3>", unsafe_allow_html=True)
        
        # Show continue button only when time is up
        col_btn = st.columns([1, 2, 1])
        with col_btn[1]:
            if st.button("➡️ Lanjut ke Tugas Aritmatika", key="finish_presentation"):
                st.session_state.page = "arithmetic_task"
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
                # Scroll to top
                components.html(
                    """
                    <script>
                    window.parent.document.querySelector('section.main').scrollTo(0, 0);
                    </script>
                    """,
                    height=0
                )
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
                
                conditions = ["Tahap 1", "Tahap 2", "Tahap 3", "Tahap 4"]
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
                
                # Scroll to top
                components.html(
                    """
                    <script>
                    window.parent.document.querySelector('section.main').scrollTo(0, 0);
                    </script>
                    """,
                    height=0
                )
                st.rerun()

def hasil_page():
    st.title("📊 Hasil Semua Tahap")
    st.markdown("---")
    
    if 'results' in st.session_state and st.session_state.results:
        df = pd.DataFrame(st.session_state.results)
        
        st.markdown("### Ringkasan Hasil")
        
        conditions = ["Tahap 1", "Tahap 2", "Tahap 3", "Tahap 4"]
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
                        st.write(f"- Terakhir Minum Kopi: {result['Terakhir Minum Kopi (jam)']} jam yang lalu")
                        st.write(f"- Durasi Tidur: {result['Durasi Tidur (jam)']} jam")
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
        "tahap4": tahap4_page,
        "rest_timer": rest_timer_page,
        "pmr_session": pmr_session_page,
        "music_instructions": music_instructions_page,
        "music_session": music_session_page,
        "feeling_evaluation": feeling_evaluation_page,
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

