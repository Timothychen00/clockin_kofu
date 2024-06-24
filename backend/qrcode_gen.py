import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import VerticalBarsDrawer,RoundedModuleDrawer,HorizontalBarsDrawer,SquareModuleDrawer,GappedSquareModuleDrawer,CircleModuleDrawer
qr = qrcode.QRCode(
    version=2,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=8,
    border=1
)
qr.add_data('https://friedclockin.azurewebsites.net/preview/a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e')   # 要轉換成 QRCode 的文字
qr.make(fit=True)          # 根據參數製作為 QRCode 物件

img = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer())      # 產生 QRCode 圖片
img.show()                 # 顯示圖片 ( Colab 不適用 )
img.save('main/static/qrcode1.png')     # 儲存圖片