# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="EngsetPro Professional",
    page_icon="📡",
    layout="wide"
)

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<div class="unpix-header">
    <div class="header-title">📡 EngsetPro Professional</div>
    <div class="header-subtitle">
        Sistem Analisis Probabilitas Blocking Engset Profesional
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
    st.info("Aplikasi Simulasi Teknik Telekomunikasi")

# =====================================================
# DASHBOARD
# =====================================================
if page == "🏠 Dashboard":

    st.markdown("""
    <div class="section-title">
        📥 Input Parameter Sistem
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="input-card">', unsafe_allow_html=True)

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
            step=0.01,
            format="%.2f"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    run = st.button("🚀 JALANKAN ANALISIS")

    if run:

        if N >= S:

            st.error(
                "⚠️ Jumlah kanal (N) harus lebih kecil dari jumlah sumber (S)"
            )

        else:

            M, Pb, iter_data, iteration = iterate(S, N, rho)

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
            st.session_state.history.append(result)

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
                    Probabilitas Blocking
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-value">
                    {r['M']:.6f}
                </div>
                <div class="metric-label">
                    Traffic Idle (M)
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-value">
                    {r['iter']}
                </div>
                <div class="metric-label">
                    Jumlah Iterasi
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
# ANALYSIS PAGE
# =====================================================
elif page == "📊 Analisis":

    st.markdown("""
    <div class="section-title">
        📊 Analisis Sistem
    </div>
    """, unsafe_allow_html=True)

    if "result" not in st.session_state:

        st.warning(
            "⚠️ Jalankan simulasi terlebih dahulu di Dashboard"
        )

    else:

        r = st.session_state.result

        st.markdown("""
        <div class="section-title">
            🔁 Tabel Iterasi Konvergensi
        </div>
        """, unsafe_allow_html=True)

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
            use_container_width=True,
            hide_index=True
        )

        st.markdown("""
        <div class="section-title">
            📈 Grafik Probabilitas Blocking
        </div>
        """, unsafe_allow_html=True)

        S = r["S"]
        rho = r["rho"]

        x = list(range(1, S))

        y = [
            engset_pb(S, n, rho)
            for n in x
        ]

        fig, ax = plt.subplots(figsize=(10, 4))

        fig.patch.set_facecolor('#f8faff')
        ax.set_facecolor('#f8faff')

        ax.plot(
            x,
            y,
            linewidth=2.5,
            marker='o'
        )

        ax.axhline(
            0.2,
            linestyle="--",
            linewidth=1.5,
            label="Ambang Batas 0.2"
        )

        ax.set_xlabel("Jumlah Kanal")
        ax.set_ylabel("Probabilitas Blocking")

        ax.grid(True)

        ax.legend()

        st.pyplot(fig)

# =====================================================
# HISTORY PAGE
# =====================================================
elif page == "📁 Riwayat":

    st.markdown("""
    <div class="section-title">
        📁 Riwayat Simulasi
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.history:

        rows = []

        for i, r in enumerate(st.session_state.history, 1):

            rows.append({
                "No": i,
                "Waktu": r["time"],
                "S": r["S"],
                "N": r["N"],
                "ρ": r["rho"],
                "M": round(r["M"], 6),
                "Pb": round(r["Pb"], 6),
                "Iterasi": r["iter"],
                "Status": r["status"]
            })

        df_history = pd.DataFrame(rows)

        st.dataframe(
            df_history,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "📭 Belum ada riwayat simulasi"
        )

# =====================================================
# EXPORT SECTION
# =====================================================
if "result" in st.session_state:

    st.markdown("---")

    st.markdown("""
    <div class="section-title">
        📥 Export Laporan Profesional
    </div>
    """, unsafe_allow_html=True)

    latest = st.session_state.result

    S = latest["S"]
    rho = latest["rho"]

    x = list(range(1, S))

    y = [
        engset_pb(S, n, rho)
        for n in x
    ]

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(
        x,
        y,
        linewidth=2.5,
        marker='o'
    )

    ax.grid(True)

    pdf = export_pdf(latest, fig)

    st.download_button(
        label="⬇️ Download Laporan PDF",
        data=pdf,
        file_name="Laporan_EngsetPro.pdf",
        mime="application/pdf"
    )
