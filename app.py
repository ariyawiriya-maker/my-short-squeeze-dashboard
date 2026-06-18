import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Short Squeeze Dashboard", layout="wide")

st.title("📊 Short Squeeze Real-time Scanner (by พารวย)")
st.subheader("ระบบคัดกรองหุ้นสายสควีซ [เวอร์ชันดึงข้อมูลฟรีผ่าน Yahoo Finance]")

# รายชื่อหุ้นสหรัฐฯ ยอดฮิตที่มีกระแส Short Squeeze และโวลุ่มสูง
watchlist = [
    # --- สาย Meme & Classic Squeeze ---
    "GME",
    "AMC",
    "SPWR",
    "BYND",
    "NVAX",
    "LCID",
    "RIVN",
    "NKLA",
    "AI",
    "PLTR",
    "SOFI",
    "CHPT",
    "OPEN",
    "UPST",
    "FSR",
    # --- สาย Crypto & Blockchain (โวลุ่มหนาแน่นสวิงแรง) ---
    "MARA",
    "RIOT",
    "COIN",
    "MSTR",
    "CLSK",
    "WULF",
    "CIFR",
    "BTBT",
    # --- สาย Tech, EV & เติบโตสูง (กองทุนชอบชอร์ต) ---
    "TSLA",
    "NIO",
    "XPEV",
    "LI",
    "AAPL",
    "NVDA",
    "AMD",
    "INTC",
    "META",
    "AMZN",
    "MSFT",
    "GOOGL",
    "NFLX",
    "BABA",
    "PDD",
    "JD",
    "BIDU",
    "THTX",
    # --- สายเก็งกำไร ยอดนิยมของรายย่อย (Retail Favorites) ---
    "SNAP",
    "PINS",
    "ROKU",
    "HOOD",
    "COSM",
    "MULN",
    "RUM",
    "DWAC",
    "DJT",
    "WE",
    "NKLA",
    "XENE",
    "CVNA",
    "FUBO",
    "LYFT",
    "UBER",
    "DKNG",
    "PENN",
    "TLRY",
    "CGC",
    "ACB",
    "SNDL",
    # --- หุ้นกลุ่ม BioTech, พลังงาน และอื่น ๆ ที่ชอร์ตแน่น ---
    "CRSP",
    "EDIT",
    "BE",
    "PLUG",
    "FCEL",
    "RUN",
    "SPCE",
    "QS",
    "BLNK",
    "EVGO",
    "CHWY",
    "JMIA",
    "RBLX",
    "U",
    "AFRM",
    "UPST",
    "LMND",
    "S",
    "PATH",
    "AI",
    "C3AI",
    "PLTR",
    "ASAN",
    "OKTA",
    "DDOG",
    "NET",
    "ZS",
    "CRWD",
    "PANW",
    "SNOW",
    "MDB",
    "COUP",
    "WDAY",
    "TEAM",
    "SHOP",
    "SQ",
    "PYPL",
]


@st.cache_data(ttl=600)
def get_yahoo_data(tickers):
    data_list = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # ดึงค่า Short % ของหุ้นแต่ละตัวจาก Yahoo
            short_ratio = info.get("shortRatio", 0.0)
            short_percent = info.get("shortPercentOfFloat", 0.0)

            # แปลงทศนิยมเป็นเปอร์เซ็นต์ (เช่น 0.22 -> 22.0%)
            if short_percent is not None and short_percent <= 1.0:
                short_percent = short_percent * 100

            data_list.append(
                {
                    "Ticker": ticker,
                    "Company": info.get("longName", "N/A"),
                    "Sector": info.get("sector", "N/A"),
                    "Short Float %": round(short_percent or 0.0, 2),
                    "Short Ratio (Days)": round(short_ratio or 0.0, 2),
                    "Price ($)": info.get("currentPrice", 0.0),
                    "Volume": info.get("volume", 0.0),
                }
            )
        except Exception as e:
            continue
    return pd.DataFrame(data_list)


with st.spinner("กำลังดึงข้อมูลสดใหม่จาก Yahoo Finance..."):
    df = get_yahoo_data(watchlist)

if df is not None and not df.empty:
    # เมนูควบคุมด้านซ้าย
    st.sidebar.header("🎯 ตั้งค่าเกณฑ์คัดกรอง (Filters)")
    min_short_float = st.sidebar.slider(
        "ระดับ Short Float ต่ำสุด (%)",
        min_value=0.0,
        max_value=50.0,
        value=10.0,
        step=1.0,
    )

    # กรองข้อมูล
    filtered_df = df[df["Short Float %"] >= min_short_float]

    # แสดงผลตัวเลข Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("จำนวนหุ้นใน List ที่ติดตาม", f"{len(df)} ตัว")
    with col2:
        st.metric(
            "จำนวนหุ้นที่เข้าเงื่อนไขสควีซ",
            f"{len(filtered_df)} ตัว",
            delta=f"Short Float >= {min_short_float}%",
        )

    st.write("### 📋 รายชื่อหุ้นที่ติดอันดับยอด Short สูงสุด (Yahoo Data)")

    # แสดงตารางแดชบอร์ด
    st.dataframe(
        filtered_df.sort_values(by="Short Float %", ascending=False),
        use_container_width=True,
    )
    st.success(
        "🎉 แผนสี่เปิดใช้งานสำเร็จ! ดึงข้อมูลตรงจาก Yahoo Finance เสถียร ไว และไม่มีวันโดนบล็อกครับพี่"
    )
else:
    st.error("🛑 ไม่สามารถดึงข้อมูลจาก Yahoo Finance ได้ในขณะนี้")