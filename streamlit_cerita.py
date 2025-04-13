import streamlit as st
import pandas as pd
import random
import re
import io
import os
from datetime import datetime

# Set page config (HARUS menjadi perintah Streamlit pertama)
st.set_page_config(
    page_title="Aplikasi Pengkondisian Stres",
    page_icon="📚",
    layout="wide"
)

# Tambahkan penanganan error untuk docx
try:
    import docx
except ImportError:
    st.error("Modul python-docx tidak terinstall. Silakan install dengan 'pip install python-docx'")

# Definisi cerita secara manual sebagai fallback
predefined_stories = [
    {
        "judul": "Hari yang Biasa",
        "isi": "Pagi hari, matahari belum terlalu tinggi. Cahaya dari balik tirai jatuh ke lantai dalam garis-garis samar. Udara di dalam kamar cukup sejuk. Tidak terlalu dingin, tidak juga hangat. Tidak ada suara bising dari luar, hanya suara samar kipas angin yang berputar perlahan di langit-langit..."
    },
    {
        "judul": "Hari di Toko Alat Tulis",
        "isi": "Pintu toko terbuka dengan suara lonceng kecil. Hana, perempuan berambut sebahu dengan kemeja abu-abu, sudah berada di balik meja kasir sejak pukul sembilan. Ia menekan tombol pada mesin kasir untuk mengecek saldo awal. Jumlahnya sesuai catatan. Tidak kurang, tidak lebih..."
    },
    # Tambahkan cerita lainnya di sini...
]

def extract_stories_from_docx(file_path):
    """
    Fungsi untuk mengekstrak cerita dari file docx dengan path tertentu
    """
    try:
        # Cek apakah file ada
        if not os.path.exists(file_path):
            return predefined_stories
            
        doc = docx.Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        
        # Cara 1: Mencari judul dengan pola ## diikuti judul
        titles_pattern1 = re.findall(r'## (.*?)(?=\n|$)', '\n'.join(paragraphs))
        
        # Cara 2: Mencari berdasarkan paragraf yang mengandung judul cerita
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
                
        # Pilih pola yang menemukan judul
        if titles_pattern1:
            titles = titles_pattern1
            
            # Membagi konten berdasarkan judul
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
            
            # Membagi konten berdasarkan posisi judul
            stories = []
            for i in range(len(story_start_indices)):
                judul = titles[i]
                start_idx = story_start_indices[i] + 1  # Mulai dari paragraf setelah judul
                
                # Tentukan akhir cerita
                if i < len(story_start_indices) - 1:
                    end_idx = story_start_indices[i + 1]
                else:
                    end_idx = len(paragraphs)
                
                # Gabungkan paragraf menjadi isi cerita
                isi = "\n\n".join(paragraphs[start_idx:end_idx])
                stories.append({"judul": judul, "isi": isi})
        else:
            return predefined_stories
        
        if not stories:
            return predefined_stories
            
        return stories
    except Exception as e:
        return predefined_stories

# Halaman pengantar/informasi
def info_page():
    st.title("Aplikasi Pengkondisian Stres")
    
    # Tampilkan informasi tentang kuesioner dan TSST
    st.markdown("""
    <style>
    .info-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    .info-header {
        color: #1E3A8A;
        font-size: 1.5rem;
        margin-bottom: 16px;
    }
    .info-content {
        font-size: 1.1rem;
        line-height: 1.6;
    }
    .tsst-card {
        background-color: #E7F3FE;
        border-left: 6px solid #2196F3;
        padding: 24px;
        margin-top: 32px;
        border-radius: 4px;
    }
    </style>
    
    <div class="info-card">
        <h2 class="info-header">Informasi</h2>
        <div class="info-content">
            <p>Kuesioner ini terdiri dari:</p>
            <ul>
                <li>Data Diri</li>
                <li>Pengkondisian berdasarkan TSST</li>
                <li>Depression, Anxiety, Stress Scale (DASS-21)</li>
                <li>Kuesioner Respons Stres Akut</li>
            </ul>
            <p>Hasil akan dapat diunduh dalam format CSV.</p>
            
            <div class="tsst-card">
                <h3>Tentang TSST (Trier Social Stress Test)</h3>
                <p><strong>Trier Social Stress Test (TSST)</strong> adalah protokol standar untuk menginduksi stres dalam kondisi laboratorium.</p>
                <p>Dikembangkan oleh Kirschbaum et al. (1993), TSST melibatkan kombinasi tekanan psikososial melalui:</p>
                <ul>
                    <li>Presentasi di depan evaluator</li>
                    <li>Tugas aritmatika dengan tekanan waktu</li>
                    <li>Evaluasi sosial</li>
                </ul>
                <p>TSST telah terbukti mampu menginduksi respons stres yang terukur dan konsisten dalam berbagai penelitian.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tombol untuk memulai
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("Mulai", use_container_width=True):
            st.session_state.page = "data_diri"
            st.experimental_rerun()

# Halaman data diri
def data_diri_page():
    st.title("Data Diri")
    
    # Dengan sidebar untuk menampilkan informasi
    with st.sidebar:
        st.header("Informasi")
        st.info("""
        Kuesioner ini terdiri dari:
        - Data Diri
        - Pengkondisian berdasarkan TSST
        - Depression, Anxiety, Stress Scale (DASS-21)
        - Kuesioner Respons Stres Akut 
        
        Hasil akan dapat diunduh dalam format CSV.
        """)
        
        with st.expander("Tentang TSST (Trier Social Stress Test)"):
            st.markdown("""
            **Trier Social Stress Test (TSST)** adalah protokol standar untuk menginduksi stres dalam kondisi laboratorium. 
            
            Dikembangkan oleh Kirschbaum et al. (1993), TSST melibatkan kombinasi tekanan psikososial melalui:
            - Presentasi di depan evaluator
            - Tugas aritmatika dengan tekanan waktu
            - Evaluasi sosial
            
            TSST telah terbukti mampu menginduksi respons stres yang terukur dan konsisten dalam berbagai penelitian.
            """)
    
    # Menggunakan columns untuk layout form
    col1, col2 = st.columns(2)
    
    with col1:
        nama = st.text_input("Nama Lengkap", key="nama")
        umur = st.number_input("Umur", min_value=0, max_value=120, step=1, key="umur")
        gender = st.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"], key="gender")
    
    with col2:
        bb = st.number_input("Berat Badan (kg)", min_value=0.0, max_value=300.0, step=0.1, key="bb")
        tb = st.number_input("Tinggi Badan (cm)", min_value=0.0, max_value=300.0, step=0.1, key="tb")
    
    # Tombol submit di tengah
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("Simpan dan Lanjutkan", use_container_width=True):
            # Validasi data
            if not nama or umur <= 0 or bb <= 0 or tb <= 0:
                st.error("Mohon isi semua data dengan benar!")
            else:
                st.session_state.data_diri = {
                    "Nama": nama,
                    "Umur": umur,
                    "Jenis Kelamin": gender,
                    "Berat Badan (kg)": bb,
                    "Tinggi Badan (cm)": tb,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.data_diri_submitted = True
                # Pindah ke halaman pengkondisian
                st.session_state.page = "pengkondisian"
                st.experimental_rerun()

# Halaman pengkondisian TSST
def pengkondisian_page():
    st.title("Pengkondisian Stres (TSST)")
    
    # Dengan sidebar untuk menampilkan informasi
    with st.sidebar:
        st.header("Informasi")
        st.info("""
        Kuesioner ini terdiri dari:
        - Data Diri
        - Pengkondisian berdasarkan TSST
        - Depression, Anxiety, Stress Scale (DASS-21)
        - Kuesioner Respons Stres Akut 
        
        Hasil akan dapat diunduh dalam format CSV.
        """)
        
        with st.expander("Tentang TSST (Trier Social Stress Test)"):
            st.markdown("""
            **Trier Social Stress Test (TSST)** adalah protokol standar untuk menginduksi stres dalam kondisi laboratorium. 
            
            Dikembangkan oleh Kirschbaum et al. (1993), TSST melibatkan kombinasi tekanan psikososial melalui:
            - Presentasi di depan evaluator
            - Tugas aritmatika dengan tekanan waktu
            - Evaluasi sosial
            
            TSST telah terbukti mampu menginduksi respons stres yang terukur dan konsisten dalam berbagai penelitian.
            """)
    
    # Tampilkan data diri dalam bentuk card
    st.markdown("""
    <style>
    .data-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    .info-box {
        background-color: #e7f3fe;
        border-left: 6px solid #2196F3;
        padding: 20px;
        margin: 20px 0;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="data-card">
        <h3>Data Diri</h3>
        <p><strong>Nama:</strong> {st.session_state.data_diri['Nama']}</p>
        <p><strong>Umur:</strong> {st.session_state.data_diri['Umur']}</p>
        <p><strong>Jenis Kelamin:</strong> {st.session_state.data_diri['Jenis Kelamin']}</p>
        <p><strong>Berat Badan:</strong> {st.session_state.data_diri['Berat Badan (kg)']} kg</p>
        <p><strong>Tinggi Badan:</strong> {st.session_state.data_diri['Tinggi Badan (cm)']} cm</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("Pilih jenis pengkondisian yang diberikan:")
    
    # Radio button untuk pemilihan pengkondisian
    pengkondisian = st.radio(
        "Jenis Pengkondisian",
        ["Baseline (Low)", "Medium", "High", "Relaksasi"],
        index=0,  # Default ke Baseline
        key="pengkondisian_option"
    )
    
    # Tampilkan informasi sesuai pengkondisian yang dipilih
    if pengkondisian == "Baseline (Low)":
        st.markdown("""
        <div class="info-box">
            <h3>Pengkondisian Baseline (TSST-Kontrol):</h3>
            <ul>
                <li>Subjek diminta membaca materi netral selama 5-10 menit</li>
                <li>Tidak ada tekanan waktu atau evaluasi sosial</li>
                <li>Tujuan: Memberikan aktivitas tanpa komponen stres</li>
            </ul>
            <p><em>Referensi: Het, S., et al. (2009). Neuroendocrine and psychometric evaluation of a placebo version of the 'Trier Social Stress Test'. Psychoneuroendocrinology, 34(7), 1075-1086.</em></p>
        </div>
        """, unsafe_allow_html=True)
    elif pengkondisian == "Medium":
        st.markdown("""
        <div class="info-box">
            <h3>Pengkondisian Medium (TSST-Modifikasi):</h3>
            <ul>
                <li>Subjek diminta mempersiapkan presentasi (5 menit) tentang topik netral</li>
                <li>Presentasi dilakukan di depan 1 orang evaluator</li>
                <li>Tugas aritmatika sederhana (pengurangan/pembagian) dengan sedikit umpan balik</li>
            </ul>
            <p><em>Referensi: Childs, E., Dlugos, A., & de Wit, H. (2010). Cardiovascular, hormonal, and emotional responses to the TSST in relation to sex and menstrual cycle phase. Psychophysiology, 47(3), 550-559.</em></p>
        </div>
        """, unsafe_allow_html=True)
    elif pengkondisian == "High":
        st.markdown("""
        <div class="info-box">
            <h3>Pengkondisian High (TSST Penuh):</h3>
            <ul>
                <li>Subjek diberi waktu persiapan 5 menit untuk presentasi tentang "kelemahan mereka" atau "mengapa mereka cocok untuk pekerjaan"</li>
                <li>Presentasi dilakukan selama 5 menit di depan 2-3 evaluator yang tidak memberikan umpan balik positif</li>
                <li>Dilanjutkan dengan tugas aritmatika yang sulit (pengurangan serial 13 dari 1022) selama 5 menit</li>
                <li>Jika subjek membuat kesalahan, diminta mulai dari awal</li>
            </ul>
            <p><em>Referensi: Kirschbaum, C., Pirke, K. M., & Hellhammer, D. H. (1993). The 'Trier Social Stress Test'—a tool for investigating psychobiological stress responses in a laboratory setting. Neuropsychobiology, 28(1-2), 76-81.</em></p>
        </div>
        """, unsafe_allow_html=True)
    else:  # Relaksasi
        st.markdown("""
        <div class="info-box">
            <h3>Pengkondisian Relaksasi:</h3>
            <ul>
                <li>Progressive Muscle Relaxation (PMR) atau latihan pernapasan dalam</li>
                <li>Mendengarkan musik menenangkan selama 10-15 menit</li>
                <li>Visualisasi tempat yang menyenangkan/damai</li>
            </ul>
            <p><em>Referensi: Pawlow, L. A., & Jones, G. E. (2002). The impact of abbreviated progressive muscle relaxation on salivary cortisol. Biological Psychology, 60(1), 1-16.</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tombol lanjut ke halaman berikutnya
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("Simpan dan Lanjutkan", use_container_width=True):
            # Simpan pilihan pengkondisian ke data diri
            st.session_state.data_diri["Pengkondisian"] = pengkondisian
            st.session_state.data_diri["Timestamp Pengkondisian"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.pengkondisian_submitted = True
            # Pindah ke halaman pengaturan cerita
            st.session_state.page = "cerita_setup"
            st.experimental_rerun()

# Halaman pengaturan cerita
def cerita_setup_page():
    st.title("Pengaturan Cerita")
    
    # Dengan sidebar untuk menampilkan informasi
    with st.sidebar:
        st.header("Informasi")
        st.info("""
        Kuesioner ini terdiri dari:
        - Data Diri
        - Pengkondisian berdasarkan TSST
        - Depression, Anxiety, Stress Scale (DASS-21)
        - Kuesioner Respons Stres Akut 
        
        Hasil akan dapat diunduh dalam format CSV.
        """)
        
        with st.expander("Tentang TSST (Trier Social Stress Test)"):
            st.markdown("""
            **Trier Social Stress Test (TSST)** adalah protokol standar untuk menginduksi stres dalam kondisi laboratorium. 
            
            Dikembangkan oleh Kirschbaum et al. (1993), TSST melibatkan kombinasi tekanan psikososial melalui:
            - Presentasi di depan evaluator
            - Tugas aritmatika dengan tekanan waktu
            - Evaluasi sosial
            
            TSST telah terbukti mampu menginduksi respons stres yang terukur dan konsisten dalam berbagai penelitian.
            """)
    
    # Tampilkan data diri dalam bentuk card
    st.markdown("""
    <style>
    .data-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="data-card">
        <h3>Data Peserta</h3>
        <p><strong>Nama:</strong> {st.session_state.data_diri['Nama']}</p>
        <p><strong>Umur:</strong> {st.session_state.data_diri['Umur']}</p>
        <p><strong>Jenis Kelamin:</strong> {st.session_state.data_diri['Jenis Kelamin']}</p>
        <p><strong>Pengkondisian:</strong> {st.session_state.data_diri['Pengkondisian']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Pengaturan teks
    st.header("Pengaturan Tampilan Teks")
    col1, col2 = st.columns(2)
    
    with col1:
        font_size = st.slider("Ukuran Font", min_value=12, max_value=24, value=st.session_state.font_size, step=1)
        st.session_state.font_size = font_size
    
    with col2:
        st.session_state.auto_scroll = st.checkbox("Auto-Scroll", value=st.session_state.auto_scroll)
        if st.session_state.auto_scroll:
            scroll_speed = st.slider("Kecepatan Scroll", min_value=0.5, max_value=5.0, value=float(st.session_state.scroll_speed), step=0.5)
            st.session_state.scroll_speed = float(scroll_speed)
    
    # Tombol untuk memulai pembacaan cerita
    st.header("Mulai Pembacaan Cerita")
    
    # Coba membaca file "Kumpulan Cerita.docx" secara langsung
    file_path = "Kumpulan Cerita.docx"
    if 'stories_loaded' not in st.session_state:
        stories = extract_stories_from_docx(file_path)
        if stories:
            st.session_state.stories = stories
            st.session_state.stories_loaded = True
        else:
            st.session_state.stories = predefined_stories
            st.session_state.stories_loaded = True
    
    col_btn = st.columns([1, 2, 1])
    with col_btn[1]:
        if st.button("Acak Cerita dan Mulai Membaca", use_container_width=True):
            if st.session_state.stories:
                st.session_state.selected_story = random.choice(st.session_state.stories)
                
                # Simpan data tambahan ke data_diri
                st.session_state.data_diri["Judul Cerita"] = st.session_state.selected_story["judul"]
                st.session_state.data_diri["Waktu Tampil"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Pindah ke halaman cerita
                st.session_state.page = "cerita"
                st.experimental_rerun()

# Halaman cerita
def cerita_page():
    # Tombol kecil untuk kembali ke pengaturan
    if st.button("⬅️ Kembali ke Pengaturan", key="back_btn"):
        st.session_state.page = "cerita_setup"
        st.experimental_rerun()
    
    selected_story = st.session_state.selected_story
    
    # CSS untuk membuat teks format Google Docs
    auto_scroll_css = ""
    if st.session_state.auto_scroll:
        # Tambahkan CSS untuk auto-scroll
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
    .main-container {{
        padding: 0;
        max-width: 1000px !important;
    }}
    {auto_scroll_css}
    </style>
    """, unsafe_allow_html=True)
    
    # Override default Streamlit container width
    st.markdown("""
    <style>
    .block-container {
        max-width: 1000px;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Format teks paragraf dengan tag <p>
    paragraphs = selected_story['isi'].split('\n\n')
    formatted_text = ""
    for para in paragraphs:
        if para.strip():
            formatted_text += f"<p>{para}</p>"
    
    # Tambahkan JavaScript untuk auto-scroll jika diperlukan
    if st.session_state.auto_scroll:
        st.markdown(f"""
        <script>
            // JavaScript untuk smooth autoscroll
            document.addEventListener('DOMContentLoaded', (event) => {{
                // Fungsi untuk scroll otomatis
                function autoScroll() {{
                    window.scrollBy(0, {st.session_state.scroll_speed});
                    scrolldelay = setTimeout(autoScroll, 10);
                }}
                
                // Mulai auto-scroll setelah sedikit delay
                setTimeout(autoScroll, 1000);
            }});
        </script>
        """, unsafe_allow_html=True)
        
        # Tampilkan judul dan konten cerita dengan gaya Google Docs
        st.markdown(f'<div class="gdocs-title">{selected_story["judul"]}</div>', unsafe_allow_html=True)
        
        # Wrap dalam container untuk efek scroll
        st.markdown(f"""
        <div class="scroll-container">
            <div class="gdocs-text">{formatted_text}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Tambahkan JavaScript untuk inisialisasi scroll
        st.markdown("""
        <script>
            // Script untuk memastikan scroll container bekerja
            window.onload = function() {
                // Scroll to top first to ensure proper start
                window.scrollTo(0, 0);
            }
        </script>
        """, unsafe_allow_html=True)
    else:
        # Tampilan normal tanpa auto-scroll
        st.markdown(f'<div class="gdocs-title">{selected_story["judul"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="gdocs-text">{formatted_text}</div>', unsafe_allow_html=True)

def main():
    # Sembunyikan semua pesan otomatis
    
    # Inisialisasi session state jika belum ada
    if 'stories' not in st.session_state:
        st.session_state.stories = predefined_stories
    
    if 'font_size' not in st.session_state:
        st.session_state.font_size = 16
    
    if 'auto_scroll' not in st.session_state:
        st.session_state.auto_scroll = False
        
    if 'scroll_speed' not in st.session_state:
        st.session_state.scroll_speed = 1.0
        
    if 'data_diri_submitted' not in st.session_state:
        st.session_state.data_diri_submitted = False
        
    if 'pengkondisian_submitted' not in st.session_state:
        st.session_state.pengkondisian_submitted = False
        
    if 'data_diri' not in st.session_state:
        st.session_state.data_diri = {}
        
    if 'page' not in st.session_state:
        st.session_state.page = "info"
    
    # Tampilkan halaman yang sesuai
    if st.session_state.page == "info":
        info_page()
    elif st.session_state.page == "data_diri":
        data_diri_page()
    elif st.session_state.page == "pengkondisian":
        pengkondisian_page()
    elif st.session_state.page == "cerita_setup":
        cerita_setup_page()
    elif st.session_state.page == "cerita":
        cerita_page()

if __name__ == "__main__":
    main()
