"""
Translation utility for multi-language support in the application.
This module provides functionality to translate content in delivery notes
and other documents to different languages, including Greek and Arabic.
"""
import os
import json
from dataclasses import dataclass
from typing import Dict, Any, Callable


@dataclass
class Translations:
    """
    Translations container that provides methods to access translations
    for a specific language.
    """
    language: str
    translations: Dict[str, str]
    
    def gettext(self, text: str) -> str:
        """
        Get the translation for a given text. If no translation exists,
        return the original text.
        
        Args:
            text: The text to translate
            
        Returns:
            str: The translated text or the original if no translation exists
        """
        return self.translations.get(text, text)


# Dictionary of supported languages and their locale codes
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'el': 'Greek',
    'ar': 'Arabic'
}

# Translation dictionaries for each language
_translations = {
    'en': {},  # English is the default language
    
    'el': {  # Greek translations
        # Order status
        'New': 'Νέα',
        'Preparing': 'Σε προετοιμασία',
        'Ready': 'Έτοιμη',
        'Delivered': 'Παραδόθηκε',
        'Cancelled': 'Ακυρώθηκε',
        
        # Delivery note
        'Delivery Note': 'Δελτίο Παράδοσης',
        'Customer Details': 'Στοιχεία Πελάτη',
        'Customer': 'Πελάτης',
        'Address': 'Διεύθυνση',
        'Phone': 'Τηλέφωνο',
        'Email': 'Email',
        'Delivery Details': 'Στοιχεία Παράδοσης',
        'Status': 'Κατάσταση',
        'Order Date': 'Ημερομηνία Παραγγελίας',
        'Delivery Date': 'Ημερομηνία Παράδοσης',
        'Order Notes': 'Σημειώσεις Παραγγελίας',
        'Order Items': 'Είδη Παραγγελίας',
        'Plant Name': 'Όνομα Φυτού',
        'Size/Pot': 'Μέγεθος/Γλάστρα',
        'Quantity': 'Ποσότητα',
        'Price': 'Τιμή',
        'Total': 'Σύνολο',
        'Delivered By': 'Παραδόθηκε Από',
        'Received By': 'Παραλήφθηκε Από',
        'Name and Signature': 'Όνομα και Υπογραφή',
        'Thank you for your business!': 'Ευχαριστούμε για τη συνεργασία!',
        'Questions? Call us at': 'Ερωτήσεις; Καλέστε μας στο',
        'Page': 'Σελίδα',
        'of': 'από',
        
        # Order dashboard
        'Orders': 'Παραγγελίες',
        'New Order': 'Νέα Παραγγελία',
        'Search': 'Αναζήτηση',
        'Filter': 'Φίλτρο',
        'Reset Filters': 'Επαναφορά Φίλτρων',
        'No orders found.': 'Δεν βρέθηκαν παραγγελίες.',
        'All Statuses': 'Όλες οι Καταστάσεις',
        'All Customers': 'Όλοι οι Πελάτες',
        'From Date': 'Από Ημερομηνία',
        'To Date': 'Έως Ημερομηνία',
        'Apply Filters': 'Εφαρμογή Φίλτρων',
        'Order Number': 'Αριθμός Παραγγελίας',
        'Customer': 'Πελάτης',
        'Items': 'Είδη',
        'Date': 'Ημερομηνία',
        'Status': 'Κατάσταση',
        'Actions': 'Ενέργειες',
        'View': 'Προβολή',
        'Edit': 'Επεξεργασία',
        'Delete': 'Διαγραφή',
        'Order Details': 'Λεπτομέρειες Παραγγελίας',
        'Edit Order': 'Επεξεργασία Παραγγελίας',
        'Add Item': 'Προσθήκη Είδους',
        'Save Changes': 'Αποθήκευση Αλλαγών',
        'Cancel': 'Ακύρωση',
    },
    
    'ar': {  # Arabic translations
        # Order status
        'New': 'جديدة',
        'Preparing': 'قيد التحضير',
        'Ready': 'جاهزة',
        'Delivered': 'تم التسليم',
        'Cancelled': 'ملغاة',
        
        # Delivery note
        'Delivery Note': 'مذكرة التسليم',
        'Customer Details': 'تفاصيل العميل',
        'Customer': 'العميل',
        'Address': 'العنوان',
        'Phone': 'الهاتف',
        'Email': 'البريد الإلكتروني',
        'Delivery Details': 'تفاصيل التسليم',
        'Status': 'الحالة',
        'Order Date': 'تاريخ الطلب',
        'Delivery Date': 'تاريخ التسليم',
        'Order Notes': 'ملاحظات الطلب',
        'Order Items': 'عناصر الطلب',
        'Plant Name': 'اسم النبات',
        'Size/Pot': 'الحجم/الوعاء',
        'Quantity': 'الكمية',
        'Price': 'السعر',
        'Total': 'المجموع',
        'Delivered By': 'تم التسليم بواسطة',
        'Received By': 'تم الاستلام بواسطة',
        'Name and Signature': 'الاسم والتوقيع',
        'Thank you for your business!': 'شكرا لتعاملك معنا!',
        'Questions? Call us at': 'أسئلة؟ اتصل بنا على',
        'Page': 'صفحة',
        'of': 'من',
        
        # Order dashboard
        'Orders': 'الطلبات',
        'New Order': 'طلب جديد',
        'Search': 'بحث',
        'Filter': 'تصفية',
        'Reset Filters': 'إعادة تعيين المرشحات',
        'No orders found.': 'لم يتم العثور على طلبات.',
        'All Statuses': 'جميع الحالات',
        'All Customers': 'جميع العملاء',
        'From Date': 'من تاريخ',
        'To Date': 'إلى تاريخ',
        'Apply Filters': 'تطبيق المرشحات',
        'Order Number': 'رقم الطلب',
        'Customer': 'العميل',
        'Items': 'العناصر',
        'Date': 'التاريخ',
        'Status': 'الحالة',
        'Actions': 'الإجراءات',
        'View': 'عرض',
        'Edit': 'تعديل',
        'Delete': 'حذف',
        'Order Details': 'تفاصيل الطلب',
        'Edit Order': 'تعديل الطلب',
        'Add Item': 'إضافة عنصر',
        'Save Changes': 'حفظ التغييرات',
        'Cancel': 'إلغاء',
    }
}


def get_translations(language: str = 'en') -> Translations:
    """
    Get translations for the specified language.
    
    Args:
        language: Language code (e.g., 'en', 'el', 'ar')
        
    Returns:
        Translations: Translations instance for the specified language
    """
    if language not in SUPPORTED_LANGUAGES:
        language = 'en'  # Fallback to English if language not supported
    
    return Translations(
        language=language,
        translations=_translations.get(language, {})
    )


def add_translation(language: str, key: str, value: str) -> bool:
    """
    Add a new translation to the specified language.
    
    Args:
        language: Language code (e.g., 'en', 'el', 'ar')
        key: The original text to translate
        value: The translated text
        
    Returns:
        bool: True if the translation was added successfully, False otherwise
    """
    if language not in SUPPORTED_LANGUAGES:
        return False
    
    _translations.setdefault(language, {})[key] = value
    return True


def save_translations_to_file(filepath: str) -> bool:
    """
    Save all translations to a JSON file.
    
    Args:
        filepath: Path to the file to save translations to
        
    Returns:
        bool: True if the translations were saved successfully, False otherwise
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(_translations, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving translations: {e}")
        return False


def load_translations_from_file(filepath: str) -> bool:
    """
    Load translations from a JSON file.
    
    Args:
        filepath: Path to the file to load translations from
        
    Returns:
        bool: True if the translations were loaded successfully, False otherwise
    """
    global _translations
    
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded_translations = json.load(f)
                
                # Update existing translations with loaded ones
                for lang, trans in loaded_translations.items():
                    if lang in SUPPORTED_LANGUAGES:
                        _translations.setdefault(lang, {}).update(trans)
            return True
        return False
    except Exception as e:
        print(f"Error loading translations: {e}")
        return False