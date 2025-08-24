let retryCount = 0;
const maxRetries = 10;

function initializeApp() {
    if (window.Telegram && window.Telegram.WebApp) {
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
        initializeTONConnect();
    } else {
        if (retryCount < maxRetries) {
            retryCount++;
            setTimeout(initializeApp, 500); // انتظر نصف ثانية ثم أعد المحاولة
        } else {
            document.body.innerHTML = `
                <div style="font-family: Arial; text-align: center; margin-top: 50px;">
                    <h2>❌ الرجاء فتح هذا التطبيق من داخل تطبيق Telegram فقط</h2>
                </div>
            `;
        }
    }
}

window.addEventListener('load', initializeApp);
