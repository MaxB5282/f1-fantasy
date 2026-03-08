import streamlit as st
import base64
import io
from pathlib import Path
from utils.database import get_supabase, get_leaderboard

st.set_page_config(
    page_title="Leaderboard | Max's F1 League",
    page_icon="🏆",
    layout="wide",
)

st.title("🏆 Leaderboard")

st.markdown("""
<style>
/* ── Player cards ──────────────────────────────────────── */
.player-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    justify-content: center;
    margin-bottom: 16px;
}
.player-card {
    background: rgba(128,128,128,0.1);
    border-radius: 12px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 14px;
    flex: 1 1 180px;
    max-width: 260px;
    min-width: 150px;
}
.player-card img {
    width: 72px;
    height: 72px;
    object-fit: cover;
    object-position: top;
    border-radius: 50%;
    flex-shrink: 0;
}
.player-img-placeholder {
    width: 72px;
    height: 72px;
    border-radius: 50%;
    background: rgba(128,128,128,0.3);
    flex-shrink: 0;
}
.player-card .medal { font-size: 1.3rem; line-height: 1; }
.player-card .pname {
    font-size: 1rem;
    font-weight: 700;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.player-card .pts {
    font-size: 1.5rem;
    font-weight: 800;
    color: #e10600;
    line-height: 1.1;
}
.player-card .pts-label {
    font-size: 0.68rem;
    opacity: 0.55;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Driver rows ───────────────────────────────────────── */
.driver-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 4px;
    border-bottom: 1px solid rgba(128,128,128,0.15);
}
.driver-row:last-child { border-bottom: none; }
.driver-left {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
    min-width: 0;
}
.driver-left img {
    width: 46px;
    height: 46px;
    object-fit: cover;
    object-position: top;
    border-radius: 50%;
    flex-shrink: 0;
}
.driver-img-placeholder {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    background: rgba(128,128,128,0.3);
    flex-shrink: 0;
}
.driver-name {
    font-weight: 600;
    font-size: 0.95rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.driver-sub {
    font-size: 0.73rem;
    opacity: 0.5;
    margin-top: 1px;
}
.driver-pts {
    font-size: 1.1rem;
    font-weight: 700;
    white-space: nowrap;
    padding-left: 16px;
    flex-shrink: 0;
}
.adj-block {
    margin-top: 10px;
    padding: 8px;
    border-radius: 8px;
    background: rgba(225,6,0,0.08);
    font-size: 0.82rem;
}
.adj-block strong { display: block; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)


def get_image_b64(folder, name):
    """Return base64-encoded JPEG string, or None if not found."""
    import unicodedata
    from PIL import Image, ImageOps
    slug = name.lower().replace(" ", "_")
    slug = unicodedata.normalize("NFD", slug)
    slug = "".join(c for c in slug if unicodedata.category(c) != "Mn")
    app_root = Path(__file__).parent.parent
    base = app_root / "images" / folder
    if not base.exists():
        return None
    valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".jfif"}
    for f in base.iterdir():
        if f.stem.lower() == slug and f.suffix.lower() in valid_exts:
            img = Image.open(f).convert("RGB")
            img = ImageOps.exif_transpose(img)
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            return base64.b64encode(buf.getvalue()).decode()
    return None


supabase = get_supabase()
player_totals, player_breakdown, adj_log = get_leaderboard(supabase)

if not player_totals:
    st.info("No data yet. Set up teams in Admin, then enter some race results.")
    st.stop()

sorted_players = sorted(player_totals.items(), key=lambda x: -x[1]["total"])
medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

# ── Player cards ──────────────────────────────────────────────────────────────
cards_html = '<div class="player-grid">'
for i, (pid, p) in enumerate(sorted_players):
    b64 = get_image_b64("players", p["name"])
    if b64:
        img_html = f'<img src="data:image/jpeg;base64,{b64}" alt="{p["name"]}">'
    else:
        img_html = '<div class="player-img-placeholder"></div>'
    cards_html += f"""
    <div class="player-card">
        {img_html}
        <div>
            <div class="medal">{medals[i]}</div>
            <div class="pname">{p['name']}</div>
            <div class="pts">{p['total']}</div>
            <div class="pts-label">points</div>
        </div>
    </div>"""
cards_html += '</div>'
st.markdown(cards_html, unsafe_allow_html=True)

st.divider()

# ── Driver breakdown ──────────────────────────────────────────────────────────
st.subheader("Driver Breakdown")

for pid, p in sorted_players:
    with st.expander(f"{p['name']}  —  {p['total']} pts"):
        rows_html = '<div>'
        for d in sorted(player_breakdown[pid], key=lambda x: -x["Total Pts"]):
            b64 = get_image_b64("drivers", d["Driver"])
            if b64:
                img_html = f'<img src="data:image/jpeg;base64,{b64}" alt="{d["Driver"]}">'
            else:
                img_html = '<div class="driver-img-placeholder"></div>'
            multiplier_badge = ' <span style="color:#e10600;font-size:0.8em">✦ 3×</span>' if d["Round"] == 4 else ""
            rows_html += f"""
            <div class="driver-row">
                <div class="driver-left">
                    {img_html}
                    <div>
                        <div class="driver-name">{d['Driver']}{multiplier_badge}</div>
                        <div class="driver-sub">Round {d['Round']} pick</div>
                    </div>
                </div>
                <div class="driver-pts">{d['Total Pts']} pts</div>
            </div>"""

        if pid in adj_log:
            rows_html += '<div class="adj-block"><strong>Adjustments</strong>'
            for adj in adj_log[pid]:
                rows_html += f'<div>{adj["reason"]}: <strong>{adj["amount"]:+d} pts</strong></div>'
            rows_html += '</div>'

        rows_html += '</div>'
        st.markdown(rows_html, unsafe_allow_html=True)
