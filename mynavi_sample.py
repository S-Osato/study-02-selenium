import os
import warnings
warnings.simplefilter('ignore', FutureWarning)
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import datetime

# Selenium4対応済


def set_driver(hidden_chrome: bool=False):
    '''
    Chromeを自動操作するためのChromeDriverを起動してobjectを取得する
    '''
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if hidden_chrome:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(f'--user-agent={USER_AGENT}') # ブラウザの種類を特定するための文字列
    options.add_argument('log-level=3') # 不要なログを非表示にする
    options.add_argument('--ignore-certificate-errors') # 不要なログを非表示にする
    options.add_argument('--ignore-ssl-errors') # 不要なログを非表示にする
    options.add_experimental_option('excludeSwitches', ['enable-logging']) # 不要なログを非表示にする
    options.add_argument('--incognito') # シークレットモードの設定を付与
    
    # ChromeのWebDriverオブジェクトを作成する。
    service=Service(ChromeDriverManager().install())
    return Chrome(service=service, options=options)


def get_timestamp():
    dt_now = datetime.datetime.now()
    return dt_now.strftime('%Y年%m月%d日 %H:%M:%S') + " "

def main():
    '''
    main処理
    '''
    
    path = 'log.txt'
    with open(path, mode='a') as f:
    
        search_keyword = input("検索キーワードを入力してください >>> ")
        # driverを起動
        driver = set_driver()
        
        # Webサイトを開く
        driver.get("https://tenshoku.mynavi.jp/")
        time.sleep(5)
        
        f.write(get_timestamp() + search_keyword + "で検索します。\n")
        
        
        '''
        ポップアップを閉じる
        ※余計なポップアップが操作の邪魔になる場合がある
        モーダルのようなポップアップ画面は、通常のclick操作では処理できない場合があるため
        excute_scriptで直接Javascriptを実行することで対処する
        '''
        try:
            # ポップアップを閉じる（seleniumだけではクローズできない）
            driver.execute_script('document.querySelector(".karte-close").click()')
            time.sleep(5)
            # ポップアップを閉じる
            driver.execute_script('document.querySelector(".karte-close").click()')
        except:
            pass


        '''
        find_elementでHTML要素(WebElement)を取得する
        byで、要素を特定する属性を指定するBy.CLASS_NAMEの他、By.NAME、By.ID、By.CSS_SELECTORなどがある
        特定した要素に対して、send_keysで入力、clickでクリック、textでデータ取得が可能
        '''
        # 検索窓に入力
        driver.find_element(by=By.CLASS_NAME, value="topSearch__text").send_keys(search_keyword)
        # 検索ボタンクリック
        driver.find_element(by=By.CLASS_NAME, value="topSearch__button").click()

        # 空のDataFrame作成
        df = pd.DataFrame()
        while True:
            '''
            find_elements(※複数形)を使用すると複数のデータがListで取得できる
            一覧から同一条件で複数のデータを取得する場合は、こちらを使用する
            '''
            name_elms = driver.find_elements(by=By.CLASS_NAME, value="cassetteRecruit__name")
            title_elms = driver.find_elements(by=By.CLASS_NAME, value="cassetteRecruit__copy")
            
            

            # 1ページ分繰り返し
            print(len(name_elms))
            '''
            name_elmsには１ページ分の情報が格納されているのでforでループさせて１つづつ取り出して、Dataframeに格納する
            '''
            
            for name_elm, title_elm in zip(name_elms, title_elms):
                print(name_elm.text)
                print(title_elm.text)
                # DataFrameに対して辞書形式でデータを追加する
                df = df.append(
                    {"会社名": name_elm.text, 
                    "求人タイトル": title_elm.text}, 
                    ignore_index=True)
                
            log_text = get_timestamp() + str(len(df.index)) + "件取得しました。\n"
            f.write(log_text)
            print("------------------------------------------------")
            try:
                driver.find_element(by=By.CLASS_NAME, value="iconFont--arrowLeft").click()
                time.sleep(5)
            except:
                f.write(get_timestamp() + '取得が完了しました。')
                break

        df.to_csv("output.csv")
    f.close()

# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
