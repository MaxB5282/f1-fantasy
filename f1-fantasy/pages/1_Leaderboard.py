import streamlit as st
import pandas as pd
from pathlib import Path
from utils.database import get_supabase, get_leaderboard

st.set_page_config(
    page_title="Leaderboard | Max's F1 League",
    page_icon="🏆",
    layout="wide",
)

st.title("🏆 Leaderboard")

# Mobile-friendly CSS: cap image heights so tall portrait photos don't dominate
st.markdown("""
<style>
/* Cap player card images */
[data-testid="stImage"] img {
    max-height: 160px;
    width: 100%;
    object-fit: cover;
    object-position: top;
    border-radius: 8px;
}
/* Shrink driver thumbnail images */
.driver-thumb img {
    max-height: 60px !important;
}
@media (max-width: 768px) {
    [data-testid="stImage"] img {
        max-height: 90px;
    }
}
</style>
""", unsafe_allow_html=True)


def get_image(folder, name):
    """Return EXIF-corrected image bytes, or None if not found."""
    import unicodedata, io
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
            return buf.getvalue()
    return None


supabase = get_supabase()
player_totals, player_breakdown, adj_log = get_leaderboard(supabase)

if not player_totals:
    st.info("No data yet. Set up teams in Admin, then enter some race results.")
    st.stop()

sorted_players = sorted(player_totals.items(), key=lambda x: -x[1]["total"])

# ── Player cards ──────────────────────────────────────────────────────────────
cols = st.columns(len(sorted_players))
medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

for i, (pid, p) in enumerate(sorted_players):
    with cols[i]:
        img = get_image("players", p["name"])
        if img:
            st.image(img, use_container_width=True)
        st.markdown(f"### {medals[i]} {p['name']}")
        st.metric("Points", p["total"])

st.divider()

# ── Driver breakdown ──────────────────────────────────────────────────────────
st.subheader("Driver Breakdown")

for pid, p in sorted_players:
    with st.expander(f"{p['name']}  —  {p['total']} pts"):
        for d in sorted(player_breakdown[pid], key=lambda x: -x["Total Pts"]):
            dcols = st.columns([1, 4, 3])
            img = get_image("drivers", d["Driver"])
            if img:
                dcols[0].image(img, width=50)
            else:
                dcols[0].write("")
            label = f"**{d['Driver']}**"
            if d["Round"] == 4:
                label += "  ✦ 3×"
            dcols[1].markdown(label)
            dcols[1].caption(f"Round {d['Round']} pick · {d['Base Pts']} base pts")
            dcols[2].metric("Points", d["Total Pts"])
        # Show waiver penalties if any
        if pid in adj_log:
            st.markdown("**Adjustments**")
            for adj in adj_log[pid]:
                st.caption(f"{adj['reason']}: **{adj['amount']:+d} pts**")
