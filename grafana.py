import requests
# from flask import Flask, jsonify
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from datetime import date
# import pandas as pd

# app = Flask(__name__)

# Bước 1: Lấy cookie từ trang trung gian
def get_cookie_from_html():
    url = "https://quanlymangagg.vn/api_cts/get_cookie.php"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    cookie_div = soup.find("div", class_="cookie-text")
    if cookie_div:
        return cookie_div.text.strip()
    return None


# Bước 2: Gọi API CTS với cookie vừa lấy
def fetch_bsc_report(cookie):
    url = "https://cts.vnpt.vn/Report/Reportclm/GetBscReport"
    params = {
        "provinceCode": "GRP",
        "year": "2025",
        "quater": "7"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Referer": "https://cts.vnpt.vn/Report/BSCReport",
        "Cookie": cookie,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json() if response.status_code == 200 else response.text

cols = ['PROVINCE_CODE', 'PROVINCE_NAME', 'FBB_QOS_T1','MBB_QOS_T1','MYTV_QOS_T1','FBB_QOE_T1','MBB_QOE_T1','MYTV_QOE_T1','KPI_QOS_T1','KPI_QOE_T1','KPI_CL_HT_VT_T1']
# Chạy
cookie = get_cookie_from_html()
result = fetch_bsc_report(cookie)
df = pd.DataFrame(result)
df2 = df[cols]
df2 = df2[2:].copy()

def compu_rank(col):
    df2[f'RANK_{col}'] = (
        df2[col]
        .rank(method='min', ascending=False, na_option='bottom')
        .astype(int)
    )

for col in cols[2:].copy():
    compu_rank(col)
# df2['RANK_FBB_QOS_T1'] = (
#     df2['FBB_QOS_T1']
#     .rank(method='min', ascending=False, na_option='bottom')
#     .astype(int)
# )
print(df2)
def time(df):
    # Tính số ngày cần (mỗi 63 hàng là 1 ngày)
    num_days = len(result) // 63
    today = date.today()

    # Tạo danh sách các ngày
    start_date = pd.Timestamp(today)
    dates = pd.date_range(start=start_date, periods=num_days, freq='D')

    # Lặp lại mỗi ngày 63 lần
    repeated_dates = dates.repeat(63)

    # Nếu df không chia hết cho 63, cần thêm phần còn lại
    if len(df) > len(repeated_dates):
        last_day = dates[-1] + pd.Timedelta(days=1)
        extra = len(df) - len(repeated_dates)
        repeated_dates = repeated_dates.append(pd.Index([last_day] * extra))

    # Gán vào cột 'time'
    df['time'] = repeated_dates.values

    return df

df2 = time(df2)


df2 = df2.iloc[[0]]
print(df2)
df2.to_csv("fbb_qos_all_provinces.csv", index=False, encoding="utf-8-sig")
# @app.route("/api/get-bsc")
# def bsc():
#     try:
#         return jsonify(df2.to_json(orient="split"))
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True)
