"""
Translations utility for multilingual PDF generation.
Provides translations for delivery notes in English, Greek, and Arabic.
"""
from flask import g

# Translations dictionary for various languages
TRANSLATIONS = {
    # English translations (default)
    'en': {
        'Delivery Note': 'Delivery Note',
        'Order Number': 'Order Number',
        'Date': 'Date',
        'Customer Details': 'Customer Details',
        'Delivery Details': 'Delivery Details',
        'Customer': 'Customer',
        'Address': 'Address',
        'Phone': 'Phone',
        'Email': 'Email',
        'Status': 'Status',
        'Order Date': 'Order Date',
        'Delivery Date': 'Delivery Date',
        'Order Notes': 'Order Notes',
        'Order Items': 'Order Items',
        'Plant Name': 'Plant Name',
        'Size/Pot': 'Size/Pot',
        'Quantity': 'Quantity',
        'Price': 'Price',
        'Total': 'Total',
        'Delivered By': 'Delivered By',
        'Received By': 'Received By',
        'Name and Signature': 'Name and Signature',
        'Thank you for your business!': 'Thank you for your business!',
        'Questions? Call us at': 'Questions? Call us at',
        'Page': 'Page',
        'of': 'of',
    },
    
    # Greek translations
    'el': {
        'Delivery Note': 'Δελτίο Παράδοσης',
        'Order Number': 'Αριθμός Παραγγελίας',
        'Date': 'Ημερομηνία',
        'Customer Details': 'Στοιχεία Πελάτη',
        'Delivery Details': 'Στοιχεία Παράδοσης',
        'Customer': 'Πελάτης',
        'Address': 'Διεύθυνση',
        'Phone': 'Τηλέφωνο',
        'Email': 'Email',
        'Status': 'Κατάσταση',
        'Order Date': 'Ημερομηνία Παραγγελίας',
        'Delivery Date': 'Ημερομηνία Παράδοσης',
        'Order Notes': 'Σημειώσεις Παραγγελίας',
        'Order Items': 'Προϊόντα Παραγγελίας',
        'Plant Name': 'Όνομα Φυτού',
        'Size/Pot': 'Μέγεθος/Γλάστρα',
        'Quantity': 'Ποσότητα',
        'Price': 'Τιμή',
        'Total': 'Σύνολο',
        'Delivered By': 'Παραδόθηκε Από',
        'Received By': 'Παραλήφθηκε Από',
        'Name and Signature': 'Όνομα και Υπογραφή',
        'Thank you for your business!': 'Ευχαριστούμε για την προτίμησή σας!',
        'Questions? Call us at': 'Έχετε ερωτήσεις; Καλέστε μας στο',
        'Page': 'Σελίδα',
        'of': 'από',
    },
    
    # Arabic translations
    'ar': {
        'Delivery Note': 'مذكرة تسليم',
        'Order Number': 'رقم الطلب',
        'Date': 'تاريخ',
        'Customer Details': 'تفاصيل العميل',
        'Delivery Details': 'تفاصيل التسليم',
        'Customer': 'العميل',
        'Address': 'العنوان',
        'Phone': 'الهاتف',
        'Email': 'البريد الإلكتروني',
        'Status': 'الحالة',
        'Order Date': 'تاريخ الطلب',
        'Delivery Date': 'تاريخ التسليم',
        'Order Notes': 'ملاحظات الطلب',
        'Order Items': 'عناصر الطلب',
        'Plant Name': 'اسم النبات',
        'Size/Pot': 'الحجم/الأصيص',
        'Quantity': 'الكمية',
        'Price': 'السعر',
        'Total': 'المجموع',
        'Delivered By': 'تم التسليم بواسطة',
        'Received By': 'تم الاستلام بواسطة',
        'Name and Signature': 'الاسم والتوقيع',
        'Thank you for your business!': 'شكرا لتعاملك معنا!',
        'Questions? Call us at': 'هل لديك أسئلة؟ اتصل بنا على',
        'Page': 'صفحة',
        'of': 'من',
    }
}

def get_translation(key, language='en'):
    """
    Get translation for a given key in the specified language.
    Falls back to English if translation not found.
    
    Args:
        key: The text key to translate
        language: The language code (en, el, ar)
        
    Returns:
        str: Translated text
    """
    if language not in TRANSLATIONS:
        language = 'en'  # Default to English
        
    translations = TRANSLATIONS[language]
    
    # Return translation if available, otherwise return English or the key itself
    if key in translations:
        return translations[key]
    elif key in TRANSLATIONS['en']:
        return TRANSLATIONS['en'][key]
    else:
        return key  # Return the key itself if no translation found

def setup_jinja_translations(app):
    """
    Set up Jinja environment to use the translation function.
    This makes the translation function available in templates as _().
    
    Args:
        app: Flask application instance
    """
    @app.context_processor
    def inject_translations():
        def translate(text):
            """Translation function for use in templates"""
            # Get language from the g object or default to English
            language = getattr(g, 'language', 'en')
            return get_translation(text, language)
            
        return dict(_=translate)