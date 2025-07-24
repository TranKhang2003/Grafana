from flask import Flask, jsonify
import pandas as pd
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_TOKEN = "Y3RzLmFnZ0AyMi8wNS8yMDI1IDEwOjI5"
API_URL_TEMPLATE = (
    "https://cts.vnpt.vn:8085/LineTestAPI/GetReportFBBQoS?"
    "provinceCode=GRP&typeDate=2"
    "&fromDate={}&toDate={}&fromDay={}&toDay={}"
)
headers = {"Authorization": API_TOKEN}

def get_fbb_qos_dataframe(from_date: str, to_date: str) -> pd.DataFrame:
    url = API_URL_TEMPLATE.format(from_date, to_date, from_date, to_date)
    
    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            data_list = response.json()  # assuming it's a list of dicts
            df = pd.DataFrame(data_list)
            df2 = df[['PROVINCE_CODE', 'PROVINCE_NAME', 'FBB_QOS_RATIO']]
            df2 = df2[2:].copy()  # loại bỏ 2 dòng đầu
            df2['FBB_QOS_RATIO'] = pd.to_numeric(df2['FBB_QOS_RATIO'], errors='coerce')
            df2['RANK'] = (
                df2['FBB_QOS_RATIO']
                .rank(method='min', ascending=False, na_option='bottom')
                .astype(int)
            )
            return df2
        else:
            print(f"Request failed with status code {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        print("Exception during request or processing:", e)
        return pd.DataFrame()

# Ví dụ: gom dữ liệu từ nhiều ngày
all_dfs = []
for day in ["17/07/2025", "18/07/2025", "19/07/2025"]:
    df_day = get_fbb_qos_dataframe(day, day)
    if not df_day.empty:
        # df_day["TIME"] = day
        all_dfs.append(df_day)

# Gộp tất cả vào một DataFrame
df = pd.concat(all_dfs, ignore_index=True)

@app.route("/get-result", methods=["GET"])
def get_result():
    # df["time"] = pd.to_datetime(df["TIME"], format="%d/%m/%Y").dt.strftime('%Y-%m-%dT%H:%M:%S')
    # result = df[["time", "PROVINCE_CODE", "PROVINCE_NAME", "FBB_QOS_RATIO", "RANK"]]
    return jsonify(df.to_dict(orient="records"))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
