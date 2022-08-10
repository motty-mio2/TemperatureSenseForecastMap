import base64
import json
from io import BytesIO
from urllib import request

import matplotlib
from matplotlib import pyplot as plt

matplotlib.use("Agg")


# プロットしたグラフを画像データとして出力するための関数
def Output_Graph():
    buffer = BytesIO()  # バイナリI/O(画像や音声データを取り扱う際に利用)
    plt.savefig(buffer, format="png")  # png形式の画像データを取り扱う
    buffer.seek(0)  # ストリーム先頭のoffset byteに変更
    img = buffer.getvalue()  # バッファの全内容を含むbytes
    graph = base64.b64encode(img)  # 画像ファイルをbase64でエンコード
    graph = graph.decode("utf-8")  # デコードして文字列から画像に変換
    buffer.close()
    return graph


# グラフをプロットするための関数
def Plot_Graph(time_list: list[str], wgbt_list: list[float]):
    x_num = list(range(0, len(time_list), 1))  # x軸の連番値を作成

    plt.switch_backend("AGG")  # スクリプトを出力させない
    plt.figure(figsize=(10, 5))  # グラフサイズ

    plt.bar(time_list, [min(i, 24) for i in wgbt_list], color="cyan")  # type:ignore

    blue_x: list[str] = []
    blue_y: list[float] = []
    for time, wgbt in zip(time_list, wgbt_list):
        if wgbt >= 24:
            blue_x.append(time)
            blue_y.append(min(wgbt, 28) - 24)
    plt.bar(blue_x, blue_y, color="blue", bottom=24)  # type:ignore

    yellow_x: list[str] = []
    yellow_y: list[float] = []
    for time, wgbt in zip(time_list, wgbt_list):
        if wgbt >= 28:
            yellow_x.append(time)
            yellow_y.append(min(wgbt, 31) - 28)
    plt.bar(yellow_x, yellow_y, color="yellow", bottom=28)  # type:ignore

    orange_x: list[str] = []
    orange_y: list[float] = []
    for time, wgbt in zip(time_list, wgbt_list):
        if wgbt >= 31:
            orange_x.append(time)
            orange_y.append(min(wgbt, 35) - 31)
    plt.bar(orange_x, orange_y, color="orange", bottom=31)  # type:ignore

    red_x: list[str] = []
    red_y: list[float] = []
    for time, wgbt in zip(time_list, wgbt_list):
        if wgbt > 35:
            red_x.append(time)
            red_y.append(wgbt - 35)
    plt.bar(red_x, red_y, color="red", bottom=35)  # type:ignore

    # 横軸を日付にする
    plt.xticks(x_num, time_list)  # type:ignore
    # x軸縦書き（90度回転）
    plt.xticks(rotation=90)  # type:ignore
    plt.title("WGBT-Graph")  # グラフタイトル
    plt.xlabel("Date")  # type:ignore
    plt.ylabel("WGBT")  # type:ignore
    plt.tight_layout()  # レイアウト
    graph = Output_Graph()  # グラフプロット

    return graph


def location2wgbt(ido: float, keido: float) -> tuple[list[float], list[str], str]:
    """WGBT温度の計算
    緯度・経度を用いて，Open-Meteo API(open-meteo.com)から，
        - 温度
        - 湿度
        - 直達日射量
        - 散乱日射量
        - 風速
        を取得します
        これらの値からWGBT温度を計算します
        (https://blog.obniz.com/news/obniz-wbgt-service.html)
    Args:
        - ido (float): 緯度
        - keido (float): 経度
    Returns:
        - wgbts_list list[float]: WGBT温度（24時間分）
        - time_list list[str]: １時間ごとの時間（24時間分）
        - Plot_Graph(time_list, wgbts_list) str: グラフ(x:wgbt, y:時間)
    """

    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={ido}&longitude={keido}"
        "&hourly=temperature_2m,relativehumidity_2m,direct_radiation,diffuse_radiation,"
        "windspeed_10m&current_weather=true&timezone=Asia%2FTokyo"
    )

    wgbts_list: list[float] = []
    time_list: list[str] = []
    year = "2022-"
    str1 = "-"
    str2 = "T"

    with request.urlopen(url) as r:
        body = json.loads(r.read())

        tdate = body["current_weather"]["time"]
        index_now_time = body["hourly"]["time"].index(tdate)

        for index in range(index_now_time, index_now_time + 24):
            time = body["hourly"]["time"][index]

            time = time.replace(year, "")
            time = time.replace(str1, "/")
            time = time.replace(str2, "/")

            time_list.append(time)

            temperature = body["hourly"]["temperature_2m"][index]
            humidity = body["hourly"]["relativehumidity_2m"][index]
            direct_radiation = body["hourly"]["direct_radiation"][index] / 1000
            diffuse_radiation = body["hourly"]["diffuse_radiation"][index] / 1000
            windspeed_10m = abs(body["hourly"]["windspeed_10m"][index] * 1000 / 3600)

            wgbt = (
                0.735 * temperature
                + 0.0374 * humidity
                + 0.00292 * temperature * humidity
                + 7.619 * (direct_radiation + diffuse_radiation)
                - 4.557 * (direct_radiation + diffuse_radiation) ** 2
                - 0.0572 * windspeed_10m
                - 4.064
            )
            wgbts_list.append(round(wgbt, 3))

    # 現在から24時間後の暑さ指数の予測値と時刻が入った配列
    return wgbts_list, time_list, Plot_Graph(time_list, wgbts_list)


def wgbt_indicator(WBGT: float) -> str:
    """WGBT温度による熱中症リスクの診断
    Args:
        WBGT (float): WGBT温度
    Returns:
        message (str): 危険度合のメッセージ
    """
    status: list[str] = [
        "運動は原則中止",
        "厳重警戒（激しい運動は中止）",
        "警戒（積極的に休憩)",
        "注意（積極的に水分補給）",
        "ほぼ安全（適宜水分補給）",
    ]

    if WBGT > 35:
        return status[0]
    elif 35 > WBGT >= 31:
        return status[1]
    elif 31 > WBGT >= 28:
        return status[2]
    elif 28 > WBGT >= 24:
        return status[3]
    else:  # WBGT < 24:
        return status[4]
