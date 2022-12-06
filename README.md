# vol6-TemperatureSenseForecastMap
## 開発概要
    - 近年では異常気象もあってか，30度以上の気温が当たり前に感じます。
    - 従来より運動をした際の熱中症による健康リスクが増大しています。
    - そこで，現在の熱中症のリスクを客観的に調査できるサービスを作成しました。
## 開発用情報
### セットアップ手順（Docker環境）
1. docker-compose.yml.base を docker-compose.yml にコピーします。
2. 中の"DATABASE_URL" の欄にログインコードを記入します
3. docker 環境を起動します `docker compose up -d`
4. アクセスします `127.0.0.1:8000`

### セットアップ手順（ローカル環境）
1. venv 環境を構築します `python -m venv .venv`
2. 仮想環境を有効化します `.\.venv\Scripts\Activate.bat`
3. 依存ライブラリをインストールします `python -m pip install -r requirements.txt`
4. django を起動します `python manage.py runserver`
5. アクセスします `127.0.0.1:8000`


### 環境変数の設定
1. `.evb.base` ファイルを**コピー**して， `.env`ファイルを作成する
2. `.env`ファイル内のトークンを置き換える

### dbの初期設定
`python manage.py makemigrations`
`python manage.py migrate`
`\COPY app_point_name(name,katakana,address,ido,keido,wbgt_time_json) FROM 'ame_master_202207029.csv' DELIMITER ',' CSV HEADER;`