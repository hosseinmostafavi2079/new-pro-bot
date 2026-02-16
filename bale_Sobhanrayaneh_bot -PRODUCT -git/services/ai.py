import httpx
from openai import OpenAI
from config import Config

class AIService:
    def __init__(self):
        # تنظیم کلاینت برای اتصال مستقیم
        http_client = httpx.Client(
            timeout=60.0,
            follow_redirects=True,
            verify=False,
            trust_env=False  
        )
        
        self.client = OpenAI(
            base_url="https://api.gapgpt.app/v1",
            api_key=Config.GAP_API_KEY,
            http_client=http_client,
            max_retries=1
        )

        # لیست کامل لینک‌ها استخراج شده از فایل شما
        self.internal_links_data = """
        - صفحه اصلی: https://sobhanrayaneh.com/
        - فروشگاه: https://sobhanrayaneh.com/shop/
        - تماس با ما: https://sobhanrayaneh.com/contact-us/
        - وبلاگ: https://sobhanrayaneh.com/blog
        - طرح تعویض: https://sobhanrayaneh.com/change/
        - فروش اقساطی: https://sobhanrayaneh.com/%d9%81%d8%b1%d9%88%d8%b4-%d8%a7%d9%82%d8%b3%d8%a7%d8%b7%db%8c/
        - لپ تاپ: https://sobhanrayaneh.com/category/laptop/
        - لپ تاپ ایسوس: https://sobhanrayaneh.com/category/laptop/asus-laptop/
        - لپ تاپ لنوو: https://sobhanrayaneh.com/category/laptop/lenovo-laptop/
        - لپ تاپ ایسر: https://sobhanrayaneh.com/category/laptop/laptop-acer/
        - لپ تاپ اچ پی: https://sobhanrayaneh.com/category/laptop/hp/
        - لپ تاپ ام اس ای: https://sobhanrayaneh.com/category/laptop/msi-laptop/
        - کامپیوتر همه کاره (آل این وان): https://sobhanrayaneh.com/category/all-in-one/
        - آل این وان ام اس ای: https://sobhanrayaneh.com/category/all-in-one/msi-all-in-one/
        - آل این وان مایا: https://sobhanrayaneh.com/category/all-in-one/maya/
        - آل این وان لنوو: https://sobhanrayaneh.com/category/all-in-one/lenovo/
        - مانیتور: https://sobhanrayaneh.com/category/monitor/
        - مانیتور ام اس ای: https://sobhanrayaneh.com/category/monitor/msi/
        - مانیتور ایسر: https://sobhanrayaneh.com/category/monitor/acer/
        - مانیتور ایسوس: https://sobhanrayaneh.com/category/monitor/asus/
        - پایه های نگهدارنده : https://sobhanrayaneh.com/category/holder-base/
        """

    def _send_request(self, system_msg, user_msg):
        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.6 # کمی کاهش دما برای دقیق‌تر شدن متن فنی
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ AI Connection Error: {e}")
            return None

    def generate_slug(self, product_name):
        # تولید URL Slug بهینه برای سئو (کوتاه و شامل کلمات کلیدی انگلیسی)
        sys = "You are a specialized SEO URL generator."
        usr = f"Create a short, SEO-friendly English URL slug for: '{product_name}'. Use lowercase, hyphens only. Remove stop words."
        result = self._send_request(sys, usr)
        if result:
            return result.replace(" ", "-").lower()
        return None

    def generate_short_desc(self, product_name):
        # توضیحات کوتاه (Meta Description Style) برای افزایش CTR
        sys = 'You are a Copywriter for "Sobhan Rayaneh". Write in Persian.'
        usr = (
            f"Write a 2-sentence persuasive summary for '{product_name}'.\n"
            "Include keywords: [خرید آنلاین, گارانتی اصلی, تحویل فوری].\n"
            "Tone: Exciting and Professional. NO emojis."
        )
        return self._send_request(sys, usr)

    def generate_long_desc(self, product_name):
        print(f"LOG: Generating SEO-Optimized Content for {product_name}...")
        
        # System Prompt: تعریف دقیق پرسونای متخصص سئو
        sys = (
            'You are a Senior SEO Content Strategist & Hardware Expert for "سبحان رایانه". '
            'Your goal is to write content that ranks #1 on Google (High E-E-A-T). '
            'You speak Persian fluently with a modern, authoritative tech tone.'
        )
        
        # User Prompt: دستورالعمل دقیق محتوایی و لینک‌سازی
        usr = (
            f"Act as a Senior SEO Content Specialist and Product Reviewer for 'سبحان رایانه'.\n"
            f"Write a comprehensive, HTML-formatted product review for: '{product_name}'.\n\n"

            "**CRITICAL RULE (NEGATIVE CONSTRAINT):**\n"
            "❌ **NEVER mention 'Warranty', 'Guarantee', or 'گارانتی' in any part of the text.**\n"
            "Focus ONLY on product features, shipping, support, installments, and price.\n\n"

            "**Strategy 1: Dynamic Content Generation**\n"
            "Since the product list varies widely (Laptops, Mouse, Server parts, Cables, etc.), you must:\n"
            "1. **Analyze the Product:** Determine the category of '{product_name}'.\n"
            "2. **Generate Relevant H3 Headers:** Do NOT use fixed headers. Create 3-4 H3 sections strictly relevant to THIS product's key features (e.g., if it's a Mouse -> Ergonomics/DPI; if it's a CPU -> Cores/Frequency/Temperature).\n"
            "3. **Dynamic FAQ:** Generate 3 questions that users actually ask about THIS specific product type (excluding warranty).\n\n"

            "**Strategy 2: Smart Internal Linking**\n"
            "You have access to the following link database:\n"
            f"{self.internal_links_data}\n"
            "**Linking Instructions:**\n"
            "1. Detect the product category and link to the relevant parent category (e.g., 'خرید مانیتور').\n"
            "2. Detect user intent (e.g., high price -> link to 'خرید اقساطی').\n"
            "3. **Embed 3-5 distinct links** naturally within the text using <a href='URL' target='_blank'>Keyword</a> tags.\n"
            "4. Do NOT force links; they must fit the sentence structure.\n\n"

            "**Strategy 3: HTML Structure & Tone**\n"
            "Output strictly in raw HTML format (No <html>/<body> tags). Use the following structure guide but keep content dynamic:\n\n"

            f"<h2>بررسی تخصصی و خرید {product_name}</h2>\n"
            "<p>[Write a captivating intro based on the product type. Hook the reader's pain points. Mention why this is a good choice for the target audience.]</p>\n\n"

            "<!-- DYNAMIC SECTION 1: Main Feature -->\n"
            "<h3>[Generate a relevant header, e.g., 'Design', 'Performance', or 'Material']</h3>\n"
            "<p>[Deep dive into this feature. If it's a high-end item, mention build quality. Insert internal links naturally here.]</p>\n\n"

            "<!-- DYNAMIC SECTION 2: Technical Specs / Usage -->\n"
            "<h3>[Generate a relevant header, e.g., 'Technical Specs', 'Compatibility', or 'User Experience']</h3>\n"
            "<ul>\n"
            "  <li><strong>[Feature A]:</strong> [Description relevant to product]</li>\n"
            "  <li><strong>[Feature B]:</strong> [Description relevant to product]</li>\n"
            "  <li><strong>[Feature C]:</strong> [Description relevant to product]</li>\n"
            "</ul>\n\n"

            "<!-- DYNAMIC SECTION 3: Value Proposition -->\n"
            "<h3>ارزش خرید و کاربری</h3>\n"
            "<p>[Discuss who should buy this. Is it for gamers? Office? Industrial use? Explain the value proposition without mentioning warranty.]</p>\n\n"

            f"<h3>چرا {product_name} را از سبحان رایانه بخریم؟</h3>\n"
            "<p>در سبحان رایانه، هدف ما ارائه بهترین تجربه خرید اینترنتی است. مزایای خرید این محصول از ما:</p>\n"
            "<ul>\n"
            "  <li>تضمین سلامت فیزیکی کالا و مهلت تست (Strictly NO warranty mention)</li>\n"
            "  <li>بسته‌بندی حرفه‌ای و ضدضربه برای ارسال ایمن به سراسر کشور</li>\n"
            "  <li>مشاوره تخصصی پیش از خرید</li>\n"
            "  <li>امکان <a href='https://sobhanrayaneh.com/%d9%81%d8%b1%d9%88%d8%b4-%d8%a7%d9%82%d8%b3%d8%a7%d8%b7%db%8c/'>خرید اقساطی</a> برای مدیریت بودجه شما</li>\n"
            "</ul>\n\n"

            "<h3>سوالات متداول (FAQ)</h3>\n"
            "<div class='faq-section'>\n"
            "  <p><strong>[Generate Question 1 relevant to product usage/specs]</strong><br>[Answer]</p>\n"
            "  <p><strong>[Generate Question 2 about shipping or box contents]</strong><br>[Answer]</p>\n"
            "  <p><strong>[Generate Question 3 about compatibility or installation]</strong><br>[Answer]</p>\n"
            "</div>\n\n"

            "**Final Constraints:**\n"
            "- Language: Persian (Farsi).\n"
            "- Tone: Expert, Trustworthy, Persuasive.\n"
            "- **NO Warranty/Guarantee mentions.**\n"
            "- Use proper HTML tags (<h2>, <h3>, <p>, <ul>, <li>, <strong>, <a>)."
        )

        
        return self._send_request(sys, usr)