import streamlit as st
import pandas as pd
import random
import re
import os
import base64
import time
import io
import numpy as np
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
    "Saya merasakan kesulitan bernapas",
    "Saya merasa detak jantung yang kuat",
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
        
        # Tambahkan data dari MIST jika tersedia
        if 'mist_results' in st.session_state:
            result_data["MIST_Total_Soal"] = st.session_state.mist_results['total_questions']
            result_data["MIST_Jawaban_Benar"] = st.session_state.mist_results['correct_answers']
            result_data["MIST_Jawaban_Salah"] = st.session_state.mist_results['incorrect_answers']
            result_data["MIST_Rata_Waktu_Respons"] = round(st.session_state.mist_results['average_response_time'], 2)
            result_data["MIST_Level_Akhir"] = st.session_state.mist_results['final_difficulty_level']
            
            # Tambahkan riwayat soal MIST
            if 'history' in st.session_state.mist_results:
                for i, item in enumerate(st.session_state.mist_results['history']):
                    result_data[f"MIST_Soal_{i+1}"] = item['question']
                    result_data[f"MIST_Jawaban_{i+1}"] = item['user_answer']
                    result_data[f"MIST_Benar_{i+1}"] = item['correct']
                    result_data[f"MIST_Waktu_Respons_{i+1}"] = round(item['response_time'], 2)
                    result_data[f"MIST_Level_{i+1}"] = item['difficulty_level']
    
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
                st.session_state.page = "tahap1"
                st.rerun()

def rest_timer_page():
    # Skip rest timer for Tahap 4 and go directly to acute_stress
    if 'current_condition' in st.session_state and st.session_state.current_condition == "Tahap 4":
        # Clear all MIST and arithmetic state variables
        keys_to_clear = [
            # Existing arithmetic keys
            'arithmetic_problems', 
            'current_problem', 
            'answers', 
            'task_completed',
            'arithmetic_history',
            'arithmetic_start_time',
            'arithmetic_time_up',
            'high_arithmetic_history',
            'high_arithmetic_attempts',
            'high_arithmetic_correct_count',
            'answer_form',
            'answer_0',
            'answer_1',
            
            # MIST-related keys
            'mist_initialized',
            'current_question',
            'current_answer',
            'correct_answer',
            'response_status',
            'question_start_time',
            'question_time_limit',
            'total_elapsed_time',
            'start_time',
            'last_update_time',
            'last_sound_time',
            'should_clear_response',
            'show_response_until',
            'consecutive_correct',
            'consecutive_incorrect',
            'difficulty_level',
            'response_times',
            'average_response_time',
            'fake_average_correct_rate',
            'user_correct_rate',
            'game_over',
            'MIST_TOTAL_DURATION',
            'correct_answers',
            'incorrect_answers',
            'total_questions',
            'mist_history'
        ]
        
        # Remove all keys from session state
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Use safer JavaScript to clean up UI elements
        components.html(
            """
            <script>
            // Use a safer approach to clean elements - hide them instead of removing
            function safeCleanup() {
                try {
                    // Hide elements rather than removing them
                    const elementsToHide = window.parent.document.querySelectorAll(
                        '.stProgress, .stButton, .stTextInput, .stNumberInput, ' +
                        '.big-font, .answer-font, .result-correct, .result-incorrect, ' +
                        '.stMetric'
                    );
                    
                    elementsToHide.forEach(el => {
                        if (el && el.style) {
                            el.style.display = 'none';
                        }
                    });
                    
                    // Stop any audio that might be playing
                    const audioElements = window.parent.document.querySelectorAll('audio');
                    audioElements.forEach(audio => {
                        if (audio) {
                            audio.pause();
                            if (audio.parentNode) {
                                try {
                                    audio.parentNode.removeChild(audio);
                                } catch (e) {
                                    // Just hide it if we can't remove it
                                    audio.style.display = 'none';
                                }
                            }
                        }
                    });
                    
                    // Try to reset any forms
                    const forms = window.parent.document.querySelectorAll('form');
                    forms.forEach(form => {
                        if (form) {
                            try {
                                form.reset();
                            } catch (e) {
                                // If reset fails, try to hide
                                if (form.style) {
                                    form.style.display = 'none';
                                }
                            }
                        }
                    });
                    
                    console.log("Cleanup completed successfully");
                } catch (e) {
                    console.log("Cleanup error:", e);
                }
            }
            
            // Execute the cleanup
            safeCleanup();
            </script>
            """,
            height=0
        )
        
        # Wait a tiny bit to ensure everything is processed
        time.sleep(0.1)
        
        # Set up default DASS21 responses if needed
        if 'dass21_responses' not in st.session_state:
            st.session_state.dass21_responses = {}
            for i in range(len(DASS21_QUESTIONS)):
                st.session_state.dass21_responses[i] = DASS21_OPTIONS[0]
        
        # Go directly to acute stress page
        st.session_state.page = "acute_stress"
        st.rerun()
    
    # Completely reset the page first for other conditions
    st.empty()
    
    # Clear all MIST and arithmetic state variables
    keys_to_clear = [
        # Existing arithmetic keys
        'arithmetic_problems', 
        'current_problem', 
        'answers', 
        'task_completed',
        'arithmetic_history',
        'arithmetic_start_time',
        'arithmetic_time_up',
        'high_arithmetic_history',
        'high_arithmetic_attempts',
        'high_arithmetic_correct_count',
        'answer_form',
        'answer_0',
        'answer_1',
        
        # MIST-related keys - complete list
        'mist_initialized',
        'current_question',
        'current_answer',
        'correct_answer',
        'response_status',
        'question_start_time',
        'question_time_limit',
        'total_elapsed_time',
        'start_time',
        'last_update_time',
        'last_sound_time',
        'should_clear_response',
        'show_response_until',
        'consecutive_correct',
        'consecutive_incorrect',
        'difficulty_level',
        'response_times',
        'average_response_time',
        'fake_average_correct_rate',
        'user_correct_rate',
        'game_over',
        'MIST_TOTAL_DURATION',
        'correct_answers',
        'incorrect_answers',
        'total_questions',
        'mist_history'
    ]
    
    # Remove all keys from session state
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Use safer JavaScript to clean up UI elements
    components.html(
        """
        <script>
        // Use a safer approach to clean elements - hide them instead of removing
        function safeCleanup() {
            try {
                // Hide elements rather than removing them
                const elementsToHide = window.parent.document.querySelectorAll(
                    '.stProgress, .stButton, .stTextInput, .stNumberInput, ' +
                    '.big-font, .answer-font, .result-correct, .result-incorrect, ' +
                    '.stMetric'
                );
                
                elementsToHide.forEach(el => {
                    if (el && el.style) {
                        el.style.display = 'none';
                    }
                });
                
                // Stop any audio that might be playing
                const audioElements = window.parent.document.querySelectorAll('audio');
                audioElements.forEach(audio => {
                    if (audio) {
                        audio.pause();
                        if (audio.parentNode) {
                            try {
                                audio.parentNode.removeChild(audio);
                            } catch (e) {
                                // Just hide it if we can't remove it
                                audio.style.display = 'none';
                            }
                        }
                    }
                });
                
                // Try to reset any forms
                const forms = window.parent.document.querySelectorAll('form');
                forms.forEach(form => {
                    if (form) {
                        try {
                            form.reset();
                        } catch (e) {
                            // If reset fails, try to hide
                            if (form.style) {
                                form.style.display = 'none';
                            }
                        }
                    }
                });
                
                console.log("Cleanup completed successfully");
            } catch (e) {
                console.log("Cleanup error:", e);
            }
        }
        
        // Execute the cleanup
        safeCleanup();
        </script>
        """,
        height=0
    )
    
    # Wait a tiny bit to ensure everything is processed
    time.sleep(0.1)
    
    # Start fresh with a new page
    st.title("⏳ Waktu Istirahat")
    st.markdown("---")
    
    # Inisialisasi state timer
    if 'rest_start_time' not in st.session_state:
        st.session_state.rest_start_time = time.time()
        st.session_state.timer_finished = False
    
    # Hitung waktu yang tersisa
    current_time = time.time()
    elapsed = current_time - st.session_state.rest_start_time
    time_left = max(0, 60 - elapsed)  # 10 detik istirahat
    
    st.markdown("""
    <div class='medium-font'>
    Silakan beristirahat sejenak sebelum melanjutkan ke tahap berikutnya.
    </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    progress = min(elapsed / 60, 1.0)  
    st.progress(progress)
    
    # Tampilkan waktu tersisa
    minutes = int(time_left // 60)
    seconds = int(time_left % 60)
    time_display = st.empty()
    time_display.markdown(f"### Waktu Istirahat Tersisa: {minutes:02d}:{seconds:02d}")
    
    # Container untuk tombol - hanya diisi ketika timer selesai
    button_container = st.empty()
    
    if time_left <= 0:
        st.session_state.timer_finished = True
        time_display.markdown("### Waktu istirahat telah habis!")
        
        # Sekarang kita tambahkan tombol ke container
        with button_container.container():
            col_btn = st.columns([1, 2, 1])
            with col_btn[1]:
                if st.button("➡️ Lanjut ke Kuesioner", key="next_after_rest"):
                    # Bersihkan state timer
                    keys_to_clear = ['rest_start_time', 'timer_finished']
                    for key in keys_to_clear:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    # Tentukan halaman berikutnya berdasarkan kondisi saat ini
                    if st.session_state.current_condition == "Tahap 1":
                        st.session_state.page = "dass21"
                    else:
                        if 'dass21_responses' not in st.session_state:
                            st.session_state.dass21_responses = {}
                            for i in range(len(DASS21_QUESTIONS)):
                                st.session_state.dass21_responses[i] = DASS21_OPTIONS[0]
                        
                        st.session_state.page = "acute_stress"
                    st.rerun()
    else:
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
    3. Dilanjutkan dengan tugas aritmatika selama 5 menit
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
    st.title("🎤 Tahap 3")
    st.markdown("---")
    
    st.markdown("""
    <div class='medium-font'>
    <b>Instruksi:</b><br>
    1. Anda akan mengerjakan tugas aritmatika sulit (pengurangan serial 13 dari 1022)<br>
    2. Dilanjutkan dengan simulasi MIST (Montreal Imaging Stress Task)
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("▶️ Mulai Tahap 3", key="start_tahap3"):
            st.session_state.current_condition = "Tahap 3"
            st.session_state.page = "high_arithmetic"
            st.rerun()

def tahap4_page():
    st.title("🧘 Tahap 4 ")
    st.markdown("---")
    
    st.markdown("""
    <div class='medium-font'>
    <b>Instruksi:</b><br>
    Anda akan melalui 3 sesi relaksasi:<br>
    1. Progressive Muscle Relaxation (PMR)<br>
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
        time_left = max(0, 2 - elapsed)  # 4 menit 30 detik = 270 detik
        
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
    audio_file = open('the-blue-danube-op-314-johann-strauss-ii-arranged-for-solo-piano-212208 (mp3cut.net).mp3', 'rb')
    audio_bytes = audio_file.read()
    
    st.audio(audio_bytes, format='audio/mp3', start_time=0)
    
    elapsed = time.time() - st.session_state.music_start_time
    time_left = max(0, 3 - elapsed)  # 5 menit = 300 detik
    
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
        2. Siapkan poin-poin utama yang ingin disampaikan<br> 
        3. Presentasikan secara jelas dan terstruktur<br>
        4. Anda akan presentasikan selama 3 menit
        </div>
        """, unsafe_allow_html=True)
        
        elapsed = time.time() - st.session_state.prep_start_time
        prep_time_left = max(0, 0 - elapsed)
        
        st.progress(min(elapsed/60, 1.0))
        st.markdown(f"### Waktu Persiapan Tersisa: {int(prep_time_left//60):02d}:{int(prep_time_left%60):02d}")
        
        st.session_state.feeling_response = st.text_area(
            "Tulis evaluasi perasaan Anda:",
            value=st.session_state.feeling_response,
            height=200,
            key="feeling_prep_input"
        )
        
        if prep_time_left <= 0:
            st.session_state.feeling_stage = "presentation"
            st.session_state.presentation_start_time = time.time()
            st.rerun()
    
    # Presentation Stage
    elif st.session_state.feeling_stage == "presentation":
        st.markdown("### Silakan sampaikan evaluasi Anda kepada evaluator")
        
        elapsed = time.time() - st.session_state.presentation_start_time
        presentation_time_left = max(0, 1 - elapsed)
        
        st.progress(min(elapsed/180, 1.0))
        st.markdown(f"### Waktu Presentasi Tersisa: {int(presentation_time_left//60):02d}:{int(presentation_time_left%60):02d}")
        
        # Display the notes in a more persistent way
        st.markdown("#### Catatan Evaluasi Anda:")
        st.markdown(f'<div class="custom-card" style="background-color:#f8f9fa; padding:15px; border-radius:10px; margin:10px 0; box-shadow:0 2px 4px rgba(0,0,0,0.1);">{st.session_state.feeling_response}</div>', 
                   unsafe_allow_html=True)
        
        if presentation_time_left <= 0 and not st.session_state.feeling_completed:
            # Save response before clearing
            if 'relaxation_responses' not in st.session_state:
                st.session_state.relaxation_responses = []
            
            st.session_state.relaxation_responses.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "response": st.session_state.feeling_response
            })
            
            # Clear only necessary states
            st.session_state.feeling_completed = True
            st.session_state.page = "rest_timer"
            st.rerun()
    
    # Auto refresh
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
        1. Mulailah dari angka 1022. <br>
        2. Lakukan pengurangan secara berurutan dengan mengurangi 13 di setiap langkah.<br>
        3. Anda memiliki waktu maksimal 5 menit untuk menyelesaikan tugas ini <br>
        4. Setiap hasil pengurangan harus disampaikan secara lisan kepada evaluator, satu per satu.<br>
        5. Evaluator akan mencatat dan memeriksa setiap jawaban yang Anda sebutkan.<br>
        6. Jika terjadi kesalahan dalam perhitungan atau penyebutan angka, Anda harus memulai kembali dari angka awal yaitu 1022.
        
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
    
    # Bersihkan halaman sepenuhnya
    st.empty()
    
    st.title("⏱️ Tugas Aritmatika - Tahap 3")
    st.markdown("---")
    
    elapsed = time.time() - st.session_state.arithmetic_start_time
    time_left = max(0, 3 - elapsed)  # 5 menit = 300 detik
    
    minutes, seconds = divmod(int(time_left), 60)
    st.markdown(f"### Waktu Tersisa: {minutes:02d}:{seconds:02d}")
    
    progress = min(elapsed / 3, 1.0)
    st.progress(progress)
    
    if time_left <= 0:
        # Arahkan ke halaman instruksi MIST terlebih dahulu
        st.session_state.page = "mist_instructions"
        st.rerun()
    
    time.sleep(0.1)
    st.rerun()

def mist_instructions_page():
    st.title("🧠 Instruksi MIST - Simulasi Aritmatika")
    st.markdown("---")
    
    st.markdown("""
    <div class='medium-font'>
    <b>Instruksi Simulasi MIST:</b><br>
    1. Anda akan diberikan soal-soal aritmatika dengan tingkat kesulitan yang meningkat.<br>
    2. Jawablah secepat dan seakurat mungkin dengan menggunakan keypad di bawah.<br>
    3. Perhatikan batas waktu untuk tiap soal (ditampilkan dengan progress bar).<br>
    4. Semakin banyak jawaban benar, semakin sulit soal berikutnya.<br>
    5. Simulasi akan berlangsung selama 3 menit.
    </div>
    """, unsafe_allow_html=True)
    
    # More detailed explanation of MIST
    st.markdown("""
    <div style='background-color:#f0f2f6; padding:15px; border-radius:10px; margin-top:20px; margin-bottom:20px;'>
    <h4>Tentang Simulasi MIST:</h4>
    <p>MIST (Mental Improvement through Speed Training) adalah simulasi tugas aritmatika dengan kondisi berikut:</p>
    <ul>
      <li>Anda akan diberikan soal aritmatika dengan tingkat kesulitan yang meningkat</li>
      <li>Ada batas waktu untuk menjawab setiap soal</li>
      <li>Semakin banyak soal yang Anda jawab dengan benar, semakin sulit soal selanjutnya</li>
      <li>Jika waktu habis sebelum Anda menjawab, soal dianggap salah</li>
      <li>Performa Anda akan dibandingkan dengan rata-rata peserta lain</li>
      <li>Durasi simulasi adalah 3 menit</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("▶️ Mulai Simulasi MIST", key="start_mist_simulation"):
            st.session_state.page = "mist_simulation"
            st.rerun()

def mist_simulation_page():
    
    # CSS untuk meningkatkan tampilan dan mencegah glitch dengan fixed heights
    st.markdown("""
    <style>
        .stButton>button {
            width: 100%;
            height: 40px;
            font-size: 20px;
        }
        .main-timer {
            position: fixed;
            top: 70px;
            left: 20px;
            background-color: rgba(255, 255, 255, 0.9);
            padding: 8px 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            z-index: 1000;
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }
        .question-timer {
            position: fixed;
            top: 70px;
            right: 20px;
            width: 200px;
            background-color: rgba(255, 255, 255, 0.9);
            padding: 8px 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            z-index: 1000;
            font-size: 16px;
            font-weight: bold;
        }
        .timer-progress {
            height: 10px;
            margin-top: 5px;
            border-radius: 5px;
            overflow: hidden;
        }
        .timer-progress-bar {
            height: 100%;
            background-color: #4CAF50;
            transition: width 0.3s ease;
        }
        .big-font {
            font-size: 30px;
            font-weight: bold;
            text-align: center;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 2px 0;
        }
        .answer-font {
            font-size: 24px;
            text-align: center;
            color: blue;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
        }
        .result-container {
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
        }
        .result-correct {
            color: green;
            font-size: 24px;
            text-align: center;
            font-weight: bold;
        }
        .result-incorrect {
            color: red;
            font-size: 24px;
            text-align: center;
            font-weight: bold;
        }
        .keypad-container {
            margin: 10px 0;
        }
        .metrics-container {
            margin-top: 5px;
            padding: 8px;
            border-radius: 5px;
        }
        .empty-space {
            height: 20px;
        }
        /* Pengaturan tambahan untuk mengurangi margin/padding dari elemen Streamlit */
        .stProgress {
            margin-top: 0 !important;
            margin-bottom: 5px !important;
            display: none;
        }
        /* Main content padding to avoid overlapping fixed timers */
        .main-content {
            margin-top: 110px;
            padding: 0 10px;
        }
        /* Hide default Streamlit elements */
        header {
            visibility: hidden;
        }
        footer {
            visibility: hidden;
        }
        /* Custom progress bars for metrics */
        .custom-progress {
            width: 100%;
            height: 10px;
            background-color: #f0f0f0;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .custom-progress-bar {
            height: 100%;
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True)
        
    # Inisialisasi variabel session state jika belum ada
    if 'mist_initialized' not in st.session_state:
        st.session_state.mist_initialized = True
        st.session_state.current_question = ""
        st.session_state.current_answer = ""
        st.session_state.correct_answer = ""
        st.session_state.response_status = None
        st.session_state.question_start_time = time.time()
        st.session_state.question_time_limit = 10  # Batas waktu awal (detik)
        st.session_state.total_elapsed_time = 0
        st.session_state.start_time = time.time()
        st.session_state.last_update_time = time.time()
        st.session_state.correct_answers = 0
        st.session_state.incorrect_answers = 0
        st.session_state.total_questions = 0
        st.session_state.consecutive_correct = 0
        st.session_state.consecutive_incorrect = 0
        st.session_state.difficulty_level = 1
        st.session_state.response_times = []
        st.session_state.average_response_time = 5  # Rata-rata awal (detik)
        st.session_state.show_response_until = 0
        st.session_state.fake_average_correct_rate = 0.75  # 75% tingkat kebenaran untuk "subjek lain"
        st.session_state.user_correct_rate = 0
        st.session_state.game_over = False
        st.session_state.should_clear_response = False
        
        # Durasi total dalam detik (3 menit)
        st.session_state.MIST_TOTAL_DURATION = 3
        st.session_state.last_sound_time = 0  # Melacak kapan terakhir kali kita memainkan suara
    
    # Buat placeholder containers dengan fixed heights
    title_container = st.container()
    main_content_container = st.container()
    main_timer_container = st.container()
    question_timer_container = st.container()
    question_display = st.container()
    answer_display = st.container()
    feedback_display = st.container()
    correct_answer_display = st.container()
    keypad_container = st.container()
    metrics_container = st.container()
    sound_container = st.empty()
    
    # Fungsi untuk membuat suara metronom
    def get_metronome_sound(fast=False):
        # Membuat suara yang lebih menarik perhatian
        sample_rate = 44100
        
        if fast:
            # Suara lebih cepat, pitch lebih tinggi untuk urgensi
            duration = 0.08  # Durasi lebih pendek
            frequency = 880  # Pitch lebih tinggi (nada A5)
            
            # Membuat tone awal
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = np.sin(2 * np.pi * frequency * t)
            
            # Menambahkan sedikit penurunan pitch di akhir untuk lebih urgen
            end_duration = 0.02
            end_t = np.linspace(0, end_duration, int(sample_rate * end_duration), False)
            end_tone = np.sin(2 * np.pi * (frequency*0.9) * end_t)
            
            # Menggabungkan tone dengan sedikit penurunan volume
            tone = np.concatenate([tone * 0.8, end_tone * 0.6])
        else:
            # Suara metronom biasa
            duration = 0.1  # 100ms
            frequency = 660  # Nada E5
            
            # Membuat tone dengan sedikit attack dan decay
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = np.sin(2 * np.pi * frequency * t)
            
            # Terapkan envelope untuk suara yang lebih baik (attack dan decay)
            envelope = np.ones_like(tone)
            attack_samples = int(0.01 * sample_rate)  # 10ms attack
            decay_samples = int(0.05 * sample_rate)   # 50ms decay
            
            # Attack (fade in)
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
            # Decay (fade out)
            envelope[-decay_samples:] = np.linspace(1, 0, decay_samples)
            
            tone = tone * envelope * 0.7  # Terapkan envelope dan sesuaikan volume
        
        # Konversi ke data 16-bit
        audio_data = (tone * 32767).astype(np.int16)
        
        # Buat file WAV di memori
        import wave
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
        
        # Dapatkan konten file WAV dan encode sebagai base64
        buffer.seek(0)
        audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        audio_html = f'<audio autoplay="true"><source src="data:audio/wav;base64,{audio_base64}" type="audio/wav"></audio>'
        return audio_html
    
    # Fungsi untuk menghasilkan pertanyaan baru
    def generate_question():
        # Bersihkan status respons sebelum menghasilkan pertanyaan baru
        st.session_state.response_status = None
        st.session_state.should_clear_response = True
        
        st.session_state.total_questions += 1
        
        if st.session_state.difficulty_level == 1:
            # Level 1: Penambahan/pengurangan sederhana
            num1 = random.randint(1, 99)
            num2 = random.randint(1, 99)
            operator = random.choice(['+', '-'])
            
            if operator == '+':
                result = num1 + num2
            else:  # operator == '-'
                # Pastikan hasilnya positif
                if num1 < num2:
                    num1, num2 = num2, num1
                result = num1 - num2
                
            st.session_state.current_question = f"{num1} {operator} {num2} = ?"
            st.session_state.correct_answer = str(result)
            
        elif st.session_state.difficulty_level == 2:
            # Level 2: Dua operasi
            num1 = random.randint(2, 20)
            num2 = random.randint(2, 10)
            num3 = random.randint(1, 20)
            operators = random.sample(['+', '-', '*'], 2)
            
            # Buat persamaan yang menghasilkan bilangan bulat positif
            equation = f"{num1} {operators[0]} {num2} {operators[1]} {num3}"
            result = eval(equation)  # Aman di sini karena kita mengontrol input
            
            st.session_state.current_question = f"{equation} = ?"
            st.session_state.correct_answer = str(result)
            
        else:  # difficulty_level == 3
            # Level 3: Tiga operasi
            num1 = random.randint(2, 15)
            num2 = random.randint(2, 10)
            num3 = random.randint(2, 8)
            num4 = random.randint(2, 5)
            operators = random.sample(['+', '-', '*'], 3)
            
            # Buat ekspresi yang aman
            expression = f"{num1} {operators[0]} {num2} {operators[1]} {num3} {operators[2]} {num4}"
            
            try:
                # Menggunakan eval dengan aman untuk aritmatika saja
                result = eval(expression)
                if result < 0 or not isinstance(result, int):
                    # Jika bukan bilangan bulat positif, coba lagi
                    return generate_question()
                    
                st.session_state.current_question = f"{expression} = ?"
                st.session_state.correct_answer = str(result)
            except:
                # Jika terjadi kesalahan, coba lagi
                return generate_question()
        
        # Reset input jawaban dan timer
        st.session_state.current_answer = ""
        st.session_state.question_start_time = time.time()
        st.session_state.last_sound_time = 0  # Reset waktu suara
    
    # Fungsi untuk menyesuaikan kesulitan
    def adjust_difficulty():
        if st.session_state.total_questions > 5:
            correct_rate = st.session_state.correct_answers / st.session_state.total_questions
            if correct_rate > 0.8 and st.session_state.difficulty_level < 3:
                st.session_state.difficulty_level += 1
            elif correct_rate < 0.3 and st.session_state.difficulty_level > 1:
                st.session_state.difficulty_level -= 1
    
    # Fungsi untuk menyesuaikan batas waktu
    def adjust_time_limit():
        if st.session_state.consecutive_correct >= 3:
            # Kurangi waktu sebesar 10%
            st.session_state.question_time_limit = max(2, st.session_state.question_time_limit * 0.9)
            st.session_state.consecutive_correct = 0
        elif st.session_state.consecutive_incorrect >= 3:
            # Tingkatkan waktu sebesar 10%
            st.session_state.question_time_limit *= 1.1
            st.session_state.consecutive_incorrect = 0
    
    # Fungsi untuk memperbarui metrik kinerja
    def update_performance_metrics(response_time, correct):
        st.session_state.response_times.append(response_time)
        st.session_state.average_response_time = sum(st.session_state.response_times) / len(st.session_state.response_times)
        
        if correct:
            st.session_state.correct_answers += 1
            st.session_state.consecutive_correct += 1
            st.session_state.consecutive_incorrect = 0
        else:
            st.session_state.incorrect_answers += 1
            st.session_state.consecutive_incorrect += 1
            st.session_state.consecutive_correct = 0
        
        st.session_state.user_correct_rate = st.session_state.correct_answers / max(1, st.session_state.total_questions)
        adjust_time_limit()
        adjust_difficulty()
    
    # Fungsi untuk mengirimkan jawaban
    def submit_answer():
        response_time = time.time() - st.session_state.question_start_time
        
        if st.session_state.current_answer == st.session_state.correct_answer:
            st.session_state.response_status = "Benar"
            update_performance_metrics(response_time, True)
        else:
            st.session_state.response_status = "Salah"
            update_performance_metrics(response_time, False)
        
        # Tampilkan respons selama 1.5 detik
        st.session_state.show_response_until = time.time() + 1.5
        st.session_state.should_clear_response = False
        
        # Simpan hasil untuk riwayat aritmatika
        if 'mist_history' not in st.session_state:
            st.session_state.mist_history = []
            
        st.session_state.mist_history.append({
            'question': st.session_state.current_question,
            'user_answer': st.session_state.current_answer,
            'correct_answer': st.session_state.correct_answer,
            'correct': st.session_state.current_answer == st.session_state.correct_answer,
            'response_time': response_time,
            'difficulty_level': st.session_state.difficulty_level
        })
    
    # Hasilkan pertanyaan pertama jika diperlukan
    if not st.session_state.current_question:
        generate_question()
    
    # Perbarui waktu yang telah berlalu
    current_time = time.time()
    time_delta = current_time - st.session_state.last_update_time
    st.session_state.total_elapsed_time += time_delta
    st.session_state.last_update_time = current_time
    
    # Calculate remaining time
    time_left = max(0, st.session_state.MIST_TOTAL_DURATION - st.session_state.total_elapsed_time)
    
    # Periksa game over
    if time_left <= 0 and not st.session_state.game_over:
        st.session_state.game_over = True
        # Simpan hasil MIST ke session state
        if 'mist_results' not in st.session_state:
            st.session_state.mist_results = {
                'correct_answers': st.session_state.correct_answers,
                'incorrect_answers': st.session_state.incorrect_answers,
                'total_questions': st.session_state.total_questions,
                'average_response_time': st.session_state.average_response_time,
                'final_difficulty_level': st.session_state.difficulty_level,
                'history': st.session_state.mist_history if 'mist_history' in st.session_state else []
            }
        # Lanjut ke halaman berikutnya setelah selesai
        st.session_state.page = "rest_timer"
        st.rerun()
    
    # Hitung timer pertanyaan saat ini
    question_elapsed = current_time - st.session_state.question_start_time
    remaining_time = max(0, st.session_state.question_time_limit - question_elapsed)
    
    # Periksa waktu habis untuk pertanyaan saat ini
    if remaining_time <= 0 and st.session_state.response_status is None:
        st.session_state.response_status = "Waktu Habis"
        update_performance_metrics(st.session_state.question_time_limit, False)
        st.session_state.show_response_until = current_time + 1.5
        st.session_state.should_clear_response = False
        
        # Simpan hasil untuk pertanyaan yang waktu habis
        if 'mist_history' not in st.session_state:
            st.session_state.mist_history = []
            
        st.session_state.mist_history.append({
            'question': st.session_state.current_question,
            'user_answer': "Tidak menjawab",
            'correct_answer': st.session_state.correct_answer,
            'correct': False,
            'response_time': st.session_state.question_time_limit,
            'difficulty_level': st.session_state.difficulty_level
        })
    
    # HTML untuk timer utama (kiri atas - fixed position)
    with main_timer_container:
        st.markdown(
            f"""
            <div class="main-timer">⏱️ Total: {int(time_left)}s</div>
            """, 
            unsafe_allow_html=True
        )
    
    # HTML untuk timer pertanyaan (kanan atas - fixed position)
    with question_timer_container:
        timer_progress = max(0, min(1.0, remaining_time / st.session_state.question_time_limit))
        timer_color = "green" if timer_progress > 0.5 else "yellow" if timer_progress > 0.25 else "red"
        st.markdown(
            f"""
            <div class="question-timer">
                ⏲️ Soal: {remaining_time:.1f}s
                <div class="timer-progress">
                    <div class="timer-progress-bar" style="width: {timer_progress * 100}%; background-color: {timer_color};"></div>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Logika suara metronom
    if st.session_state.response_status is None and not st.session_state.game_over:
        play_sound = False
        sound_interval = 1.0  # Interval default (1 detik)
        
        # Sesuaikan frekuensi suara berdasarkan waktu yang tersisa
        if remaining_time < 3:
            # Tempo cepat ketika waktu hampir habis (4 kali per detik)
            sound_interval = 0.25
            if current_time - st.session_state.last_sound_time >= sound_interval:
                play_sound = True
                # Gunakan suara urgen ketika waktu < 3 detik
                sound_container.markdown(get_metronome_sound(fast=True), unsafe_allow_html=True)
                st.session_state.last_sound_time = current_time
        elif remaining_time < 5:
            # Tempo sedang (2 kali per detik)
            sound_interval = 0.5
            if current_time - st.session_state.last_sound_time >= sound_interval:
                play_sound = True
                # Gunakan suara lebih urgen ketika waktu < 5 detik
                sound_container.markdown(get_metronome_sound(fast=True), unsafe_allow_html=True)
                st.session_state.last_sound_time = current_time
        else:
            # Tempo normal (1 kali per detik)
            sound_interval = 1.0
            if current_time - st.session_state.last_sound_time >= sound_interval:
                play_sound = True
                # Gunakan suara metronom normal
                sound_container.markdown(get_metronome_sound(fast=False), unsafe_allow_html=True)
                st.session_state.last_sound_time = current_time
    
    # Bagian konten game dalam container tetap
    with main_content_container:
        if not st.session_state.game_over:
            # Tampilkan pertanyaan
            with question_display:
                st.markdown(f'<div class="big-font">{st.session_state.current_question}</div>', unsafe_allow_html=True)
            
            # Tampilkan jawaban saat ini
            with answer_display:
                st.markdown(f'<div class="answer-font">Jawaban: {st.session_state.current_answer}</div>', unsafe_allow_html=True)
            
            # Tangani pesan respons (benar/salah)
            with feedback_display:
                if st.session_state.response_status:
                    if current_time < st.session_state.show_response_until:
                        result_class = "result-correct" if st.session_state.response_status == "Benar" else "result-incorrect"
                        st.markdown(f'<div class="result-container"><div class="{result_class}">{st.session_state.response_status}</div></div>', unsafe_allow_html=True)
                    else:
                        # Bersihkan tampilan tetapi pertahankan tinggi
                        st.markdown('<div class="result-container"></div>', unsafe_allow_html=True)
                        
                        # Tampilkan pertanyaan baru
                        generate_question()
                        st.rerun()
                else:
                    # Bersihkan umpan balik tetapi pertahankan tinggi
                    st.markdown('<div class="result-container"></div>', unsafe_allow_html=True)
            
            # Placeholder kosong untuk menjaga konsistensi tata letak
            with correct_answer_display:
                st.markdown('<div class="empty-space"></div>', unsafe_allow_html=True)
            
            # Input angka
            with keypad_container:
                if st.session_state.response_status is None:
                    # Buat keypad dengan semua tombol dalam satu baris
                    cols_digits = st.columns(12)  # 10 digits + backspace + submit
                    
                    # Tombol 0-9 dalam satu baris
                    for i in range(10):
                        with cols_digits[i]:
                            if st.button(f"{i}", key=f"num_{i}"):
                                st.session_state.current_answer += str(i)
                    
                    # Tombol backspace
                    with cols_digits[10]:
                        if st.button("⌫", key="backspace"):
                            if st.session_state.current_answer:
                                st.session_state.current_answer = st.session_state.current_answer[:-1]
                    
                    # Tombol submit
                    with cols_digits[11]:
                        if st.button("✓", key="submit", type="primary"):
                            if st.session_state.current_answer:
                                submit_answer()
            
            # Metrik kinerja dalam format yang bersih
            with metrics_container:
                col1, col2 = st.columns(2)
                
                with col1:
                    your_score = int(st.session_state.user_correct_rate * 100)
                    st.markdown(f"<div><b>Performa Anda:</b> {your_score}%</div>", unsafe_allow_html=True)
                    st.markdown(f"""
                        <div class="custom-progress">
                            <div class="custom-progress-bar" style="width: {your_score}%; background-color: #4CAF50;"></div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    avg_score = int(st.session_state.fake_average_correct_rate * 100)
                    st.markdown(f"<div><b>Performa Rata-rata:</b> {avg_score}%</div>", unsafe_allow_html=True)
                    st.markdown(f"""
                        <div class="custom-progress">
                            <div class="custom-progress-bar" style="width: {avg_score}%; background-color: #2196F3;"></div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"<div><b>Skor:</b> {st.session_state.correct_answers}/{st.session_state.total_questions}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div><b>Level:</b> {st.session_state.difficulty_level}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div><b>Waktu Respons Rata-rata:</b> {st.session_state.average_response_time:.1f}s</div>", unsafe_allow_html=True)
        else:
            # Tampilan game over - tetap menggunakan container untuk konsistensi
            with question_display:
                st.markdown('<div class="big-font">Tes Selesai</div>', unsafe_allow_html=True)
            
            with answer_display:
                st.markdown(f'<div class="answer-font">Skor Akhir Anda: {st.session_state.correct_answers}/{st.session_state.total_questions}</div>', unsafe_allow_html=True)
            
            with feedback_display:
                st.markdown('<div class="result-container"><div class="result-correct">Selamat! Anda telah menyelesaikan simulasi MIST.</div></div>', unsafe_allow_html=True)
            
            with correct_answer_display:
                st.markdown('<div class="empty-space"></div>', unsafe_allow_html=True)
            
            with keypad_container:
                col_btn = st.columns([1, 2, 1])
                with col_btn[1]:
                    if st.button("➡️ Lanjutkan ke Tahap Berikutnya", key="next_to_rest"):
                        # Lanjut ke halaman berikutnya
                        st.session_state.page = "rest_timer"
                        st.rerun()
    
    # Auto-refresh untuk pembaruan timer tetapi dengan delay lebih lama
    if not st.session_state.game_over:
        time.sleep(0.3)  # Delay lebih lama untuk mengurangi glitch
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
        if 'font_size' not in st.session_state:
            st.session_state.font_size = 16
            
        font_size = st.slider(
            "Ukuran Font", 
            12, 24, 
            st.session_state.font_size,
            key="font_size_slider"
        )
        if font_size != st.session_state.font_size:
            st.session_state.font_size = font_size
    
    with col2:
        if 'auto_scroll' not in st.session_state:
            st.session_state.auto_scroll = False
            
        auto_scroll = st.checkbox(
            "Auto-Scroll", 
            st.session_state.auto_scroll,
            key="auto_scroll_checkbox"
        )
        if auto_scroll != st.session_state.auto_scroll:
            st.session_state.auto_scroll = auto_scroll
            
        if st.session_state.auto_scroll:
            if 'scroll_speed' not in st.session_state:
                st.session_state.scroll_speed = 1.0
                
            scroll_speed = st.slider(
                "Kecepatan Scroll", 
                0.5, 5.0, 
                st.session_state.scroll_speed,
                step=0.5, 
                key="scroll_speed_slider"
            )
            if scroll_speed != st.session_state.scroll_speed:
                st.session_state.scroll_speed = scroll_speed
    
    st.markdown("### Mulai Pembacaan Cerita")
    if 'stories_loaded' not in st.session_state:
        st.session_state.stories = extract_stories_from_docx("Kumpulan Cerita.docx")
        st.session_state.stories_loaded = True
    
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("🔀 Mulai Membaca", key="start_reading"):
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
    
    # Initialize timer state
    if 'presentation_start_time' not in st.session_state:
        st.session_state.presentation_start_time = time.time()
        st.session_state.presentation_time_up = False
    
    # Calculate remaining time
    elapsed = time.time() - st.session_state.presentation_start_time
    time_left = max(0, 300 - elapsed)  # 5 menit = 300 detik
    
    st.markdown("### Topik Presentasi Anda:")
    st.markdown(f"<div style='padding:10px; background-color:#cce5ff; border-radius:5px; font-size:24px; font-weight:bold;'>{st.session_state.selected_topic}</div>", unsafe_allow_html=True)
    
    # Display remaining time
    minutes = int(time_left // 60)
    seconds = int(time_left % 60)
    st.markdown(f"### Waktu Presentasi Tersisa: {minutes:02d}:{seconds:02d}")
    
    # Progress bar
    st.progress(min(elapsed/300, 1.0))
    
    st.markdown("### Catatan Persiapan Anda:")
    st.write(st.session_state.presentation_notes)
    
    # Check if time is up
    if time_left <= 0 and not st.session_state.presentation_time_up:
        st.session_state.presentation_time_up = True
        # Clear timer state
        keys_to_clear = ['presentation_start_time', 'presentation_time_up']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        st.session_state.page = "arithmetic_task"  # Langsung ke aritmatika tahap 2
        st.rerun()
    
    time.sleep(0.1)
    st.rerun()

def arithmetic_task_page():
    # Clear all presentation-related states
    for key in ['presentation_notes', 'selected_topic', 'high_presentation_notes', 'high_presentation_topic']:
        if key in st.session_state:
            del st.session_state[key]

    st.title("🧮 Tugas Aritmatika - Tahap 2")
    st.markdown("---")
    
    st.markdown("""
    <div class='medium-font'>
    <b>Instruksi:</b><br>
    1. Selesaikan soal pengurangan/pembagian berikut<br>
    2. Jawab dengan benar untuk melanjutkan ke soal berikutnya<br>
    3. Anda memiliki waktu 5 menit untuk mengerjakan soal-soal<br>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize timer
    if 'arithmetic_start_time' not in st.session_state:
        st.session_state.arithmetic_start_time = time.time()
        st.session_state.arithmetic_time_up = False
    
    # Calculate remaining time
    elapsed = time.time() - st.session_state.arithmetic_start_time
    time_left = max(0, 300 - elapsed)  # 5 minutes = 300 seconds
    
    # Display remaining time
    minutes = int(time_left // 60)
    seconds = int(time_left % 60)
    st.markdown(f"### Waktu Tersisa: {minutes:02d}:{seconds:02d}")
    
    # Progress bar
    st.progress(min(elapsed/300, 1.0))
    
    # Initialize arithmetic problems
    if 'arithmetic_problems' not in st.session_state:
        st.session_state.arithmetic_problems = []
        st.session_state.current_problem = 0
        st.session_state.answers = []
        
        # Generate first problem
        if random.random() > 0.5:
            a = random.randint(500, 999)
            b = random.randint(100, 499)
            st.session_state.arithmetic_problems.append({
                'type': 'pengurangan',
                'question': f"{a} - {b} = ?",
                'answer': a - b
            })
        else:
            b = random.randint(10, 99)
            answer = random.randint(10, 99)
            a = b * answer
            while a < 100 or a > 999:
                b = random.randint(10, 99)
                answer = random.randint(10, 99)
                a = b * answer
            st.session_state.arithmetic_problems.append({
                'type': 'pembagian',
                'question': f"{a} ÷ {b} = ?",
                'answer': answer
            })

    # Display current problem
    problem = st.session_state.arithmetic_problems[st.session_state.current_problem]
    st.markdown(f"### Soal:")
    st.markdown(f"<div class='big-font'>{problem['question']}</div>", unsafe_allow_html=True)
    
    # Create form for answer input
    with st.form(key='answer_form'):
        answer_key = f"answer_{st.session_state.current_problem}"
        user_answer = st.number_input(
            "Jawaban Anda:", 
            key=answer_key,
            step=1,
            value=None,
            label_visibility="collapsed"
        )
        submitted = st.form_submit_button("Masukan Jawaban")
    
    # Handle submitted answers
    if submitted or user_answer is not None:
        if user_answer is not None:
            is_correct = (user_answer == problem['answer'])
            
            st.session_state.answers.append({
                'problem': problem['question'],
                'user_answer': user_answer,
                'is_correct': is_correct,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
            
            if is_correct:
                # Generate new problem after correct answer
                if random.random() > 0.5:
                    a = random.randint(500, 999)
                    b = random.randint(100, 499)
                    st.session_state.arithmetic_problems.append({
                        'type': 'pengurangan',
                        'question': f"{a} - {b} = ?",
                        'answer': a - b
                    })
                else:
                    b = random.randint(10, 99)
                    answer = random.randint(10, 99)
                    a = b * answer
                    while a < 100 or a > 999:
                        b = random.randint(10, 99)
                        answer = random.randint(10, 99)
                        a = b * answer
                    st.session_state.arithmetic_problems.append({
                        'type': 'pembagian',
                        'question': f"{a} ÷ {b} = ?",
                        'answer': answer
                    })
                
                st.session_state.current_problem += 1
                st.rerun()
    
    # Check if time is up
    if time_left <= 0 and not st.session_state.arithmetic_time_up:
        st.session_state.arithmetic_time_up = True
        st.session_state.page = "rest_timer"
        st.rerun()
    
    # Auto refresh for timer update
    time.sleep(0.1)
    st.rerun()

def cerita_page():
    if st.button("⬅️ Kembali ke Pengaturan", key="back_button"):
        st.session_state.page = "cerita_setup"
        st.rerun()
    
    if 'reading_start_time' not in st.session_state:
        st.session_state.reading_start_time = time.time()
        st.session_state.reading_time_up = False
    
    elapsed = time.time() - st.session_state.reading_start_time
    time_left = max(0, 60 - elapsed)
    
    selected_story = st.session_state.selected_story
    
    minutes, seconds = divmod(int(time_left), 60)
    
    # CSS untuk timer yang tetap posisinya (fixed) saat scroll
    st.markdown("""
    <style>
    .fixed-timer {
        position: fixed;
        top: 70px;
        left: 20px;
        background-color: white;
        padding: 10px 15px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        z-index: 1000;
        font-size: 16px;
        font-weight: bold;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # HTML untuk menampilkan timer yang fixed dalam format serupa dengan kode asli
    st.markdown(
        f"""
        <div class="fixed-timer">Waktu Membaca: {minutes:02d}:{seconds:02d}</div>
        """, 
        unsafe_allow_html=True
    )
    
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
        st.session_state.page = "rest_timer"  # Langsung pindah ke halaman istirahat
        st.rerun()
    
    # Hapus bagian tombol "Lanjut ke Istirahat" karena sekarang otomatis
    if st.session_state.reading_time_up:
        time.sleep(0.1)  # Memberi waktu kecil untuk memastikan transisi
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
                # Hanya di Tahap 1 kita lanjut ke acute stress
                if st.session_state.current_condition == "Tahap 1":
                    st.session_state.page = "acute_stress"
                else:
                    # Untuk kondisi lain, langsung simpan dan lanjut ke tahap berikutnya
                    save_session_results(st.session_state.current_condition)
                    
                    conditions = ["Tahap 1", "Tahap 2", "Tahap 3", "Tahap 4"]
                    current_index = conditions.index(st.session_state.current_condition)
                    
                    if current_index < len(conditions) - 1:
                        next_condition = conditions[current_index + 1]
                        st.session_state.page = next_condition.lower().replace(" ", "")
                    else:
                        st.session_state.page = "hasil"
                    
                    del st.session_state.dass21_responses
                
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

    # ✅ Inisialisasi aman
    if 'dass21_responses' not in st.session_state:
        st.session_state.dass21_responses = {}

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

                # Scroll ke atas
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
                        st.write(f"- Terakhir Minum Kopi: {result['Terakhir Minum Kopi (jam)']}")
                        st.write(f"- Durasi Tidur: {result['Durasi Tidur (jam)']} jam")
                    with col2:
                        st.markdown("**Hasil Tes:**")
                        
                        # Only display DASS-21 results for Tahap 1
                        if condition == "Tahap 1":
                            st.write(f"- Depresi: {result['Skor DASS21 - Depresi']} ({result['Kategori DASS21 - Depresi']})")
                            st.write(f"- Kecemasan: {result['Skor DASS21 - Kecemasan']} ({result['Kategori DASS21 - Kecemasan']})")
                            st.write(f"- Stres: {result['Skor DASS21 - Stres']} ({result['Kategori DASS21 - Stres']})")
                        
                        # Always display Acute Stress results
                        st.write(f"- Stres Akut: {result['Skor Respons Stres Akut']} ({result['Kategori Respons Stres Akut']})")
                        
                        # Display condition-specific results
                        if condition == "Tahap 2" and "Topik Presentasi" in result:
                            st.write(f"- Topik Presentasi: {result['Topik Presentasi']}")
                            if "Total_Soal_Aritmatika" in result:
                                st.write(f"- Soal Aritmatika Benar: {result['Total_Jawaban_Benar']}/{result['Total_Soal_Aritmatika']}")
                        
                        if condition == "Tahap 3" and "Topik Presentasi" in result:
                            st.write(f"- Topik Presentasi: {result['Topik Presentasi']}")
                            if "Jumlah Percobaan Aritmatika" in result:
                                st.write(f"- Percobaan Aritmatika: {result['Jumlah Percobaan Aritmatika']}")
                            
                            # Tambahkan hasil MIST untuk Tahap 3
                            if "MIST_Total_Soal" in result:
                                st.markdown("**Hasil MIST:**")
                                st.write(f"- Total Soal: {result['MIST_Total_Soal']}")
                                st.write(f"- Jawaban Benar: {result['MIST_Jawaban_Benar']}")
                                st.write(f"- Jawaban Salah: {result['MIST_Jawaban_Salah']}")
                                st.write(f"- Tingkat Akurasi: {round((result['MIST_Jawaban_Benar'] / result['MIST_Total_Soal']) * 100, 2)}%")
                                st.write(f"- Rata-rata Waktu Respons: {result['MIST_Rata_Waktu_Respons']} detik")
                                st.write(f"- Level Kesulitan Akhir: {result['MIST_Level_Akhir']}")
                        
                        if condition == "Tahap 4" and "Jenis_Relaksasi" in result:
                            st.write(f"- Jenis Relaksasi: {result['Jenis_Relaksasi']}")
                            st.write(f"- Durasi Relaksasi: {result['Durasi_Relaksasi']}")
                    
                    # Tampilkan detail MIST jika tersedia dan ini adalah Tahap 3
                    if condition == "Tahap 3" and "MIST_Total_Soal" in result:
                        st.markdown("---")
                        st.markdown("**Detail Simulasi MIST:**")
                        
                        # Buat tabel untuk detail soal MIST
                        mist_data = []
                        i = 0
                        while f"MIST_Soal_{i+1}" in result:
                            mist_data.append({
                                "Soal": result[f"MIST_Soal_{i+1}"],
                                "Jawaban Pengguna": result[f"MIST_Jawaban_{i+1}"],
                                "Status": "✅ Benar" if result[f"MIST_Benar_{i+1}"] else "❌ Salah",
                                "Waktu Respons (detik)": result[f"MIST_Waktu_Respons_{i+1}"],
                                "Level Kesulitan": result[f"MIST_Level_{i+1}"]
                            })
                            i += 1
                        
                        if mist_data:
                            mist_df = pd.DataFrame(mist_data)
                            st.dataframe(mist_df)
        
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
        "high_arithmetic": high_arithmetic_page,
        "mist_instructions": mist_instructions_page,
        "mist_simulation": mist_simulation_page,  # Tambahkan halaman MIST
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
