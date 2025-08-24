let telegramWebApp = null;
let walletAddress = null;

// التحقق من وجود Telegram WebApp
function isTelegramEnvironment() {
    return (window.Telegram && 
            window.Telegram.WebApp && 
            window.Telegram.WebApp.initData);
}

// تهيئة التطبيق
function initializeApp() {
    if (isTelegramEnvironment()) {
        telegramWebApp = window.Telegram.WebApp;
        document.getElementById('app-container').style.display = 'block';
        document.getElementById('telegram-error').style.display = 'none';
        
        // تهيئة Telegram WebApp
        telegramWebApp.ready();
        telegramWebApp.expand();
        
        // إعداد event listeners
        setupEventListeners();
        
        // محاولة الات التلقائي بالمحفظة إذا كانت متاحة
        checkWalletAvailability();
        
    } else {
        document.getElementById('app-container').style.display = 'none';
        document.getElementById('telegram-error').style.display = 'block';
    }
}

// إعداد event listeners
function setupEventListeners() {
    document.getElementById('init-wallet').addEventListener('click', initializeWallet);
    document.getElementById('send-ton').addEventListener('click', sendTon);
    document.getElementById('receive-ton').addEventListener('click', receiveTon);
}

// التحقق من توفر المحفظة
function checkWalletAvailability() {
    if (telegramWebApp && telegramWebApp.isVersionAtLeast('6.10')) {
        document.getElementById('wallet-status').textContent = 'حالة المحفظة: جاهزة';
        document.getElementById('init-wallet').disabled = false;
    } else {
        document.getElementById('wallet-status').textContent = 'حالة المحفظة: غير مدعومة في إصدارك';
        document.getElementById('init-wallet').disabled = true;
    }
}

// تهيئة المحفظة
function initializeWallet() {
    if (!telegramWebApp) return;
    
    try {
        // استخدام Telegram Wallet API
        telegramWebApp.openInvoice('https://t.me/wallet/start?startapp=SYRX', {
            onInvoiceClosed: function(invoiceStatus) {
                if (invoiceStatus === 'paid') {
                    document.getElementById('wallet-status').textContent = 'حالة المحفظة: موصولة';
                    document.getElementById('send-ton').disabled = false;
                    fetchWalletInfo();
                }
            }
        });
        
    } catch (error) {
        document.getElementById('transaction-status').textContent = 'خطأ: ' + error.message;
    }
}

// جلب معلومات المحفظة
async function fetchWalletInfo() {
    try {
        // هنا يمكنك استخدام Telegram Wallet API للحصول على المعلومات
        document.getElementById('wallet-address').textContent = 'العنوان: جاري التحميل...';
        document.getElementById('balance').textContent = 'الرصيد: جاري التحميل...';
        
        // محاكاة للحصول على البيانات (ستحتاج لاستبدالها بـ API حقيقي)
        setTimeout(() => {
            document.getElementById('wallet-address').textContent = 'العنوان: EQ...1234';
            document.getElementById('balance').textContent = 'الرصيد: 10.5 TON';
        }, 1000);
        
    } catch (error) {
        document.getElementById('transaction-status').textContent = 'خطأ في جلب المعلومات';
    }
}

// إرسال TON
async function sendTon() {
    if (!telegramWebApp) return;
    
    try {
        document.getElementById('transaction-status').textContent = 'جاري إعداد المعاملة...';
        
        // استخدام Telegram Wallet API لإرسال المعاملة
        const transaction = {
            to: 'EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c',
            amount: '1000000000', // 1 TON في nanoTON
            comment: 'Payment from SYRX App'
        };
        
        telegramWebApp.openInvoice(`https://t.me/wallet/send?to=${transaction.to}&amount=${transaction.amount}`, {
            onInvoiceClosed: function(status) {
                if (status === 'paid') {
                    document.getElementById('transaction-status').textContent = 'تم إرسال 1 TON بنجاح!';
                    fetchWalletInfo(); // تحديث الرصيد
                } else {
                    document.getElementById('transaction-status').textContent = 'تم إلغاء المعاملة';
                }
            }
        });
        
    } catch (error) {
        document.getElementById('transaction-status').textContent = 'خطأ: ' + error.message;
    }
}

// استقبال TON
function receiveTon() {
    if (!walletAddress) {
        document.getElementById('transaction-status').textContent = 'يجب توصيل المحفظة أولاً';
        return;
    }
    
    // عرض عنوان المحفظة للاستقبال
    telegramWebApp.showPopup({
        title: 'عنوان استقبال TON',
        message: `استخدم هذا العنوان لاستقبال TON:\n${walletAddress}`,
        buttons: [{ type: 'ok' }]
    });
    
    document.getElementById('transaction-status').textContent = 'عرض عنوان الاستقبال';
}

// تهيئة التطبيق عند التحميل
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initializeApp, 100);
});
