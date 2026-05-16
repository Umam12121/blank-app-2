import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from math import factorial
from datetime import datetime
import io

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    HRFlowable
)

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER


# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="EngsetPro Professional",
    page_icon="📡",
    layout="wide"
)


# =====================================================
# STYLE CSS
# =====================================================
st.markdown("""
<style>

body {
    font-family: sans-serif;
}

.unpix-header {
    background: linear-gradient(90deg,#1d4ed8,#2563eb);
    padding: 30px;
    border-radius: 20px;
    color: white;
    margin-bottom: 20px;
}

.header-title {
    font-size: 32px;
    font-weight: bold;
}

.header-subtitle {
    font-size: 15px;
    opacity: 0.9;
}

.section-title {
    font-size: 24px;
    font-weight: bold;
    margin-top: 20px;
    margin-bottom: 15px;
    color: #1d4ed8;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4,1fr);
    gap: 15px;
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #dbeafe;
    text-align: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.metric-value {
    font-size: 22px;
    font-weight: bold;
    color: #1d4ed8;
}

.metric-label {
    margin-top: 10px;
    color: #64748b;
}

.input-card {
    background: white;
    padding: 20px;
    border-radius: 20px;
    border: 1px solid #dbeafe;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# SESSION STATE
# =====================================================
if "history" not in st.session_state:
    st.session_state.history = []


# =====================================================
# RUMUS ENGSET
# =====================================================
def nCr(n, r):

    if r > n:
        return 0

    return factorial(n) // (
        factorial(r) * factorial(n - r)
    )


def engset_pb(S, N, M):

    num = nCr(S - 1, N) * (M ** N)

    den = sum(
        nCr(S - 1, k) * (M ** k)
        for k in range(N + 1)
    )

    if den == 0:
        return 0

    return num / den


def iterate(S, N, rho):

    M = rho

    tol = 0.0001

    data = []

    i = 1

    while True:

        Pb = engset_pb(S, N, M)

        M_new = rho * (1 - Pb)

        diff = abs(M_new - M)

        data.append([
            i,
            round(M, 8),
            round(Pb, 8),
            round(diff, 8)
        ])

        if diff < tol:
            break

        M = M_new

        i += 1

    return M_new, Pb, data, i


# =====================================================
# EXPORT PDF
# =====================================================
def export_pdf(data, fig):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'title',
        parent=styles['Title'],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1d4ed8")
    )

    elements = []

    elements.append(
        Paragraph(
            "LAPORAN ENGSETPRO",
            title_style
        )
    )

    elements.append(Spacer(1, 20))

    table_data = [
        ["Parameter", "Nilai"],
        ["Jumlah Sumber (S)", str(data["S"])],
        ["Jumlah Kanal (N)", str(data["N"])],
        ["Traffic per Sumber", str(data["rho"])],
        ["Blocking Probability", f"{data['Pb']:.6f}"],
        ["Traffic Idle", f"{data['M']:.6f}"],
        ["Iterasi", str(data["iter"])],
        ["Status", data["status"]],
    ]

    table = Table(table_data, colWidths=[7*cm, 7*cm])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1d4ed8")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BACKGROUND", (0,1), (-1,-1), colors.whitesmoke),
    ]))

    elements.append(table)

    elements.append(Spacer(1, 20))

    img_buffer = io.BytesIO()

    fig.savefig(img_buffer, format='png')

    img_buffer.seek(0)

    elements.append(
        Image(
            img_buffer,
            width=15*cm,
            height=7*cm
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"Laporan dibuat pada {data['time']}",
            styles['Normal']
        )
    )

    doc.build(elements)

    buffer.seek(0)

    return buffer


# =====================================================
# HEADER
# =====================================================
st.markdown("""
<div class="unpix-header">
    <div class="header-title">
        📡 EngsetPro Professional
    </div>

    <div class="header-subtitle">
        Sistem Analisis Probabilitas Blocking Engset
    </div>
</div>
""", unsafe_allow_html=True)


# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:

    st.title("📂 Navigasi")

    page = st.radio(
        "Pilih Menu",
        [
            "🏠 Dashboard",
            "📊 Analisis",
            "📁 Riwayat"
        ]
    )

    st.markdown("---")

    st.info(
        "Aplikasi simulasi sistem telekomunikasi"
    )


# =====================================================
# DASHBOARD
# =====================================================
if page == "🏠 Dashboard":

    st.markdown("""
    <div class="section-title">
        📥 Input Parameter Sistem
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="input-card">',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        S = st.number_input(
            "Jumlah Sumber (S)",
            min_value=1,
            value=10
        )

    with col2:

        N = st.number_input(
            "Jumlah Kanal (N)",
            min_value=1,
            value=3
        )

    with col3:

        rho = st.number_input(
            "Traffic per Sumber (ρ)",
            min_value=0.0,
            value=0.5,
            step=0.01
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    run = st.button(
        "🚀 Jalankan Analisis"
    )

    if run:

        if N >= S:

            st.error(
                "Jumlah kanal harus lebih kecil dari jumlah sumber"
            )

        else:

            M, Pb, iter_data, iteration = iterate(
                S,
                N,
                rho
            )

            status = (
                "OPTIMAL"
                if Pb < 0.2
                else "PADAT"
            )

            result = {
                "S": S,
                "N": N,
                "rho": rho,
                "M": M,
                "Pb": Pb,
                "iter": iteration,
                "status": status,
                "iter_data": iter_data,
                "time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            }

            st.session_state.result = result

            st.session_state.history.append(
                result
            )

    if "result" in st.session_state:

        r = st.session_state.result

        st.markdown("""
        <div class="section-title">
            📊 Hasil Simulasi
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-grid">

            <div class="metric-card">
                <div class="metric-value">
                    {r['Pb']:.6f}
                </div>

                <div class="metric-label">
                    Blocking Probability
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-value">
                    {r['M']:.6f}
                </div>

                <div class="metric-label">
                    Traffic Idle
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-value">
                    {r['iter']}
                </div>

                <div class="metric-label">
                    Iterasi
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-value">
                    {r['status']}
                </div>

                <div class="metric-label">
                    Status Sistem
                </div>
            </div>

        </div>
        """, unsafe_allow_html=True)


# =====================================================
# ANALISIS
# =====================================================
elif page == "📊 Analisis":

    st.markdown("""
    <div class="section-title">
        📊 Analisis Sistem
    </div>
    """, unsafe_allow_html=True)

    if "result" not in st.session_state:

        st.warning(
            "Jalankan simulasi terlebih dahulu"
        )

    else:

        r = st.session_state.result

        df = pd.DataFrame(
            r["iter_data"],
            columns=[
                "Iterasi",
                "M",
                "Pb",
                "Selisih"
            ]
        )

        st.dataframe(
            df,
            use_container_width=True
        )

        S = r["S"]

        rho = r["rho"]

        x = list(range(1, S))

        y = [
            engset_pb(S, n, rho)
            for n in x
        ]

        fig, ax = plt.subplots(figsize=(10,4))

        ax.plot(
            x,
            y,
            marker='o',
            linewidth=2
        )

        ax.axhline(
            0.2,
            linestyle='--',
            label='Threshold'
        )

        ax.set_xlabel(
            "Jumlah Kanal"
        )

        ax.set_ylabel(
            "Blocking Probability"
        )

        ax.grid(True)

        ax.legend()

        st.pyplot(fig)


# =====================================================
# RIWAYAT
# =====================================================
elif page == "📁 Riwayat":

    st.markdown("""
    <div class="section-title">
        📁 Riwayat Simulasi
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.history:

        rows = []

        for i, r in enumerate(
            st.session_state.history,
            1
        ):

            rows.append({
                "No": i,
                "Waktu": r["time"],
                "S": r["S"],
                "N": r["N"],
                "ρ": r["rho"],
                "Pb": round(r["Pb"], 6),
                "Status": r["status"]
            })

        df_history = pd.DataFrame(rows)

        st.dataframe(
            df_history,
            use_container_width=True
        )

    else:

        st.info(
            "Belum ada riwayat simulasi"
        )


# =====================================================
# EXPORT PDF
# =====================================================
if "result" in st.session_state:

    st.markdown("---")

    latest = st.session_state.result

    S = latest["S"]

    rho = latest["rho"]

    x = list(range(1, S))

    y = [
        engset_pb(S, n, rho)
        for n in x
    ]

    fig, ax = plt.subplots(figsize=(10,4))

    ax.plot(
        x,
        y,
        marker='o'
    )

    ax.grid(True)

    pdf = export_pdf(
        latest,
        fig
    )

    st.download_button(
        label="⬇️ Download PDF",
        data=pdf,
        file_name="Laporan_EngsetPro.pdf",
        mime="application/pdf"
    )
