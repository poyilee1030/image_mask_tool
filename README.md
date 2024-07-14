
Original                   |  After mask
:-------------------------:|:-------------------------:
![](https://github.com/poyilee1030/image_mask_tool/blob/main/input/demo.png)  |  ![](https://github.com/poyilee1030/image_mask_tool/blob/main/output/demo.png)


這個 repository 展示了一個 圖片遮蔽小程式

使用說明
1. 建置 python 3.8 環境，按照 requirements.txt 安裝 library

2. 執行 main.py

3. 點擊 select src 按鈕(在右上角)，選取 input 資料夾 (裡面有一張 demo.png)

4. 直接在左邊的圖上用滑鼠左鍵拖拉一個矩形 (或多個)
   這些位置會被記錄在右下的清單中，使用 delete 刪除

5. 點擊 save image，會存在 output/demo.png 底下
   可以看到原本選取的矩形被遮蔽了
   而原本的 input 資料夾內會多出一個 demo.json
   這是為了下次讀取時還能記得上次選取的位置

6. 執行 reverse.py
   在 reverse 資料夾下會得到原本的圖

我將 main.py 和 reverse.py 打包成了 exe 並放在 release.zip 裡面
你可以直接下載和執行
就不需要建置第一步的環境了

-------------------------------------------------------------------------------

This repository demonstrates an image masking tool.

Instructions for Use:
1. Set up a Python 3.8 environment and install the required libraries using requirements.txt.

2. Run main.py.

3. Click the "select src" button (top right corner) and choose the input folder (which contains a demo.png).

4. Left-click and drag on the image on the left to create one or more rectangles.
   These positions will be recorded in the list on the bottom right. Use "delete" to remove rectangles.

5. Click "save image". The masked image will be saved in output/demo.png.
   Additionally, a demo.json file will be created in the input folder to remember the selected positions for future use.

6. Run reverse.py. You will find the original image in the reverse folder.

I have packaged main.py and reverse.py into an executable (release.zip). 
You can download and run it directly without needing to set up the environment in step one.

