from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import time
import os

def get_card_prices():
    url = "https://cardrush.media/pokemon/buying_prices"
    
    with sync_playwright() as p:
        # headless=Trueで画面を出さずに実行（デバッグ時はFalseにすると動きが見えます）
        # scraper.py の一部を修正
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        
        print(f"アクセス中: {url}")
        page.goto(url)
        
        # 表（table）が表示されるまで待機
        print("表の読み込みを待機中...")
        page.wait_for_selector("table", timeout=15000)
        time.sleep(2) # 念のための追加待機
        
        cards = []
        
        # 全ての「行(tr)」を取得
        rows = page.query_selector_all("tr")
        print(f"解析中... {len(rows)}件の行が見つかりました。")

        for row in rows:
            cols = row.query_selector_all("td")
            # 画像を見ると、1列目が名前、5列目あたりが買取価格になっています
            if len(cols) >= 5:
                name = cols[0].inner_text().strip()
                price_raw = cols[4].inner_text().strip() # 5番目の列
                
                # 数字だけを抽出
                price_text = "".join(filter(str.isdigit, price_raw))
                
                if name and price_text:
                    cards.append({
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'card_name': name,
                        'price': int(price_text)
                    })
        
        browser.close()
        return pd.DataFrame(cards)

if __name__ == "__main__":
    df = get_card_prices()
    if not df.empty:
        print(f"【大成功】 {len(df)}件のデータを取得しました！")
        print(df.head(10)) # 最初の10件を表示
        filename = "price_history.csv"
        if not os.path.isfile(filename):
            df.to_csv(filename, index=False, encoding='utf-8-sig')
        else:
            df.to_csv(filename, mode='a', header=False, index=False, encoding='utf-8-sig')
        print("\nprice_history.csv に保存しました。")
    else:
        print("データが取得できませんでした。列の番号が違う可能性があります。")