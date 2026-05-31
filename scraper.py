from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import time
import os

def get_card_prices():
    url = "https://cardrush.media/pokemon/buying_prices"
    
    with sync_playwright() as p:
        # 1. ユーザーエージェントを普通のWindowsブラウザに偽装
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        # 2. ブラウザの起動設定
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        
        # 3. 偽装情報を含んだコンテキストを作成
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()
        
        print(f"アクセス中: {url}")
        # タイムアウトを少し長めに設定してページ遷移
        page.goto(url, wait_until="networkidle", timeout=60000)
        
        # 4. 表（table）が表示されるまで待機（タイムアウトを30秒に延長）
        print("表の読み込みを待機中...")
        try:
            page.wait_for_selector("table", timeout=30000)
        except Exception as e:
            print(f"エラー: 表が見つかりませんでした。タイムアウトしました。")
            browser.close()
            return pd.DataFrame()

        time.sleep(3) # 読み込み完了後の安定化時間を少し追加
        
        cards = []
        
        # 全ての「行(tr)」を取得
        rows = page.query_selector_all("tr")
        print(f"解析中... {len(rows)}件の行が見つかりました。")

        for row in rows:
            cols = row.query_selector_all("td")
            # 1列目が名前、5列目（インデックス4）が買取価格
            if len(cols) >= 5:
                name = cols[0].inner_text().strip()
                price_raw = cols[4].inner_text().strip()
                
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
        print(df.head(10)) 
        
        filename = "price_history.csv"
        # CSV保存処理（追記モード）
        if not os.path.isfile(filename):
            df.to_csv(filename, index=False, encoding='utf-8-sig')
        else:
            df.to_csv(filename, mode='a', header=False, index=False, encoding='utf-8-sig')
        
        print(f"\n{filename} にデータを蓄積しました。")
    else:
        print("データが取得できませんでした。サイト側の制限か、構造が変わった可能性があります。")