"""
Translations utility for multilingual support
Provides translations for delivery notes and other documents in English, Greek, and Arabic.
"""

# Translation dictionaries for different languages
TRANSLATIONS = {
    'en': {
        'delivery_note': 'Delivery Note',
        'order_number': 'Order Number',
        'date': 'Date',
        'customer': 'Customer',
        'delivery_address': 'Delivery Address',
        'item': 'Item',
        'description': 'Description',
        'quantity': 'Quantity',
        'unit': 'Unit',
        'price': 'Price',
        'total': 'Total',
        'subtotal': 'Subtotal',
        'vat': 'VAT',
        'grand_total': 'Grand Total',
        'notes': 'Notes',
        'signature': 'Signature',
        'thank_you': 'Thank you for your business!'
    },
    'el': {
        'delivery_note': 'Δελτίο Αποστολής',
        'order_number': 'Αριθμός Παραγγελίας',
        'date': 'Ημερομηνία',
        'customer': 'Πελάτης',
        'delivery_address': 'Διεύθυνση Παράδοσης',
        'item': 'Είδος',
        'description': 'Περιγραφή',
        'quantity': 'Ποσότητα',
        'unit': 'Μονάδα',
        'price': 'Τιμή',
        'total': 'Σύνολο',
        'subtotal': 'Μερικό Σύνολο',
        'vat': 'ΦΠΑ',
        'grand_total': 'Γενικό Σύνολο',
        'notes': 'Σημειώσεις',
        'signature': 'Υπογραφή',
        'thank_you': 'Ευχαριστούμε για τη συνεργασία!'
    },
    'ar': {
        'delivery_note': 'مذكرة تسليم',
        'order_number': 'رقم الطلب',
        'date': 'التاريخ',
        'customer': 'العميل',
        'delivery_address': 'عنوان التسليم',
        'item': 'البند',
        'description': 'الوصف',
        'quantity': 'الكمية',
        'unit': 'الوحدة',
        'price': 'السعر',
        'total': 'المجموع',
        'subtotal': 'المجموع الفرعي',
        'vat': 'ضريبة القيمة المضافة',
        'grand_total': 'المجموع الكلي',
        'notes': 'ملاحظات',
        'signature': 'التوقيع',
        'thank_you': 'شكرا لعملك!'
    }
}

def get_translations(language='en'):
    """
    Get a dictionary of translations for the specified language
    
    Args:
        language (str): Language code ('en', 'el', 'ar')
        
    Returns:
        dict: Dictionary of translations
    """
    if language not in TRANSLATIONS:
        language = 'en'  # Fallback to English
    
    return TRANSLATIONS[language]

def translate_to_language(text, language='en'):
    """
    Translate a specific text key to the given language
    
    Args:
        text (str): The text key to translate
        language (str): Language code ('en', 'el', 'ar')
        
    Returns:
        str: The translated text
    """
    translations = get_translations(language)
    return translations.get(text, text)  # Fallback to the original text if no translation