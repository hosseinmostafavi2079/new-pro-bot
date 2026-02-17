import os
import requests
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.drawing.image import Image as ExcelImage
from PIL import Image as PilImage

def generate_excel_report(products, filename="products_report.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.sheet_view.rightToLeft = True  # راست‌چین کردن شیت
    ws.title = "گزارش محصولات"

    # --- استایل‌ها ---
    header_font = Font(name='B Titr', size=12, bold=True, color="FFFFFF")
    cell_font = Font(name='B Nazanin', size=11)
    center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
    
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid") # آبی تیره
    
    border_style = Side(border_style="thin", color="000000")
    border = Border(left=border_style, right=border_style, top=border_style, bottom=border_style)

    # --- هدر ---
    headers = ["تصویر", "نام محصول", "SKU", "قیمت (تومان)", "وضعیت", "دسته‌بندی", "لینک"]
    ws.append(headers)

    # اعمال استایل به هدر
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = border

    # تنظیم عرض ستون‌ها
    ws.column_dimensions['A'].width = 15  # ستون عکس
    ws.column_dimensions['B'].width = 40  # نام
    ws.column_dimensions['C'].width = 15  # SKU
    ws.column_dimensions['D'].width = 20  # قیمت
    ws.column_dimensions['E'].width = 15  # وضعیت
    ws.column_dimensions['F'].width = 20  # دسته
    ws.column_dimensions['G'].width = 30  # لینک

    # --- پر کردن داده‌ها ---
    row_num = 2
    for p in products:
        # تنظیم ارتفاع سطر برای عکس
        ws.row_dimensions[row_num].height = 60

        # اطلاعات متنی
        title = p.get('name', '---')
        sku = p.get('sku', '---')
        try:
            price = "{:,}".format(int(p['regular_price'])) if p.get('regular_price') else "0"
        except: price = "0"
        
        stock_status = "✅ موجود" if p.get('stock_status') == 'instock' else "❌ ناموجود"
        
        cats = [c['name'] for c in p.get('categories', [])]
        cat_str = "، ".join(cats)
        
        link = p.get('permalink', '')

        # نوشتن در سلول‌ها
        ws.cell(row=row_num, column=2, value=title).alignment = center_align
        ws.cell(row=row_num, column=3, value=sku).alignment = center_align
        ws.cell(row=row_num, column=4, value=price).alignment = center_align
        ws.cell(row=row_num, column=5, value=stock_status).alignment = center_align
        ws.cell(row=row_num, column=6, value=cat_str).alignment = center_align
        ws.cell(row=row_num, column=7, value=link).alignment = center_align

        # اعمال فونت و بوردر
        for col in range(2, 8):
            cell = ws.cell(row=row_num, column=col)
            cell.font = cell_font
            cell.border = border

        # --- پردازش عکس ---
        img_url = p['images'][0]['src'] if p.get('images') else None
        if img_url:
            try:
                response = requests.get(img_url, timeout=5)
                if response.status_code == 200:
                    image_data = BytesIO(response.content)
                    pil_img = PilImage.open(image_data)
                    
                    # ریسایز عکس برای اینکه حجم فایل زیاد نشه
                    pil_img.thumbnail((80, 80))
                    
                    # تبدیل به فرمت اکسل
                    img = ExcelImage(pil_img)
                    
                    # محاسبه مکان دقیق وسط سلول (تقریبی)
                    # انکور به سلول A + شماره ردیف
                    anchor = f"A{row_num}"
                    ws.add_image(img, anchor)
            except Exception as e:
                print(f"Image Error: {e}")
                ws.cell(row=row_num, column=1, value="No Image")
        
        row_num += 1

    wb.save(filename)
    return filename