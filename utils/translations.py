"""
Translations module for multilingual delivery notes
Supports English, Greek, and Arabic translations
"""

# Dictionary of translations keyed by language code
TRANSLATIONS = {
    'en': {  # English (default)
        'delivery_note': 'Delivery Note',
        'order_number': 'Order Number',
        'date': 'Date',
        'customer': 'Customer',
        'delivery_date': 'Delivery Date',
        'item': 'Item',
        'quantity': 'Quantity',
        'unit_price': 'Unit Price',
        'total': 'Total',
        'notes': 'Notes',
        'subtotal': 'Subtotal',
        'vat': 'VAT',
        'grand_total': 'Grand Total',
        'thank_you': 'Thank you for your business!',
        'signature': 'Signature',
        'status': 'Status',
        'prepared_by': 'Prepared By',
        'received_by': 'Received By',
        'page': 'Page',
        'of': 'of'
    },
    'el': {  # Greek
        'delivery_note': 'Δελτίο Παράδοσης',
        'order_number': 'Αριθμός Παραγγελίας',
        'date': 'Ημερομηνία',
        'customer': 'Πελάτης',
        'delivery_date': 'Ημερομηνία Παράδοσης',
        'item': 'Είδος',
        'quantity': 'Ποσότητα',
        'unit_price': 'Τιμή Μονάδας',
        'total': 'Σύνολο',
        'notes': 'Σημειώσεις',
        'subtotal': 'Μερικό Σύνολο',
        'vat': 'ΦΠΑ',
        'grand_total': 'Τελικό Σύνολο',
        'thank_you': 'Ευχαριστούμε για τη συνεργασία!',
        'signature': 'Υπογραφή',
        'status': 'Κατάσταση',
        'prepared_by': 'Συντάχθηκε από',
        'received_by': 'Παραλήφθηκε από',
        'page': 'Σελίδα',
        'of': 'από'
    },
    'ar': {  # Arabic
        'delivery_note': 'مذكرة تسليم',
        'order_number': 'رقم الطلب',
        'date': 'تاريخ',
        'customer': 'عميل',
        'delivery_date': 'تاريخ التسليم',
        'item': 'بند',
        'quantity': 'كمية',
        'unit_price': 'سعر الوحدة',
        'total': 'مجموع',
        'notes': 'ملاحظات',
        'subtotal': 'المجموع الفرعي',
        'vat': 'ضريبة القيمة المضافة',
        'grand_total': 'المبلغ الإجمالي',
        'thank_you': 'شكرا لعملك!',
        'signature': 'التوقيع',
        'status': 'حالة',
        'prepared_by': 'أعدها',
        'received_by': 'استلمت من قبل',
        'page': 'صفحة',
        'of': 'من'
    }
}

# Status translations
STATUS_TRANSLATIONS = {
    'en': {  # English
        'new': 'New',
        'preparing': 'Preparing',
        'ready': 'Ready for Delivery',
        'delivered': 'Delivered',
        'cancelled': 'Cancelled'
    },
    'el': {  # Greek
        'new': 'Νέα',
        'preparing': 'Σε προετοιμασία',
        'ready': 'Έτοιμο για παράδοση',
        'delivered': 'Παραδόθηκε',
        'cancelled': 'Ακυρώθηκε'
    },
    'ar': {  # Arabic
        'new': 'جديد',
        'preparing': 'تحضير',
        'ready': 'جاهز للتسليم',
        'delivered': 'تم التسليم',
        'cancelled': 'ألغيت'
    }
}

def translate_to_language(key, language='en'):
    """
    Translate a key to the specified language
    
    Args:
        key (str): The key to translate
        language (str): Language code ('en', 'el', 'ar')
        
    Returns:
        str: Translated text or the key itself if not found
    """
    if language not in TRANSLATIONS:
        language = 'en'  # Default to English
        
    return TRANSLATIONS[language].get(key, key)

def translate_status(status, language='en'):
    """
    Translate an order status to the specified language
    
    Args:
        status (str): The status value to translate
        language (str): Language code ('en', 'el', 'ar')
        
    Returns:
        str: Translated status or the status itself if not found
    """
    if language not in STATUS_TRANSLATIONS:
        language = 'en'  # Default to English
        
    return STATUS_TRANSLATIONS[language].get(status, status)