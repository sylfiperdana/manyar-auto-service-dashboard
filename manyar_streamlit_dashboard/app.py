from __future__ import annotations

import base64
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# KONFIGURASI APLIKASI & PENCARIAN LOGO
# ============================================================

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"

LOGO_CANDIDATES = [
    APP_DIR / "logo.png",
    Path.cwd() / "logo.png",
    APP_DIR / "assets" / "logo.png",
]
LOGO_PATH = next((p for p in LOGO_CANDIDATES if p.is_file()), None)

st.set_page_config(
    page_title="Manyar Auto Service | Business Intelligence",
    page_icon=str(LOGO_PATH) if LOGO_PATH else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

SERVICE_FILE = "dashboard_service.csv"
INVENTORY_FILE = "dashboard_inventory.csv"
USAGE_FILE = "dashboard_usage.csv"

SERVICE_REQUIRED = {
    "id_servis",
    "tanggal_servis",
    "bulan",
    "jenis_pelanggan",
    "jenis_servis",
    "kategori_kerusakan",
    "tingkat_keparahan",
    "jumlah_item_rencana",
    "status_acc",
    "durasi_pengerjaan_menit",
    "estimasi_menit",
    "selisih_estimasi",
    "biaya_sparepart",
    "waktu_antre_menit",
}

INVENTORY_REQUIRED = {
    "kode_sparepart",
    "nama_sparepart",
    "kategori_sparepart",
    "stok_awal",
    "stok_masuk",
    "stok_keluar",
    "stok_akhir",
    "stok_minimum",
}

USAGE_REQUIRED = {
    "id_penggunaan",
    "id_servis",
    "tanggal_servis",
    "kode_sparepart",
    "nama_sparepart",
    "jumlah",
    "harga_satuan",
    "total_biaya_sparepart",
}

# ============================================================
# PALET WARNA SELARAS WEB MANYAR AUTO SERVICE
# ============================================================

MAS_RED = "#E60000"
MAS_RED_DARK = "#DC2626"
MAS_RED_SOFT = "#FEF2F2"
MAS_RED_BORDER = "#FECACA"
BG_PAGE = "#F8F9FA"
BG_CARD = "#FFFFFF"
BORDER_LIGHT = "#E5E7EB"
DARK = "#1F2937"
MUTED = "#4B5563"


# ============================================================
# CUSTOM SVG ICONS (SINGLE-LINE AGAR AMAN DI MARKDOWN)
# ============================================================

def svg_icon(name: str, color: str = "currentColor", size: int = 18) -> str:
    icons = {
        "dashboard": (
            f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f'<rect x="3" y="3" width="7" height="7" rx="1"></rect>'
            f'<rect x="14" y="3" width="7" height="7" rx="1"></rect>'
            f'<rect x="14" y="14" width="7" height="7" rx="1"></rect>'
            f'<rect x="3" y="14" width="7" height="7" rx="1"></rect></svg>'
        ),
        "inventory": (
            f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>'
            f'<polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>'
            f'<line x1="12" y1="22.08" x2="12" y2="12"></line></svg>'
        ),
        "info": (
            f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            f'<circle cx="12" cy="12" r="10"></circle>'
            f'<line x1="12" y1="16" x2="12" y2="12"></line>'
            f'<line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
        ),
    }
    return icons.get(name, "")


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    f"""<style>
.stApp {{
    background-color: {BG_PAGE};
    color: {DARK};
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}
header[data-testid="stHeader"] {{
    background-color: rgba(248, 249, 250, 0.85);
    backdrop-filter: blur(6px);
}}
.block-container {{
    padding-top: 3.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1480px;
}}
[data-testid="stSidebar"] {{
    background-color: {BG_CARD};
    border-right: 1px solid {BORDER_LIGHT};
}}
[data-testid="stSidebar"] .block-container {{
    padding-top: 1.5rem !important;
}}
.sidebar-brand {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 4px 2px 16px 2px;
    border-bottom: 1px solid {BORDER_LIGHT};
    margin-bottom: 16px;
}}
.sidebar-brand-title {{
    font-size: 1.02rem;
    font-weight: 700;
    color: {DARK};
    line-height: 1.2;
}}
.sidebar-brand-sub {{
    font-size: 0.75rem;
    color: #6B7280;
    font-weight: 500;
}}
.nav-pill-active {{
    background-color: {MAS_RED_SOFT};
    color: {MAS_RED_DARK};
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 0.9rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 18px;
}}
[data-testid="stSidebar"] span[data-baseweb="tag"],
span[data-baseweb="tag"] {{
    background-color: {MAS_RED_SOFT} !important;
    color: {MAS_RED_DARK} !important;
    border: 1px solid {MAS_RED_BORDER} !important;
    border-radius: 6px !important;
}}
span[data-baseweb="tag"] span {{
    color: {MAS_RED_DARK} !important;
    font-weight: 600 !important;
}}
span[data-baseweb="tag"] svg {{
    fill: {MAS_RED_DARK} !important;
}}
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="input"] > div:focus-within {{
    border-color: {MAS_RED} !important;
    box-shadow: 0 0 0 1px {MAS_RED} !important;
}}
.top-navbar {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_LIGHT};
    border-radius: 12px;
    padding: 16px 22px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}}
.top-navbar-left {{
    display: flex;
    align-items: center;
    gap: 16px;
}}
.eyebrow {{
    color: {MAS_RED};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.72rem;
    font-weight: 700;
    margin-bottom: 3px;
}}
.main-title {{
    font-size: 1.55rem;
    line-height: 1.2;
    font-weight: 700;
    color: {DARK};
    margin: 0;
}}
.subtitle {{
    color: #6B7280;
    font-size: 0.88rem;
    margin-top: 4px;
}}
.status-badge {{
    background-color: {MAS_RED_SOFT};
    color: {MAS_RED_DARK};
    border: 1px solid {MAS_RED_BORDER};
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}}
.status-dot {{
    height: 8px;
    width: 8px;
    background-color: {MAS_RED};
    border-radius: 50%;
    display: inline-block;
}}
div[data-testid="stMetric"] {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_LIGHT};
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}}
div[data-testid="stMetric"]:hover {{
    border-color: {MAS_RED_BORDER};
    box-shadow: 0 4px 10px rgba(230, 0, 0, 0.05);
}}
div[data-testid="stMetricLabel"] p {{
    color: #6B7280 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}}
div[data-testid="stMetricValue"] div {{
    color: {DARK} !important;
    font-size: 1.65rem !important;
    font-weight: 700 !important;
}}
/* Navigasi Tab Garis Bawah Merah */
div[data-testid="stTabs"] button[data-baseweb="tab"] {{
    background-color: transparent !important;
    border: none !important;
    padding: 10px 20px !important;
    color: {MUTED} !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    transition: color 0.15s ease;
}}
div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {{
    color: {MAS_RED} !important;
}}
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {{
    color: {MAS_RED} !important;
    font-weight: 700 !important;
}}
div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {{
    background-color: {MAS_RED} !important;
    height: 3px !important;
    border-radius: 3px 3px 0 0 !important;
}}
div[data-testid="stTabs"] div[data-baseweb="tab-border"] {{
    background-color: {BORDER_LIGHT} !important;
}}
.insight-card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_LIGHT};
    border-top: 3px solid {MAS_RED};
    border-radius: 12px;
    padding: 16px 18px;
    min-height: 150px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}}
.insight-kicker {{
    color: {MAS_RED};
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 6px;
}}
.insight-title {{
    color: {DARK};
    font-size: 1.02rem;
    font-weight: 700;
    margin-bottom: 6px;
}}
.insight-body {{
    color: #6B7280;
    font-size: 0.87rem;
    line-height: 1.5;
}}
.rec-card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_LIGHT};
    border-radius: 12px;
    padding: 16px 18px;
    height: 100%;
}}
.rec-number {{
    display: inline-block;
    background-color: {MAS_RED_SOFT};
    color: {MAS_RED_DARK};
    font-weight: 700;
    font-size: 0.78rem;
    padding: 3px 10px;
    border-radius: 6px;
    margin-bottom: 8px;
}}
.clean-callout {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_LIGHT};
    border-left: 4px solid {MAS_RED};
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 14px;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.88rem;
    color: {DARK};
}}
.stDownloadButton > button {{
    background-color: {MAS_RED};
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.45rem 1rem;
}}
.stDownloadButton > button:hover {{
    background-color: {MAS_RED_DARK};
    color: #FFFFFF;
}}
</style>""",
    unsafe_allow_html=True,
)


# ============================================================
# FUNGSI BANTU & DATA
# ============================================================

@st.cache_data
def get_logo_base64(path_str: str | None) -> str | None:
    if not path_str:
        return None
    p = Path(path_str)
    if not p.is_file():
        return None
    return base64.b64encode(p.read_bytes()).decode("utf-8")


def locate_data_file(filename: str) -> Path | None:
    candidates = [DATA_DIR / filename, APP_DIR / filename, Path.cwd() / "data" / filename]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


@st.cache_data(show_spinner="Memuat dataset dashboard...")
def read_csv_cached(path_string: str) -> pd.DataFrame:
    return pd.read_csv(path_string)


def load_dataset(filename: str, required: set[str]) -> pd.DataFrame:
    path = locate_data_file(filename)
    if path is None:
        st.error(
            f"File **{filename}** belum ditemukan. "
            f"Letakkan file tersebut di folder `{DATA_DIR.name}/`."
        )
        st.stop()

    try:
        df = read_csv_cached(str(path))
    except Exception as exc:
        st.error(f"Gagal membaca `{filename}`: {exc}")
        st.stop()

    missing = sorted(required.difference(df.columns))
    if missing:
        st.error(
            f"Kolom pada `{filename}` belum sesuai. "
            f"Kolom yang tidak ditemukan: {', '.join(missing)}"
        )
        st.stop()

    return df


def to_numeric_columns(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def rupiah(value: float | int) -> str:
    value = float(value) if pd.notna(value) else 0.0
    if abs(value) >= 1_000_000_000:
        return f"Rp{value / 1_000_000_000:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " miliar"
    if abs(value) >= 1_000_000:
        return f"Rp{value / 1_000_000:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " juta"
    return "Rp" + f"{value:,.0f}".replace(",", ".")


def angka(value: float | int, decimals: int = 0) -> str:
    if pd.isna(value):
        return "—"
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def insight_card(kicker: str, title: str, body: str) -> None:
    html = (
        f'<div class="insight-card">'
        f'<div class="insight-kicker">{kicker}</div>'
        f'<div class="insight-title">{title}</div>'
        f'<div class="insight-body">{body}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_callout(icon_name: str, content_html: str) -> None:
    html = (
        f'<div class="clean-callout">'
        f'{svg_icon(icon_name, MAS_RED, 18)}'
        f'<div>{content_html}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def chart_layout(fig, height: int = 350):
    fig.update_layout(
        height=height,
        margin=dict(l=14, r=32, t=54, b=14),  # r & t diperbesar agar label lega
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_CARD,
        font=dict(color=DARK, family="Inter, Arial, sans-serif"),
        title_font=dict(size=15, color=DARK),
        legend_title_text="",
        hoverlabel=dict(bgcolor="white", font_color=DARK, bordercolor=BORDER_LIGHT),
    )
    fig.update_xaxes(showgrid=False, linecolor=BORDER_LIGHT)
    fig.update_yaxes(gridcolor="#F3F4F6", zeroline=False)
    return fig


# ============================================================
# MEMUAT DATASET HASIL ETL NOTEBOOK
# ============================================================

service = load_dataset(SERVICE_FILE, SERVICE_REQUIRED)
inventory = load_dataset(INVENTORY_FILE, INVENTORY_REQUIRED)
usage = load_dataset(USAGE_FILE, USAGE_REQUIRED)

service["tanggal_servis"] = pd.to_datetime(service["tanggal_servis"], errors="coerce")
usage["tanggal_servis"] = pd.to_datetime(usage["tanggal_servis"], errors="coerce")

service = to_numeric_columns(
    service,
    [
        "jumlah_item_rencana",
        "durasi_pengerjaan_menit",
        "estimasi_menit",
        "selisih_estimasi",
        "biaya_sparepart",
        "waktu_antre_menit",
    ],
)
inventory = to_numeric_columns(
    inventory,
    ["stok_awal", "stok_masuk", "stok_keluar", "stok_akhir", "stok_minimum"],
)
usage = to_numeric_columns(
    usage,
    ["jumlah", "harga_satuan", "total_biaya_sparepart"],
)

service["status_acc"] = service["status_acc"].astype(str).str.strip()
service["kategori_kerusakan"] = service["kategori_kerusakan"].astype(str).str.strip()
service["tingkat_keparahan"] = service["tingkat_keparahan"].astype(str).str.strip()

service["bulan"] = service["tanggal_servis"].dt.strftime("%Y-%m")
usage["bulan"] = usage["tanggal_servis"].dt.strftime("%Y-%m")

inventory["kritis"] = inventory["stok_akhir"] <= inventory["stok_minimum"]
inventory["selisih_stok"] = inventory["stok_akhir"] - inventory["stok_minimum"]

if service["tanggal_servis"].notna().sum() == 0:
    st.error("Kolom tanggal_servis tidak memiliki tanggal valid.")
    st.stop()


# ============================================================
# SIDEBAR: BRANDING WEB & FILTER GLOBAL
# ============================================================

logo_b64 = get_logo_base64(str(LOGO_PATH) if LOGO_PATH else None)

with st.sidebar:
    if logo_b64:
        brand_html = (
            f'<div class="sidebar-brand">'
            f'<img src="data:image/png;base64,{logo_b64}" width="44" style="border-radius: 6px; object-fit: contain;">'
            f'<div>'
            f'<div class="sidebar-brand-title">Manyar Auto Service</div>'
            f'<div class="sidebar-brand-sub">BI &amp; Analytics Portal</div>'
            f'</div></div>'
        )
        st.markdown(brand_html, unsafe_allow_html=True)
    else:
        st.markdown("## Manyar Auto Service")
        st.caption("BI & Analytics Portal")

    nav_pill_html = (
        f'<div class="nav-pill-active">'
        f'{svg_icon("dashboard", MAS_RED_DARK, 18)}'
        f'<span>Dashboard</span></div>'
    )
    st.markdown(nav_pill_html, unsafe_allow_html=True)

    st.markdown("#### Filter Data")

    valid_dates = service["tanggal_servis"].dropna()
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    selected_dates = st.date_input(
        "Rentang tanggal servis",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        format="DD/MM/YYYY",
    )

    if isinstance(selected_dates, (tuple, list)):
        if len(selected_dates) == 2:
            start_date, end_date = selected_dates
        elif len(selected_dates) == 1:
            start_date = end_date = selected_dates[0]
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date = end_date = selected_dates

    category_options = sorted(service["kategori_kerusakan"].dropna().unique().tolist())
    severity_order = ["Ringan", "Sedang", "Berat"]
    available_severity = [
        item for item in severity_order
        if item in service["tingkat_keparahan"].dropna().unique()
    ]
    available_severity += sorted(
        set(service["tingkat_keparahan"].dropna().unique()) - set(available_severity)
    )

    selected_categories = st.multiselect(
        "Kategori pekerjaan/kerusakan",
        options=category_options,
        default=category_options,
    )
    selected_severities = st.multiselect(
        "Tingkat keparahan",
        options=available_severity,
        default=available_severity,
    )

mask = (
    service["tanggal_servis"].dt.date.between(start_date, end_date)
    & service["kategori_kerusakan"].isin(selected_categories)
    & service["tingkat_keparahan"].isin(selected_severities)
)
filtered = service.loc[mask].copy()

usage["id_servis"] = usage["id_servis"].astype(str)
filtered_service_ids = set(filtered["id_servis"].astype(str))
usage_mask = (
    usage["tanggal_servis"].dt.date.between(start_date, end_date)
    & usage["id_servis"].isin(filtered_service_ids)
)
filtered_usage = usage.loc[usage_mask].copy()

filtered_inventory = inventory.copy()
critical_inventory = filtered_inventory.loc[
    filtered_inventory["kritis"]
].sort_values("selisih_stok")


# ============================================================
# HEADER ALA TOPBAR WEB MANYAR AUTO SERVICE
# ============================================================

logo_html = (
    f'<img src="data:image/png;base64,{logo_b64}" width="54" style="object-fit: contain;">'
    if logo_b64
    else ""
)
jumlah_terfilter_str = angka(len(filtered))

header_html = (
    f'<div class="top-navbar">'
    f'<div class="top-navbar-left">'
    f'{logo_html}'
    f'<div>'
    f'<div class="eyebrow">CV. MANYAR AUTO SERVICE</div>'
    f'<div class="main-title">Business Intelligence Dashboard</div>'
    f'<div class="subtitle">Monitoring performa servis, akurasi estimasi pengerjaan, biaya sparepart, dan stok inventori.</div>'
    f'</div></div>'
    f'<div><span class="status-badge"><span class="status-dot"></span>'
    f'Periode: {start_date.strftime("%d/%m/%Y")} – {end_date.strftime("%d/%m/%Y")} ({jumlah_terfilter_str} servis)'
    f'</span></div></div>'
)
st.markdown(header_html, unsafe_allow_html=True)


# ============================================================
# KPI: ENAM INDIKATOR
# ============================================================

total_servis = len(filtered)
jumlah_acc = int(filtered["status_acc"].eq("ACC").sum())
acc_rate = (jumlah_acc / total_servis * 100) if total_servis else 0.0

filtered_acc = filtered.loc[
    filtered["status_acc"].eq("ACC")
    & filtered["durasi_pengerjaan_menit"].notna()
].copy()

avg_duration = (
    filtered_acc["durasi_pengerjaan_menit"].mean()
    if not filtered_acc.empty else np.nan
)

valid_mape = filtered_acc.loc[
    filtered_acc["estimasi_menit"].notna()
    & (filtered_acc["durasi_pengerjaan_menit"] > 0)
].copy()

if not valid_mape.empty:
    mape = (
        (
            valid_mape["estimasi_menit"]
            - valid_mape["durasi_pengerjaan_menit"]
        ).abs()
        / valid_mape["durasi_pengerjaan_menit"]
    ).mean() * 100
else:
    mape = np.nan

critical_count = int(filtered_inventory["kritis"].sum())
inventory_count = len(filtered_inventory)
total_cost = filtered["biaya_sparepart"].fillna(0).sum()

st.markdown("#### Ringkasan Indikator Utama")

kpi_row_1 = st.columns(3)
kpi_row_1[0].metric(
    "Total Servis",
    angka(total_servis),
    help="Jumlah record servis sesuai filter."
)
kpi_row_1[1].metric(
    "Tingkat Persetujuan (ACC Rate)",
    f"{angka(acc_rate, 2)}%",
    help=f"{angka(jumlah_acc)} servis ACC dari {angka(total_servis)} servis."
)
kpi_row_1[2].metric(
    "Rata-rata Durasi ACC",
    f"{angka(avg_duration, 1)} menit" if pd.notna(avg_duration) else "—",
    help="Rata-rata durasi hanya dihitung pada servis ACC yang memiliki durasi aktual."
)

kpi_row_2 = st.columns(3)
kpi_row_2[0].metric(
    "MAPE Estimasi Waktu",
    f"{angka(mape, 2)}%" if pd.notna(mape) else "—",
    help="Mean Absolute Percentage Error pada servis ACC dengan durasi dan estimasi valid."
)
kpi_row_2[1].metric(
    "Item Stok Kritis",
    f"{critical_count} / {inventory_count} item",
    help="Snapshot inventori: stok akhir <= stok minimum. Tidak terpengaruh filter servis."
)
kpi_row_2[2].metric(
    "Total Biaya Sparepart",
    rupiah(total_cost),
    help="Jumlah biaya sparepart yang terhubung dengan servis sesuai filter."
)

st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)


# ============================================================
# NAVIGASI HALAMAN (TABS GARIS BAWAH MERAH)
# ============================================================

tab1, tab2, tab3 = st.tabs([
    "Ringkasan & Insight",
    "Analisis Operasional",
    "Inventori & Keputusan",
])


# ============================================================
# HALAMAN 1: RINGKASAN DAN INSIGHT
# ============================================================

with tab1:
    st.markdown("#### Gambaran Aktivitas Bengkel")

    if filtered.empty:
        st.info("Tidak ada servis yang sesuai dengan filter saat ini. Ubah filter pada sidebar.")
    else:
        col_a, col_b = st.columns([1.5, 1])

        with col_a:
            monthly = (
                filtered.assign(
                    bulan=filtered["tanggal_servis"].dt.to_period("M").astype(str)
                )
                .groupby("bulan", as_index=False)
                .agg(total_servis=("id_servis", "count"))
                .sort_values("bulan")
            )

            fig_month = px.line(
                monthly,
                x="bulan",
                y="total_servis",
                markers=True,
                text="total_servis",
                title="Tren Jumlah Servis per Bulan",
                labels={
                    "bulan": "Bulan",
                    "total_servis": "Jumlah Servis",
                },
            )
            fig_month.update_traces(
                line=dict(color=MAS_RED, width=3),
                marker=dict(size=8, color=MAS_RED_DARK),
                textposition="top center",
                cliponaxis=False,
            )
            y_min = monthly["total_servis"].min()
            y_max = monthly["total_servis"].max()
            fig_month.update_yaxes(range=[max(0, y_min - 4), y_max * 1.12])
            chart_layout(fig_month, 360)
            st.plotly_chart(fig_month, use_container_width=True)

        with col_b:
            status_df = (
                filtered["status_acc"]
                .value_counts()
                .rename_axis("status")
                .reset_index(name="jumlah")
            )
            fig_status = px.pie(
                status_df,
                names="status",
                values="jumlah",
                hole=0.62,
                title="Komposisi Persetujuan Servis (ACC)",
                color="status",
                color_discrete_map={
                    "ACC": DARK,
                    "Tidak ACC": "#FCA5A5",
                },
            )
            fig_status.update_traces(
                textposition="inside",
                textinfo="percent+label",
            )
            chart_layout(fig_status, 360)
            st.plotly_chart(fig_status, use_container_width=True)

        st.markdown("#### Insight Utama")
        insight_cols = st.columns(3)

        cat_duration = (
            filtered_acc.groupby("kategori_kerusakan")
            .agg(
                rata2_durasi=("durasi_pengerjaan_menit", "mean"),
                jumlah=("id_servis", "count"),
            )
            .dropna()
            .sort_values("rata2_durasi", ascending=False)
        )

        with insight_cols[0]:
            if not cat_duration.empty:
                highest = cat_duration.iloc[0]
                lowest = cat_duration.iloc[-1]
                highest_name = cat_duration.index[0]
                lowest_name = cat_duration.index[-1]
                insight_card(
                    "Durasi Pekerjaan",
                    f"{highest_name}: {angka(highest['rata2_durasi'], 1)} menit",
                    f"Rata-rata durasi tertinggi pada filter terpilih. "
                    f"Terendah adalah {lowest_name} ({angka(lowest['rata2_durasi'], 1)} menit). "
                    "Gunakan kategori pekerjaan sebagai acuan estimasi."
                )
            else:
                insight_card(
                    "Durasi Pekerjaan",
                    "Belum tersedia",
                    "Tidak ada servis ACC berdurasi valid pada filter terpilih."
                )

        with insight_cols[1]:
            tidak_acc = total_servis - jumlah_acc
            insight_card(
                "Persetujuan Servis",
                f"ACC Rate {angka(acc_rate, 1)}%",
                f"{angka(jumlah_acc)} dari {angka(total_servis)} servis berstatus ACC; "
                f"{angka(tidak_acc)} servis tidak ACC pada filter terpilih."
            )

        with insight_cols[2]:
            if not critical_inventory.empty:
                first_critical = critical_inventory.iloc[0]
                gap = abs(float(first_critical["selisih_stok"]))
                insight_card(
                    "Prioritas Inventori",
                    f"{critical_count} dari {inventory_count} item kritis",
                    f"Kekurangan terbesar pada {first_critical['nama_sparepart']}: "
                    f"stok akhir {angka(first_critical['stok_akhir'])}, minimum "
                    f"{angka(first_critical['stok_minimum'])}, selisih {angka(gap)} unit."
                )
            else:
                insight_card(
                    "Prioritas Inventori",
                    "Tidak ada item kritis",
                    "Seluruh stok akhir berada di atas stok minimum pada snapshot inventori."
                )

        if not monthly.empty:
            busiest = monthly.loc[monthly["total_servis"].idxmax()]
            quietest = monthly.loc[monthly["total_servis"].idxmin()]
            render_callout(
                "info",
                f'<b>Aktivitas Bulanan:</b> Bulan tersibuk adalah <b>{busiest["bulan"]}</b> '
                f'({angka(busiest["total_servis"])} servis), sedangkan terendah '
                f'<b>{quietest["bulan"]}</b> ({angka(quietest["total_servis"])} servis).'
            )

    st.markdown("#### Rekomendasi Keputusan")
    rec1, rec2, rec3 = st.columns(3)

    with rec1:
        names = (
            ", ".join(critical_inventory["nama_sparepart"].head(3).astype(str).tolist())
            if not critical_inventory.empty
            else "Tidak ada item kritis saat ini"
        )
        rec1_html = (
            f'<div class="rec-card">'
            f'<span class="rec-number">1. Prioritas Stok Kritis</span>'
            f'<p style="font-size:0.88rem; color:{DARK}; margin-bottom:6px;">'
            f'<b>Pelaksana:</b> Admin gudang &amp; owner. Verifikasi kebutuhan dan <i>lead time</i> pemasok untuk: <b>{names}</b>.'
            f'</p>'
            f'<p style="font-size:0.85rem; color:#6B7280; margin:0;">'
            f'<b>Target uji:</b> Item kritis turun dari {critical_count} menjadi 0 dalam satu bulan setelah verifikasi.'
            f'</p></div>'
        )
        st.markdown(rec1_html, unsafe_allow_html=True)

    with rec2:
        rec2_html = (
            f'<div class="rec-card">'
            f'<span class="rec-number">2. Perbaikan Estimasi Servis</span>'
            f'<p style="font-size:0.88rem; color:{DARK}; margin-bottom:6px;">'
            f'<b>Pelaksana:</b> Admin bengkel. Gunakan kategori pekerjaan dan tingkat keparahan sebagai masukan estimasi awal.'
            f'</p>'
            f'<p style="font-size:0.85rem; color:#6B7280; margin:0;">'
            f'<b>Ukuran keberhasilan:</b> Evaluasi MAPE pada transaksi aktual; target uji MAPE &lt; 10%.'
            f'</p></div>'
        )
        st.markdown(rec2_html, unsafe_allow_html=True)

    with rec3:
        rec3_html = (
            f'<div class="rec-card">'
            f'<span class="rec-number">3. Validasi Transaksi Aktual</span>'
            f'<p style="font-size:0.88rem; color:{DARK}; margin-bottom:6px;">'
            f'<b>Pelaksana:</b> Owner &amp; tim administrasi. Kumpulkan transaksi aktual untuk menguji ulang pola statistik.'
            f'</p>'
            f'<p style="font-size:0.85rem; color:#6B7280; margin:0;">'
            f'<b>Ukuran keberhasilan:</b> Tersedia minimal tiga bulan data aktual dari sistem web yang siap divalidasi.'
            f'</p></div>'
        )
        st.markdown(rec3_html, unsafe_allow_html=True)


# ============================================================
# HALAMAN 2: ANALISIS OPERASIONAL
# ============================================================

with tab2:
    st.markdown("#### Analisis Durasi dan Aktivitas Servis")

    if filtered.empty:
        st.info("Tidak ada data operasional pada filter terpilih.")
    else:
        op_left, op_right = st.columns(2)

        with op_left:
            category_duration = (
                filtered_acc.groupby("kategori_kerusakan", as_index=False)
                .agg(
                    rata2_durasi=("durasi_pengerjaan_menit", "mean"),
                    jumlah_servis=("id_servis", "count"),
                )
                .sort_values("rata2_durasi", ascending=True)
            )

            if not category_duration.empty:
                fig_category = px.bar(
                    category_duration,
                    x="rata2_durasi",
                    y="kategori_kerusakan",
                    orientation="h",
                    text="rata2_durasi",
                    title="Rata-rata Durasi per Kategori Kerusakan",
                    labels={
                        "rata2_durasi": "Durasi Rata-rata (menit)",
                        "kategori_kerusakan": "Kategori Kerusakan",
                    },
                    hover_data={"jumlah_servis": True},
                    color="rata2_durasi",
                    color_continuous_scale=["#FCA5A5", MAS_RED, "#7F1D1D"],
                )
                fig_category.update_traces(
                    texttemplate="%{x:.1f}",
                    textposition="outside",
                )
                fig_category.update_traces(
                    texttemplate="%{x:.1f}",
                    textposition="outside",
                    cliponaxis=False,
                )
                fig_category.update_xaxes(range=[0, category_duration["rata2_durasi"].max() * 1.18])
                fig_category.update_coloraxes(showscale=False)
                chart_layout(fig_category, 430)
                st.plotly_chart(fig_category, use_container_width=True)
            else:
                st.info("Belum tersedia durasi ACC untuk grafik kategori.")

        with op_right:
            severity_order_local = ["Ringan", "Sedang", "Berat"]
            severity_duration = (
                filtered_acc.groupby("tingkat_keparahan", as_index=False)
                .agg(
                    rata2_durasi=("durasi_pengerjaan_menit", "mean"),
                    jumlah_servis=("id_servis", "count"),
                )
            )
            severity_duration["urutan"] = severity_duration["tingkat_keparahan"].map(
                {name: i for i, name in enumerate(severity_order_local)}
            )
            severity_duration = severity_duration.sort_values("urutan")

            if not severity_duration.empty:
                fig_severity = px.bar(
                    severity_duration,
                    x="tingkat_keparahan",
                    y="rata2_durasi",
                    text="rata2_durasi",
                    title="Rata-rata Durasi per Tingkat Keparahan",
                    labels={
                        "tingkat_keparahan": "Tingkat Keparahan",
                        "rata2_durasi": "Durasi Rata-rata (menit)",
                    },
                    hover_data={"jumlah_servis": True},
                    color="tingkat_keparahan",
                    color_discrete_map={
                        "Ringan": "#9CA3AF",
                        "Sedang": "#F87171",
                        "Berat": MAS_RED_DARK,
                    },
                )
                fig_severity.update_traces(
                    texttemplate="%{y:.1f}",
                    textposition="outside",
                    cliponaxis=False,
                )
                fig_severity.update_yaxes(range=[0, severity_duration["rata2_durasi"].max() * 1.15])
                fig_severity.update_layout(showlegend=False)
                chart_layout(fig_severity, 430)
                st.plotly_chart(fig_severity, use_container_width=True)
            else:
                st.info("Belum tersedia durasi ACC untuk grafik keparahan.")

        st.markdown("#### Tren Biaya dan Penggunaan Sparepart")
        usage_by_month = (
            filtered_usage.assign(
                bulan=filtered_usage["tanggal_servis"].dt.to_period("M").astype(str)
            )
            .groupby("bulan", as_index=False)
            .agg(
                total_biaya=("total_biaya_sparepart", "sum"),
                total_penggunaan=("jumlah", "sum"),
            )
            .sort_values("bulan")
        )

        if not usage_by_month.empty:
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                cost_fig = px.bar(
                    usage_by_month,
                    x="bulan",
                    y="total_biaya",
                    title="Total Biaya Sparepart per Bulan",
                    labels={
                        "bulan": "Bulan",
                        "total_biaya": "Biaya Sparepart (Rp)",
                    },
                    text_auto=".3s",
                )
                cost_fig.update_traces(marker_color=MAS_RED)
                chart_layout(cost_fig, 380)
                st.plotly_chart(cost_fig, use_container_width=True)

            with col_u2:
                top_parts = (
                    filtered_usage.groupby("nama_sparepart", as_index=False)
                    .agg(total_penggunaan=("jumlah", "sum"))
                    .nlargest(10, "total_penggunaan")
                    .sort_values("total_penggunaan", ascending=True)
                )

                if not top_parts.empty:
                    parts_fig = px.bar(
                        top_parts,
                        x="total_penggunaan",
                        y="nama_sparepart",
                        orientation="h",
                        text="total_penggunaan",
                        title="Top 10 Sparepart Paling Sering Digunakan",
                        labels={
                            "total_penggunaan": "Total Penggunaan (unit)",
                            "nama_sparepart": "Nama Sparepart",
                        },
                    )
                    parts_fig.update_traces(
                        marker_color=DARK,
                        texttemplate="%{x:.0f}",
                        textposition="outside",
                        cliponaxis=False,
                    )
                    parts_fig.update_xaxes(
                        range=[0, top_parts["total_penggunaan"].max() * 1.18]
                    )
                    parts_fig.update_yaxes(automargin=True)
                    chart_layout(parts_fig, 380)
                    st.plotly_chart(parts_fig, use_container_width=True)
        else:
            st.info("Tidak ada catatan penggunaan sparepart pada periode terpilih.")

        st.markdown("#### Ringkasan Tabel per Kategori Kerusakan")
        if not category_duration.empty:
            st.dataframe(
                category_duration.drop(columns=["urutan"], errors="ignore"),
                hide_index=True,
                use_container_width=True,
                column_config={
                    "kategori_kerusakan": st.column_config.TextColumn("Kategori Pekerjaan/Kerusakan"),
                    "rata2_durasi": st.column_config.NumberColumn("Rata-rata Durasi (menit)", format="%.2f"),
                    "jumlah_servis": st.column_config.NumberColumn("Jumlah Servis", format="%d"),
                },
            )


# ============================================================
# HALAMAN 3: INVENTORI DAN KEPUTUSAN
# ============================================================

with tab3:
    st.markdown("#### Monitoring Inventori Sparepart")
    st.caption(
        "Data inventori merupakan snapshot akhir periode. "
        "Status kritis didefinisikan sebagai stok akhir <= stok minimum."
    )

    inv_a, inv_b, inv_c = st.columns(3)
    inv_a.metric("Total Item Terdaftar", f"{angka(inventory_count)} item")
    inv_b.metric("Item Stok Kritis", f"{angka(critical_count)} item")
    critical_pct = (critical_count / inventory_count * 100) if inventory_count else 0
    inv_c.metric("Proporsi Item Kritis", f"{angka(critical_pct, 1)}%")

    if not critical_inventory.empty:
        st.markdown("##### Daftar Item Kritis yang Perlu Diverifikasi")
        table = critical_inventory[
            [
                "kode_sparepart",
                "nama_sparepart",
                "stok_akhir",
                "stok_minimum",
                "selisih_stok",
            ]
        ].rename(
            columns={
                "kode_sparepart": "Kode",
                "nama_sparepart": "Nama Sparepart",
                "stok_akhir": "Stok Akhir",
                "stok_minimum": "Stok Minimum",
                "selisih_stok": "Selisih",
            }
        )
        st.dataframe(
            table,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Stok Akhir": st.column_config.NumberColumn(format="%d unit"),
                "Stok Minimum": st.column_config.NumberColumn(format="%d unit"),
                "Selisih": st.column_config.NumberColumn(format="%d unit"),
            },
        )

        fig_stock = px.bar(
            critical_inventory.sort_values("selisih_stok"),
            x="selisih_stok",
            y="nama_sparepart",
            orientation="h",
            text="selisih_stok",
            title="Kesenjangan Stok Akhir terhadap Batas Minimum",
            labels={
                "selisih_stok": "Stok Akhir - Stok Minimum (unit)",
                "nama_sparepart": "Nama Sparepart",
            },
        )
        fig_stock.update_traces(
            marker_color=MAS_RED,
            texttemplate="%{x:.0f}",
            textposition="outside",
        )
        chart_layout(fig_stock, 380)
        st.plotly_chart(fig_stock, use_container_width=True)
    else:
        st.success("Tidak ada item dengan stok akhir di bawah atau sama dengan stok minimum.")

    st.markdown("##### Seluruh Data Inventori")
    all_inventory = inventory[
        [
            "kode_sparepart",
            "nama_sparepart",
            "kategori_sparepart",
            "stok_awal",
            "stok_masuk",
            "stok_keluar",
            "stok_akhir",
            "stok_minimum",
            "selisih_stok",
            "kritis",
        ]
    ].copy()

    st.dataframe(
        all_inventory.sort_values(["kritis", "selisih_stok"], ascending=[False, True]),
        hide_index=True,
        use_container_width=True,
        column_config={
            "kode_sparepart": st.column_config.TextColumn("Kode"),
            "nama_sparepart": st.column_config.TextColumn("Nama Sparepart"),
            "kategori_sparepart": st.column_config.TextColumn("Kategori"),
            "stok_awal": st.column_config.NumberColumn("Stok Awal", format="%d"),
            "stok_masuk": st.column_config.NumberColumn("Stok Masuk", format="%d"),
            "stok_keluar": st.column_config.NumberColumn("Stok Keluar", format="%d"),
            "stok_akhir": st.column_config.NumberColumn("Stok Akhir", format="%d"),
            "stok_minimum": st.column_config.NumberColumn("Stok Minimum", format="%d"),
            "selisih_stok": st.column_config.NumberColumn("Selisih Stok", format="%d"),
            "kritis": st.column_config.CheckboxColumn("Kritis"),
        },
    )

    if not critical_inventory.empty:
        priority_item = critical_inventory.iloc[0]
        render_callout(
            "inventory",
            f'<b>Prioritas Verifikasi:</b> <b>{priority_item["nama_sparepart"]}</b> '
            f'({priority_item["kode_sparepart"]}) memiliki stok akhir '
            f'{angka(priority_item["stok_akhir"])} unit, sedangkan stok minimum '
            f'{angka(priority_item["stok_minimum"])} unit (kekurangan {angka(abs(priority_item["selisih_stok"]))} unit). '
            f'Admin gudang dan owner perlu memeriksa kebutuhan aktual serta <i>lead time</i> pemasok.'
        )

    st.download_button(
        "Unduh Tabel Inventori (.CSV)",
        data=inventory.to_csv(index=False).encode("utf-8-sig"),
        file_name="inventori_dashboard.csv",
        mime="text/csv",
    )


# ============================================================
# DOWNLOAD DATA TERFILTER DAN FOOTER
# ============================================================

st.divider()
download_col1, download_col2 = st.columns(2)

with download_col1:
    st.download_button(
        "Unduh Data Servis Terfilter (.CSV)",
        data=filtered.to_csv(index=False).encode("utf-8-sig"),
        file_name="servis_terfilter.csv",
        mime="text/csv",
        disabled=filtered.empty,
    )

with download_col2:
    st.download_button(
        "Unduh Penggunaan Sparepart Terfilter (.CSV)",
        data=filtered_usage.to_csv(index=False).encode("utf-8-sig"),
        file_name="penggunaan_sparepart_terfilter.csv",
        mime="text/csv",
        disabled=filtered_usage.empty,
    )

st.caption(
    "Copyright © 2026 CV. Manyar Auto Service. All rights reserved."
)