import requests
import urllib
import tkinter as tk
import tkinter.filedialog as fd
import os
import webbrowser
import PIL.Image
import PIL.ImageTk
import time
import re
from bs4 import BeautifulSoup
from tkinter import simpledialog,messagebox as tmsg
from pathlib import Path


input_folder = None
cpath = None
img_list = []
filename = None
end = False
countimg =0
window = None
# 新しいウィンドウを開く関数
def open_new_window():
    new_window = tk.Toplevel(root)  # 新しいウィンドウを作成
    new_window.title("新しいウィンドウ")  # タイトルを設定

    # 画面の幅と高さを取得
    screen_width = root.winfo_screenwidth()  # 画面の幅
    screen_height = root.winfo_screenheight()  # 画面の高さ
    
    # ウィンドウの幅を画面の42%、高さを250pxに設定
    new_window_width = int(screen_width * 0.42)  # 画面幅の42%
    new_window_height = 250  # 高さを調整（テキスト表示が見やすいように250pxに）

    # 新しいウィンドウのサイズを設定
    new_window.geometry(f"{new_window_width}x{new_window_height}")  # 動的なサイズ設定

    # 注意書きのテキストを表示
    notice_text = (
        "注意: スクレイピングを行う際の留意点\n\n"
        "1. スクレイピングを行う前に、対象のウェブサイトの利用規約を確認してください。\n"
        "2. サーバーに過度な負荷をかけないように、適切な間隔でリクエストを送るようにしましょう。\n"
        "3. 法的な問題が生じないよう、スクレイピングを行う前に、サイト運営者に許可を得ることを推奨します。\n"
        "4. スクレイピングしたデータの使用についても注意が必要です。\n"
        "5. サイト側の負荷を減らすため、適切に間隔を空けてリクエストを送信しましょう。"
    )
    
    # 新しいウィンドウにラベルを追加して注意書きを表示
    label = tk.Label(new_window, text=notice_text, font=("Arial", 12), justify="left", anchor="w")
    label.pack(padx=20, pady=10, anchor="nw", fill="both")  # anchor="nw"で左上に配置、fill="both"でテキストが広がる

    # 閉じるボタンを追加
    button = tk.Button(new_window, text="閉じる", command=new_window.destroy)  # 閉じるボタン
    button.pack(pady=10)

"""
def sanitize_filename(filename):
    # 無効な文字を正規表現で置き換え（Windowsのファイル名に使えない文字を除去）
    invalid_chars = r'[<>:"/\\|?*]'  # 無効な文字リスト
    filename = re.sub(invalid_chars, "_", filename)  # 無効な文字をアンダースコアに置換
    return filename
"""
# フォルダの作成
def makeFolder(folder):
    global input_folder
   # folder = txtbox2.get()
    # ファルダ名を記入しているかの確認
    if folder:
        tmsg.showinfo("作成しました！","フォルダを作成しました！！！！！")
    
    
    input_folder = Path(folder)
    input_folder.mkdir(exist_ok = True)
    

def dataoutPut(url, countimg=None):
    global input_folder, filename
    
    try:
        # URLからHTMLを取得
        html = requests.get(url)
        
        # BeautifulSoupでHTMLを解析
        soup = BeautifulSoup(html.content, "html.parser")
        
        # 取得する画像の最大数を設定
        if countimg is None:
            countimg_max = float('inf')  # 無限大にして、すべての画像を取得
        else:
            countimg_max = countimg
        
        countLevel = 0
        
        # imgタグをすべて取得
        for elements in soup.find_all("img"):
            if countLevel >= countimg_max:
                break
            
            # 画像のsrc属性を取得
            src = elements.get("src")
            
            if not src:
                continue  # srcがない場合はスキップ
            
            # 完全な画像URLを取得
            imgdata = urllib.parse.urljoin(url, src)
            
            # SVGは除外
            if "svg" in imgdata:
                continue
            
            try:
                # 画像データを取得
                img = requests.get(imgdata)
                img.raise_for_status()  # ステータスコードチェック
            except requests.exceptions.RequestException as e:
                print(f"画像の取得に失敗しました: {e}")
                continue
            
            # ファイル名の無効な文字を置き換え
            filename = imgdata.split("/")[-1]
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)  # 無効な文字を_に置換
            
            # 保存先のフォルダを作成（存在しない場合）
            out_folder = os.path.join(input_folder, filename)
            os.makedirs(os.path.dirname(out_folder), exist_ok=True)  # フォルダがない場合作成
            
            try:
                # 画像ファイルを保存
                with open(out_folder, mode="wb") as f:
                    f.write(img.content)
            except Exception as e:
                print(f"画像の保存に失敗しました: {e}")
                continue
            
            countLevel += 1
        # 取得した画像数を表示
        if countimg_max == float('inf'):
            count_display = "すべての画像"
        else:
            count_display = str(countLevel)
        # 処理した画像数を表示
        print(f"取得した画像数: {count_display}")
        time.sleep(1)
        tmsg.showinfo(f"{count_display}書き込み完了", f"指定された{count_display}件の画像ファイルの書き込みが終了しました")
            
    except requests.exceptions.RequestException as e:
        tmsg.showerror("エラー", f"リクエストエラーが発生しました: {e}")
    except AttributeError as e:
        tmsg.showerror("エラー", f"HTML解析エラーが発生しました: {e}")
    except Exception as e:
        tmsg.showerror("エラー", f"エラーが発生しました: {e}")

# 画像取得方法を選択するGUI
def chooseImageOption():
    global window # window をグローバル変数として扱う
    def selectAll():
        global countimg
        countimg = None  # すべての画像を取得
        window.quit()  # 処理完了後にウィンドウを閉じる

    def selectNumber():
        def enterNumber():
            global countimg
            countimg_str = count_entry.get()
            if not countimg_str.strip():
                tmsg.showerror("エラー", "件数を入力してください！")
                return
            
            try:
                countimg = int(countimg_str.strip())  # 数字に変換
                if countimg <= 0:
                    tmsg.showerror("エラー", "1件以上の件数を指定してください！")
                    return
                if countimg > 1000:  # 最大1000件までに制限
                    tmsg.showerror("エラー", "最大1000件まで指定できます。")
                    return
                window.quit()  # 処理完了後にウィンドウを閉じる
            except ValueError:
                tmsg.showerror("エラー", "無効な件数が入力されました。数値を入力してください。")
                return
        
        # 画像件数を入力するウィンドウ
        count_window = tk.Toplevel(window)
        count_window.title("件数を入力")
        count_label = tk.Label(count_window, text="取得する画像の件数を入力してください（最大1000件）")
        count_label.pack(pady=5)
        count_entry = tk.Entry(count_window)
        count_entry.pack(pady=5)
        count_button = tk.Button(count_window, text="決定", command=enterNumber)
        count_button.pack(pady=5)
    
    window = tk.Tk()
    window.title("画像取得方法選択")
    
    label = tk.Label(window, text="画像取得方法を選択してください")
    label.pack(pady=10)
    
    # ボタンを作成して表示
    all_button = tk.Button(window, text="すべての画像を取得", command=selectAll)
    all_button.pack(pady=5)
    
    number_button = tk.Button(window, text="指定件数を取得", command=selectNumber)
    number_button.pack(pady=5)
    
    window.mainloop()  # メインループを実行
    # 処理が完了した後にウィンドウを閉じる
    window.destroy()  # ここでメインウィンドウを完全に破棄
    

# 入力メニュー
def inputMenu():
    global end, countimg
    while True:
        folder = simpledialog.askstring("フォルダ名", "フォルダ名を入力してください")
        if folder is None:
            break
        
        if not folder.strip():  
            tmsg.showerror("フォルダ名", "フォルダ名を入力してください！！")
            continue
        
        makeFolder(folder)  
        break
    
    while True:
        url = simpledialog.askstring("URL入力", "URLを入力してください")
        if url is None:  # キャンセルが押された場合、ループを終了
            break
        if url is None or not url.strip():
            tmsg.showerror("エラー", "URLを入力してください！")
            continue
        
        # 画像取得方法を選択する
        chooseImageOption()  # ボタンで選択する
        
        # 選択後、指定された方法で画像取得処理を行う
        dataoutPut(url, countimg)
        
# 画像を消去する関数
def clear_image():
    global imgdata  # imgdataはグローバル変数で、現在表示している画像データを保持
    imgdata = None  # 画像データをNoneに設定
    lbl2.configure(image=None)  # ラベルから画像を削除
    lbl2.image = None  # ラベルから画像の参照も削除

# 画像をGUIに貼る
def disPhont(path):
    global imgdata,cpath
    cpath = path
    newImage = PIL.Image.open(path)
    # ウィンドウのサイズに合わせて画像をリサイズ（例えば、最大サイズ1024x768）
    #window_width = root.winfo_width()
    #window_height = root.winfo_height()
     # 画像のサイズをウィンドウのサイズに合わせて調整
    newImage = newImage.resize((400, 550), PIL.Image.Resampling.LANCZOS)
    # 画像データを表示
    imgdata = PIL.ImageTk.PhotoImage(newImage)
    lbl2.configure(image = imgdata)
    lbl2.image = imgdata
    
    # ファイルパスをテキストボックスに表示
    txtbox1.delete(0, tk.END)
    txtbox1.insert(tk.END, path)

# 画像をGUIに白黒に変換ある
def convdisPhont():
    global cpath
    if cpath:
        # 画像を白黒に変換
        newImage = PIL.Image.open(cpath).convert("L")
        # ウィンドウのサイズに合わせて画像をリサイズ（例えば、最大サイズ1024x768）
        #window_width = root.winfo_width()
        #window_height = root.winfo_height()
        # 画像のサイズをウィンドウのサイズに合わせて調整
        newImage = newImage.resize((400, 550), PIL.Image.Resampling.LANCZOS)
        # 画像データを表示
        imgdata = PIL.ImageTk.PhotoImage(newImage)
        lbl2.configure(image = imgdata)
        lbl2.image = imgdata
    

# ファイルを開く関数
def openFile():
    global img_list, current_index, current_directory
    fpath = fd.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.gif")])  # 画像ファイルの選択
    if fpath:
        # 選択された画像のディレクトリを取得
        current_directory = os.path.dirname(fpath)
        
        # ディレクトリ内の画像ファイルをリストアップ
        img_list = [file for file in os.listdir(current_directory) if file.lower().endswith(('jpg', 'jpeg', 'png', 'gif'))]
        img_list.sort()  # 画像をアルファベット順にソート
        
        # 現在選択した画像のインデックスを取得
        current_index = img_list.index(os.path.basename(fpath))
        
        # 最初の画像を表示
        disPhont(os.path.join(current_directory, img_list[current_index]))

# 次の画像を表示する関数
def nextImg():
    global img_list, current_index, current_directory
    if img_list:
        # 次の画像のインデックスを計算
        current_index = (current_index + 1) % len(img_list)  # リストの終わりに達したら最初に戻る
        
        # 次の画像のパスを取得
        next_image_path = os.path.join(current_directory, img_list[current_index])
        
        # 次の画像を表示
        disPhont(next_image_path)

# 前の画像を表示する関数
def backImg(): 
    global img_list, current_index, current_directory
    if img_list:
        # 次の画像のインデックスを計算
        current_index = (current_index - 1) % len(img_list)  # リストの終わりに達したら最初に戻る
        
        # 次の画像のパスを取得
        next_image_path = os.path.join(current_directory, img_list[current_index])
        
        # 次の画像を表示
        disPhont(next_image_path)
        

# ブラウザを開く関数
def open_browser():
    url = "https://www.google.com/"
    webbrowser.open(url)
# ブラウザを開く関数
def open_browser1():
    url = "https://www.yahoo.co.jp/"
    webbrowser.open(url)
# ブラウザを開く関数

    
# ウィンドを閉じる関数
def close_window():
    root.destroy()


# GUIの設定
root = tk.Tk()
root.title("画像を取得するアプリ")
root.geometry("950x1200")  # サイズを調整（画面に合わせて変更可）

# ラベルの設定
lbl1 = tk.Label(root, text="画像取得アプリ", font=("Arial", 24), pady=20)
lbl1.pack()

lbl2 = tk.Label(root, text="操作を選んでください", font=("Arial", 16), pady=10)
lbl2.pack()

# フレームを作って配置（入力ボックスとボタンを横並びにする）
frame_inputs = tk.Frame(root)
frame_inputs.pack(pady=30)

# txtbox1 と btn1 を横並びに配置
txtbox1 = tk.Entry(frame_inputs, width=50, font=("Arial", 14))
txtbox1.grid(row=0, column=0, padx=10)  # 左側に配置

# btn1 = tk.Button(frame_inputs, text="画像を取得", command=dataoutPut)
# btn1.grid(row=0, column=1, padx=10)  # txtbox1 の隣に配置

# txtbox2 と btn3 を横並びに配置（2行目）
# txtbox2 = tk.Entry(frame_inputs, width=20)
# txtbox2.grid(row=1, column=0, padx=10, pady=10)  # 次の行に配置

# btn3 = tk.Button(frame_inputs, text="フォルダの作成", command=makeFoler)
# btn3.grid(row=1, column=1, padx=10, pady=10)  # txtbox2 の隣に配置
# ボタン用のフレームを作成
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=20)  # 上部に余白を追加して配置

btn4 = tk.Button(frame_buttons, text="画像を白黒する", command=convdisPhont, font=("Arial", 14), width=18)
btn4.grid(row=0, column=1, padx=20, pady=10)  # 中央に配置

btn5 = tk.Button(frame_buttons, text="Back", command=backImg, font=("Arial", 12), width=10)
btn5.grid(row=0, column=0, padx=20, pady=10)  # 左側に配置

btn6 = tk.Button(frame_buttons, text="Next", command=nextImg, font=("Arial", 12), width=10)
btn6.grid(row=0, column=2, padx=20, pady=10)  # 右側に配置



btn9 = tk.Button(frame_buttons, text="閉じる", command=close_window, font=("Arial", 14), width=20)
btn9.grid(row=2, column=1, padx=20, pady=10)  # btn11の真下に配置

btn11 = tk.Button(frame_buttons, text="画像消去", command=clear_image, font=("Arial", 14), width=18)
btn11.grid(row=1, column=1, padx=20, pady=10)  # btn4の真下に配置

btn10 = tk.Button(root, text="注意書き！！", command=open_new_window, font=("Arial", 14), width=13)
btn10.place(x=790, y=11)  # 右下に配置


# メニューバーの作成
menu_bar = tk.Menu(root)

# "ファイル" メニューの作成
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="取得", command=inputMenu)
file_menu.add_command(label="フォルダ名を開く", command=openFile)
menu_bar.add_cascade(label="メニュー", menu=file_menu)

# "接続" メニューの作成
connect_menu = tk.Menu(menu_bar, tearoff=0)
connect_menu.add_command(label="Google接続", command=open_browser)
connect_menu.add_command(label="Yahoo接続", command=open_browser1)
menu_bar.add_cascade(label="接続", menu=connect_menu)

# メニューバーをウィンドウに設定
root.config(menu=menu_bar)

root.mainloop()