"""
Translation utilities for multi-language support
Supports English, Greek, and Arabic
"""

# English translations (default)
EN_TRANSLATIONS = {
    # General
    'Company Name': 'Company Name',
    'Address Line 1': 'Address Line 1',
    'City, Postal Code': 'City, Postal Code',
    'Phone': 'Phone',
    'Email': 'Email',
    
    # Document title
    'DELIVERY NOTE': 'DELIVERY NOTE',
    'Delivery Note': 'Delivery Note',
    
    # Sections
    'Order Information': 'Order Information',
    'Customer Information': 'Customer Information',
    'Order Items': 'Order Items',
    'Notes': 'Notes',
    
    # Order info
    'Order Number': 'Order Number',
    'Order Date': 'Order Date',
    'Delivery Date': 'Delivery Date',
    'Not specified': 'Not specified',
    
    # Customer info
    'Customer': 'Customer',
    'Address': 'Address',
    'N/A': 'N/A',
    
    # Items table
    'Product/Plant': 'Product/Plant',
    'Quantity': 'Quantity',
    'Notes': 'Notes',
    
    # Signatures
    'Delivered By (Signature & Name)': 'Delivered By (Signature & Name)',
    'Received By (Signature & Name)': 'Received By (Signature & Name)',
    
    # Footer
    'Thank you for your business! This delivery note is not an invoice.': 'Thank you for your business! This delivery note is not an invoice.'
}

# Greek translations
EL_TRANSLATIONS = {
    # General
    'Company Name': 'Επωνυμία Εταιρείας',
    'Address Line 1': 'Διεύθυνση Γραμμή 1',
    'City, Postal Code': 'Πόλη, ΤΚ',
    'Phone': 'Τηλέφωνο',
    'Email': 'Email',
    
    # Document title
    'DELIVERY NOTE': 'ΔΕΛΤΙΟ ΑΠΟΣΤΟΛΗΣ',
    'Delivery Note': 'Δελτίο Αποστολής',
    
    # Sections
    'Order Information': 'Πληροφορίες Παραγγελίας',
    'Customer Information': 'Στοιχεία Πελάτη',
    'Order Items': 'Είδη Παραγγελίας',
    'Notes': 'Σημειώσεις',
    
    # Order info
    'Order Number': 'Αριθμός Παραγγελίας',
    'Order Date': 'Ημερομηνία Παραγγελίας',
    'Delivery Date': 'Ημερομηνία Παράδοσης',
    'Not specified': 'Δεν καθορίστηκε',
    
    # Customer info
    'Customer': 'Πελάτης',
    'Address': 'Διεύθυνση',
    'N/A': 'Μ/Δ',
    
    # Items table
    'Product/Plant': 'Προϊόν/Φυτό',
    'Quantity': 'Ποσότητα',
    
    # Signatures
    'Delivered By (Signature & Name)': 'Παραδόθηκε Από (Υπογραφή & Όνομα)',
    'Received By (Signature & Name)': 'Παρελήφθη Από (Υπογραφή & Όνομα)',
    
    # Footer
    'Thank you for your business! This delivery note is not an invoice.': 'Σας ευχαριστούμε για τη συνεργασία! Αυτό το δελτίο αποστολής δεν είναι τιμολόγιο.'
}

# Arabic translations
AR_TRANSLATIONS = {
    # General
    'Company Name': 'اسم الشركة',
    'Address Line 1': 'العنوان سطر 1',
    'City, Postal Code': 'المدينة، الرمز البريدي',
    'Phone': 'هاتف',
    'Email': 'بريد إلكتروني',
    
    # Document title
    'DELIVERY NOTE': 'مذكرة تسليم',
    'Delivery Note': 'مذكرة تسليم',
    
    # Sections
    'Order Information': 'معلومات الطلب',
    'Customer Information': 'معلومات العميل',
    'Order Items': 'عناصر الطلب',
    'Notes': 'ملاحظات',
    
    # Order info
    'Order Number': 'رقم الطلب',
    'Order Date': 'تاريخ الطلب',
    'Delivery Date': 'تاريخ التسليم',
    'Not specified': 'غير محدد',
    
    # Customer info
    'Customer': 'العميل',
    'Address': 'العنوان',
    'N/A': 'غير متوفر',
    
    # Items table
    'Product/Plant': 'المنتج/النبات',
    'Quantity': 'الكمية',
    
    # Signatures
    'Delivered By (Signature & Name)': 'تم التسليم بواسطة (التوقيع والاسم)',
    'Received By (Signature & Name)': 'تم الاستلام بواسطة (التوقيع والاسم)',
    
    # Footer
    'Thank you for your business! This delivery note is not an invoice.': 'شكرًا لتعاملك معنا! مذكرة التسليم هذه ليست فاتورة.'
}

# Translation dictionaries by language code
TRANSLATIONS = {
    'en': EN_TRANSLATIONS,
    'el': EL_TRANSLATIONS,
    'ar': AR_TRANSLATIONS
}

def get_translations(language_code='en'):
    """
    Get a translation function for the specified language
    
    Args:
        language_code (str): Language code ('en', 'el', 'ar')
        
    Returns:
        function: Translation function that takes a string and returns its translation
    """
    # Get the translation dictionary for the requested language
    # Fallback to English if the language is not supported
    translations = TRANSLATIONS.get(language_code, EN_TRANSLATIONS)
    
    # Create and return a translation function
    def translate(text):
        """Translate a string to the selected language"""
        return translations.get(text, text)
    
    return translate