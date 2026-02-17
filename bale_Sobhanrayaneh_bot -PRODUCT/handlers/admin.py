import os
from utils.state_manager import state_manager
from services.bale import BaleService
from services.woo import WooService
from services.ai import AIService
from utils.image_utils import process_image  
from utils.excel_logger import log_product_to_excel, log_edit_to_excel, LOG_FILE
# ایمپورت ماژول جدید اکسل ساز
from utils.excel_exporter import generate_excel_report
from utils.auth_manager import auth

bale = BaleService()
woo = WooService()
ai = AIService()

# --- مراحل وضعیت ---
(
    WAITING_TITLE, WAITING_PRICE, WAITING_SKU, WAITING_CATEGORY, WAITING_IMAGE,
    WAITING_NEW_ADMIN_ID, WAITING_DEL_ADMIN_ID, WAITING_EDIT_SEARCH, WAITING_EDIT_VALUE,
    # مراحل جدید برای اکسل
    WAITING_EXPORT_TYPE, WAITING_EXPORT_SCOPE, WAITING_EXPORT_CAT
) = map(str, range(12))

# --- کیبوردها ---
BTN_CANCEL = [["🔙 انصراف"]]
BTN_FINISH_UPLOAD = [["✅ پایان ارسال و انتشار"], ["🔙 انصراف"]]

KB_MAIN_SUPER = [
    ["➕ افزودن محصول", "✏️ ویرایش محصول"],
    ["📊 دریافت گزارش", "👤 مدیریت ادمین‌ها"],
    ["📥 خروجی اکسل محصولات"] # دکمه جدید
]

KB_MAIN_SUB = [
    ["➕ افزودن محصول", "✏️ ویرایش محصول"],
    ["📥 خروجی اکسل محصولات"]
]

KB_ADMIN_PANEL = [
    ["➕ استخدام مدیر", "❌ حذف مدیر"],
    ["📋 لیست مدیران"],
    ["🔙 بازگشت"]
]

INLINE_EDIT_ACTIONS = [
    [{"text": "💰 تغییر قیمت", "callback_data": "action_price"}, {"text": "🗑 حذف قیمت", "callback_data": "action_del_price"}],
    [{"text": "➕ افزایش موجودی", "callback_data": "action_add_stock"}, {"text": "➖ کاهش موجودی", "callback_data": "action_reduce_stock"}],
    [{"text": "✅ موجود (InStock)", "callback_data": "action_instock"}, {"text": "❌ ناموجود (OutStock)", "callback_data": "action_outstock"}],
    [{"text": "🔄 بروزرسانی وضعیت", "callback_data": "action_refresh"}, {"text": "🔙 انصراف", "callback_data": "action_cancel"}]
]

def show_product_panel(chat_id, product):
    title = product['name']
    sku = product.get('sku', '---')
    link = product.get('permalink', '#')
    try:
        if not product.get('regular_price'): price = "ندارد ❌"
        else: price = f"{int(product['regular_price']):,} تومان"
    except: price = "نامشخص"

    qty = product.get('stock_quantity') or 0
    is_managing = product.get('manage_stock', False)
    if product['stock_status'] == 'instock':
        stock_display = f"✅ موجود (تعداد: {qty})" if is_managing else "✅ موجود"
    else:
        stock_display = "❌ ناموجود"
    
    img = product['images'][0]['src'] if product['images'] else None
    caption = f"📦 <b>مدیریت محصول:</b>\n🏷 <b>نام:</b> {title}\n🔖 <b>SKU:</b> <code>{sku}</code>\n💰 <b>قیمت:</b> {price}\n📦 <b>وضعیت:</b> {stock_display}\n👇 عملیات:"
    
    if img:
        try: bale.send_photo(chat_id, img, caption, inline_keyboard=INLINE_EDIT_ACTIONS)
        except: bale.send_message(chat_id, caption, inline_keyboard=INLINE_EDIT_ACTIONS)
    else:
        bale.send_message(chat_id, caption, inline_keyboard=INLINE_EDIT_ACTIONS)

def handle_admin_flow(chat_id, message_data, is_callback=False):
    text = message_data.get("text", "")
    current_step = state_manager.get_step(chat_id)
    user_role = auth.get_role(chat_id)
    main_kb = KB_MAIN_SUPER if user_role == "super_admin" else KB_MAIN_SUB

    if is_callback:
        data = state_manager.get_data(chat_id)
        ctx = data.get("edit_context")
        if text == "action_cancel":
            state_manager.clear_state(chat_id)
            bale.send_message(chat_id, "لغو عملیات.", keyboard=main_kb)
            return
        if not ctx and text.startswith("action_"):
            bale.send_message(chat_id, "⚠️ نشست منقضی شده. لطفا دوباره جستجو کنید.")
            return

        if text == "action_price":
            state_manager.update_data(chat_id, "edit_mode", "price")
            state_manager.set_step(chat_id, WAITING_EDIT_VALUE)
            bale.send_message(chat_id, "💰 <b>قیمت جدید</b> (تومان):", keyboard=BTN_CANCEL)
            return
        elif text == "action_del_price":
            woo.update_product(ctx['id'], {"regular_price": "", "sale_price": ""})
            log_edit_to_excel(chat_id, ctx['name'], ctx['sku'], "حذف قیمت", "قیمت حذف شد")
            bale.send_message(chat_id, "🗑 قیمت حذف شد.")
            new_prod = woo.get_product_by_sku(ctx['sku'])
            if new_prod: show_product_panel(chat_id, new_prod)
            return
        elif text == "action_add_stock":
            state_manager.update_data(chat_id, "edit_mode", "add_stock")
            state_manager.set_step(chat_id, WAITING_EDIT_VALUE)
            bale.send_message(chat_id, "➕ تعداد <b>افزایش</b>:", keyboard=BTN_CANCEL)
            return
        elif text == "action_reduce_stock":
            state_manager.update_data(chat_id, "edit_mode", "reduce_stock")
            state_manager.set_step(chat_id, WAITING_EDIT_VALUE)
            bale.send_message(chat_id, "➖ تعداد <b>کاهش</b>:", keyboard=BTN_CANCEL)
            return
        elif text == "action_instock":
            woo.update_product(ctx['id'], {"stock_status": "instock", "manage_stock": False})
            log_edit_to_excel(chat_id, ctx['name'], ctx['sku'], "تغییر وضعیت", "InStock")
            bale.send_message(chat_id, "✅ موجود شد.")
            new_prod = woo.get_product_by_sku(ctx['sku'])
            if new_prod: show_product_panel(chat_id, new_prod)
            return
        elif text == "action_outstock":
            woo.update_product(ctx['id'], {"stock_status": "outofstock"})
            log_edit_to_excel(chat_id, ctx['name'], ctx['sku'], "تغییر وضعیت", "OutStock")
            bale.send_message(chat_id, "❌ ناموجود شد.")
            new_prod = woo.get_product_by_sku(ctx['sku'])
            if new_prod: show_product_panel(chat_id, new_prod)
            return
        elif text == "action_refresh":
            new_prod = woo.get_product_by_sku(ctx['sku'])
            if new_prod: show_product_panel(chat_id, new_prod)
            return

    if text == "🔙 انصراف":
        state_manager.clear_state(chat_id)
        bale.send_message(chat_id, "لغو شد.", keyboard=main_kb)
        return

    # ==========================
    # بخش جدید: خروجی اکسل
    # ==========================
    if text == "📥 خروجی اکسل محصولات":
        state_manager.clear_state(chat_id)
        state_manager.set_step(chat_id, WAITING_EXPORT_TYPE)
        kb = [["همه محصولات"], ["فقط موجودها", "فقط ناموجودها"], ["🔙 انصراف"]]
        bale.send_message(chat_id, "📊 چه محصولاتی را می‌خواهید؟", keyboard=kb)
        return

    if current_step == WAITING_EXPORT_TYPE:
        status_map = {
            "فقط موجودها": "instock",
            "فقط ناموجودها": "outofstock",
            "همه محصولات": None
        }
        if text not in status_map:
            bale.send_message(chat_id, "لطفا از دکمه‌ها انتخاب کنید.")
            return
        
        state_manager.update_data(chat_id, "export_status", status_map[text])
        
        kb = [["کل فروشگاه"], ["انتخاب دسته‌بندی خاص"], ["🔙 انصراف"]]
        state_manager.set_step(chat_id, WAITING_EXPORT_SCOPE)
        bale.send_message(chat_id, "📂 محدوده گزارش؟", keyboard=kb)
        return

    if current_step == WAITING_EXPORT_SCOPE:
        if text == "کل فروشگاه":
            export_data(chat_id)
            return
        elif text == "انتخاب دسته‌بندی خاص":
            bale.send_message(chat_id, "⏳ دریافت دسته‌ها...")
            cats = woo.get_categories(0)
            kb = []
            row = []
            cats_map = {}
            for c in cats:
                cats_map[c['name']] = c['id']
                row.append(c['name'])
                if len(row) == 2:
                    kb.append(row)
                    row = []
            if row: kb.append(row)
            kb.append(["🔙 انصراف"])
            state_manager.update_data(chat_id, "export_cats_map", cats_map)
            state_manager.set_step(chat_id, WAITING_EXPORT_CAT)
            bale.send_message(chat_id, "📂 کدام دسته؟", keyboard=kb)
            return
        else:
            bale.send_message(chat_id, "انتخاب اشتباه.")
            return

    if current_step == WAITING_EXPORT_CAT:
        data = state_manager.get_data(chat_id)
        cats_map = data.get("export_cats_map", {})
        if text not in cats_map:
            bale.send_message(chat_id, "نامعتبر.")
            return
        
        cat_id = cats_map[text]
        state_manager.update_data(chat_id, "export_cat_id", cat_id)
        export_data(chat_id)
        return

    # ==========================
    # لاجیک‌های قبلی (مدیریت، ویرایش، افزودن)
    # ==========================
    if user_role == "super_admin":
        if text == "👤 مدیریت ادمین‌ها":
            bale.send_message(chat_id, "⚙️ پنل پرسنل:", keyboard=KB_ADMIN_PANEL)
            return
        if text == "🔙 بازگشت":
            bale.send_message(chat_id, "🏠 منوی اصلی:", keyboard=main_kb)
            return
        if text == "📋 لیست مدیران":
            admins = auth.get_all_admins()
            msg = f"👑 Super: {admins['super']}\n💼 Sub: {admins['sub']}"
            bale.send_message(chat_id, msg)
            return
        if text == "➕ استخدام مدیر":
            state_manager.clear_state(chat_id)
            state_manager.set_step(chat_id, WAITING_NEW_ADMIN_ID)
            bale.send_message(chat_id, "🔢 آیدی:", keyboard=BTN_CANCEL)
            return
        if current_step == WAITING_NEW_ADMIN_ID:
            if text.isdigit() and auth.add_admin(int(text)):
                bale.send_message(chat_id, "✅ شد.", keyboard=KB_ADMIN_PANEL)
            else:
                bale.send_message(chat_id, "⚠️ نشد.", keyboard=KB_ADMIN_PANEL)
            state_manager.clear_state(chat_id)
            return
        if text == "❌ حذف مدیر":
            state_manager.clear_state(chat_id)
            state_manager.set_step(chat_id, WAITING_DEL_ADMIN_ID)
            bale.send_message(chat_id, "🔢 آیدی:", keyboard=BTN_CANCEL)
            return
        if current_step == WAITING_DEL_ADMIN_ID:
            if text.isdigit() and auth.remove_admin(int(text)):
                bale.send_message(chat_id, "🗑 شد.", keyboard=KB_ADMIN_PANEL)
            else:
                bale.send_message(chat_id, "⛔ نشد.", keyboard=KB_ADMIN_PANEL)
            state_manager.clear_state(chat_id)
            return
        if text == "📊 دریافت گزارش":
            if os.path.exists(LOG_FILE):
                bale.send_document(chat_id, LOG_FILE, caption="📊 گزارش عملکرد")
            else:
                bale.send_message(chat_id, "❌ خالی.")
            return

    if text == "✏️ ویرایش محصول":
        state_manager.clear_state(chat_id)
        state_manager.set_step(chat_id, WAITING_EDIT_SEARCH)
        bale.send_message(chat_id, "🔍 SKU را وارد کنید:", keyboard=BTN_CANCEL)
        return

    if current_step == WAITING_EDIT_SEARCH:
        bale.send_message(chat_id, "⏳ جستجو...")
        product = woo.get_product_by_sku(text)
        if not product:
            bale.send_message(chat_id, "❌ یافت نشد.", keyboard=BTN_CANCEL)
            return
        edit_context = {"id": product['id'], "name": product['name'], "sku": product.get('sku', text)}
        state_manager.update_data(chat_id, "edit_context", edit_context)
        show_product_panel(chat_id, product)
        return

    if current_step == WAITING_EDIT_VALUE:
        data = state_manager.get_data(chat_id)
        ctx = data.get("edit_context")
        mode = data.get("edit_mode")
        if not ctx:
            bale.send_message(chat_id, "❌ نشست منقضی شد.", keyboard=main_kb)
            state_manager.clear_state(chat_id)
            return
        clean_text = text.replace(",", "")
        if not clean_text.isdigit():
            bale.send_message(chat_id, "⛔ فقط عدد.")
            return
        value = int(clean_text)
        update_data = {}
        log_action, log_details = "", ""
        
        if mode == "price":
            update_data = {"regular_price": str(value)}
            log_action = "تغییر قیمت"
            log_details = f"قیمت: {value}"
        elif mode == "add_stock":
            current_prod = woo.get_product_by_sku(ctx['sku'])
            current_qty = (current_prod.get('stock_quantity') or 0) if current_prod else 0
            new_qty = current_qty + value
            update_data = {"stock_quantity": new_qty, "manage_stock": True, "stock_status": "instock"}
            log_action = "افزایش موجودی"
            log_details = f"موجودی: {new_qty} (+{value})"
        elif mode == "reduce_stock":
            current_prod = woo.get_product_by_sku(ctx['sku'])
            current_qty = (current_prod.get('stock_quantity') or 0) if current_prod else 0
            new_qty = max(0, current_qty - value)
            update_data = {"stock_quantity": new_qty, "manage_stock": True}
            if new_qty == 0: update_data["stock_status"] = "outofstock"
            log_action = "کاهش موجودی"
            log_details = f"موجودی: {new_qty} (-{value})"

        bale.send_message(chat_id, "⏳ اعمال...")
        res = woo.update_product(ctx['id'], update_data)
        if res:
            log_edit_to_excel(chat_id, ctx['name'], ctx['sku'], log_action, log_details)
            bale.send_message(chat_id, f"✅ شد!\n{log_details}")
            state_manager.set_step(chat_id, WAITING_EDIT_SEARCH)
            new_prod = woo.get_product_by_sku(ctx['sku'])
            if new_prod: show_product_panel(chat_id, new_prod)
        else:
            bale.send_message(chat_id, "❌ خطا.", keyboard=main_kb)
            state_manager.set_step(chat_id, WAITING_EDIT_SEARCH)
        return

    if text == "➕ افزودن محصول":
        state_manager.clear_state(chat_id)
        state_manager.set_step(chat_id, WAITING_TITLE)
        bale.send_message(chat_id, "🛒 <b>نام محصول</b>:", keyboard=BTN_CANCEL)
        return
    if current_step == WAITING_TITLE:
        state_manager.update_data(chat_id, "title", text)
        state_manager.set_step(chat_id, WAITING_PRICE)
        bale.send_message(chat_id, "💰 <b>قیمت</b>:", keyboard=BTN_CANCEL)
        return
    if current_step == WAITING_PRICE:
        clean = text.replace(",", "")
        if not clean.isdigit():
            bale.send_message(chat_id, "⛔ فقط عدد.")
            return
        state_manager.update_data(chat_id, "price", clean)
        state_manager.set_step(chat_id, WAITING_SKU)
        bale.send_message(chat_id, "🔖 <b>SKU</b>:", keyboard=BTN_CANCEL)
        return
    if current_step == WAITING_SKU:
        state_manager.update_data(chat_id, "sku", text)
        bale.send_message(chat_id, "⏳ دسته‌ها...")
        cats = woo.get_categories(parent=0)
        kb = []
        row = []
        valid = {}
        for c in cats:
            valid[c['name']] = c['id']
            row.append(c['name'])
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        kb.append(["🔙 انصراف"])
        state_manager.update_data(chat_id, "valid_cats", valid)
        state_manager.set_step(chat_id, WAITING_CATEGORY)
        bale.send_message(chat_id, "📂 دسته:", keyboard=kb)
        return
    if current_step == WAITING_CATEGORY:
        data = state_manager.get_data(chat_id)
        valid = data.get("valid_cats", {})
        if text not in valid:
            bale.send_message(chat_id, "⛔ انتخاب کنید.")
            return
        cat_id = valid[text]
        subs = woo.get_categories(parent=cat_id)
        if subs:
            new_valid = {}
            new_kb = []
            row = []
            for c in subs:
                new_valid[c['name']] = c['id']
                row.append(c['name'])
                if len(row) == 2:
                    new_kb.append(row)
                    row = []
            if row: new_kb.append(row)
            new_kb.append(["🔙 انصراف"])
            state_manager.update_data(chat_id, "valid_cats", new_valid)
            bale.send_message(chat_id, f"📂 زیردسته «{text}»:", keyboard=new_kb)
            return
        else:
            state_manager.update_data(chat_id, "cat_id", cat_id)
            title = data['title']
            bale.send_message(chat_id, "1️⃣ لینک...", keyboard=BTN_CANCEL)
            slug = ai.generate_slug(title)
            state_manager.update_data(chat_id, "seo_slug", slug or title)
            bale.send_message(chat_id, "2️⃣ مقاله...", keyboard=BTN_CANCEL)
            long = ai.generate_long_desc(title)
            state_manager.update_data(chat_id, "seo_long", long or "")
            bale.send_message(chat_id, "3️⃣ خلاصه...", keyboard=BTN_CANCEL)
            short = ai.generate_short_desc(title)
            state_manager.update_data(chat_id, "seo_short", short or "")
            state_manager.update_data(chat_id, "uploaded_images", []) 
            state_manager.set_step(chat_id, WAITING_IMAGE)
            bale.send_message(chat_id, "📸 عکس‌ها؟", keyboard=BTN_FINISH_UPLOAD)
            return
    if current_step == WAITING_IMAGE:
        data = state_manager.get_data(chat_id)
        uploaded_images = data.get("uploaded_images", [])
        if text == "✅ پایان ارسال و انتشار":
            if not uploaded_images:
                bale.send_message(chat_id, "⛔ حداقل یک عکس.", keyboard=BTN_FINISH_UPLOAD)
                return
            bale.send_message(chat_id, f"🚀 انتشار...")
            result = woo.create_product(
                title=data['title'], price=data['price'], sku=data['sku'],
                category_id=data['cat_id'], slug=data['seo_slug'],
                description=data['seo_long'], short_description=data['seo_short'],
                image_ids=uploaded_images
            )
            if result and result.get("id"):
                link = result.get('permalink')
                log_product_to_excel(chat_id, data['title'], data['price'], data['sku'], link)
                bale.send_message(chat_id, f"✅ منتشر شد!\n🔗 {link}", keyboard=KB_MAIN_SUPER)
                state_manager.clear_state(chat_id)
            else:
                bale.send_message(chat_id, "❌ خطا.")
            return
        if "photo" in message_data:
            bale.send_message(chat_id, "⏳ آپلود...")
            file_id = message_data["photo"][-1]["file_id"]
            path = bale.get_file_path(file_id)
            raw = bale.download_file(path)
            if not raw: return
            processed = process_image(raw)
            wp_id = woo.upload_image_to_wp(processed)
            if wp_id:
                uploaded_images.append(wp_id)
                state_manager.update_data(chat_id, "uploaded_images", uploaded_images)
                bale.send_message(chat_id, f"✅ عکس {len(uploaded_images)}.", keyboard=BTN_FINISH_UPLOAD)
            return

def export_data(chat_id):
    """تابع اجرایی برای جمع‌آوری داده و ارسال فایل"""
    main_kb = KB_MAIN_SUPER if auth.get_role(chat_id) == "super_admin" else KB_MAIN_SUB
    bale.send_message(chat_id, "⏳ در حال دریافت محصولات و دانلود تصاویر... (ممکن است زمان ببرد)")
    
    data = state_manager.get_data(chat_id)
    status = data.get("export_status")
    cat_id = data.get("export_cat_id")
    
    all_products = []
    
    # استفاده از جنریتور برای دریافت تمام صفحات
    for batch in woo.get_all_products_generator(category_id=cat_id, stock_status=status):
        all_products.extend(batch)
        # اطلاع رسانی پیشرفت به کاربر
        if len(all_products) % 20 == 0:
            bale.send_message(chat_id, f"📥 {len(all_products)} محصول دریافت شد...")

    if not all_products:
        bale.send_message(chat_id, "❌ محصولی با این مشخصات یافت نشد.", keyboard=main_kb)
        state_manager.clear_state(chat_id)
        return

    bale.send_message(chat_id, f"🎨 در حال ساخت فایل اکسل برای {len(all_products)} محصول...")
    
    try:
        filename = generate_excel_report(all_products, f"Export_{chat_id}.xlsx")
        bale.send_document(chat_id, filename, caption=f"📊 لیست محصولات\nتعداد: {len(all_products)}")
        os.remove(filename)
    except Exception as e:
        print(f"Export Error: {e}")
        bale.send_message(chat_id, "❌ خطا در ساخت فایل.", keyboard=main_kb)

    state_manager.clear_state(chat_id)