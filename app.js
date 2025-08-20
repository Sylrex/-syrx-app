// TonConnect
const tonConnect = new TonConnect.TonConnect({bridgeUrl: "https://bridge.tonapi.io"});
let walletAddress = "";

// Mock user (سوف نستبدلها بعد تسجيل دخول Telegram)
let telegramId = "123456";
let playerName = "Guest";
let playerPoints = 0;
let referralCode = "-";

// Navigation
document.querySelectorAll('.tab').forEach(tab=>{
    tab.addEventListener('click', ()=>{
        document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
        tab.classList.add('active');
        document.querySelectorAll('.page').forEach(p=>p.classList.add('hidden'));
        document.getElementById(tab.dataset.tab).classList.remove('hidden');
    });
});

// Connect TON Wallet
document.getElementById('connectWalletBtn').addEventListener('click', async ()=>{
    try {
        const wallet = await tonConnect.requestWallet();
        walletAddress = wallet.account.address;
        alert("✅ Connected: " + walletAddress);
        fetch('/api/update',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({telegram_id:telegramId,wallet_address:walletAddress,points:playerPoints})
        });
    } catch(e){
        alert("❌ Wallet connection failed");
    }
});

// Mock tasks
const tasks = [
    {id:1,title:"📱 Join Telegram",url:"https://t.me/SylrexOfficial",reward:100},
    {id:2,title:"🐦 Follow on X",url:"https://x.com/SylrexOfficial?t=xMY6eEauM0DXY5VllXdT-w&s=09",reward:120},
    {id:3,title:"📺 Subscribe YouTube 1",url:"https://www.youtube.com/@Sylrex_Official",reward:80},
    {id:4,title:"📺 Subscribe YouTube 2",url:"https://www.youtube.com/@SylrexOfficial",reward:80},
    {id:5,title:"📘 Like Facebook",url:"https://www.facebook.com/share/1JYzm6CGsS/",reward:90}
];

// Render tasks
function renderTasks(){
    const container = document.getElementById('taskList');
    container.innerHTML = "";
    tasks.forEach(t=>{
        const div = document.createElement('div');
        div.className = "task-item";
        div.innerHTML = `<div class="task-info">${t.title} <div class="task-reward">+${t.reward}</div></div>
            <button class="btn" onclick="completeTask(${t.id})">▶️ Start</button>`;
        container.appendChild(div);
    });
}

// Complete task
function completeTask(taskId){
    const task = tasks.find(t=>t.id===taskId);
    if(!task) return;
    fetch('/api/complete-task',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({telegram_id:telegramId,task_name:task.title,reward:task.reward})
    }).then(res=>res.json()).then(data=>{
        if(data.success){
            playerPoints = data.points;
            document.getElementById('playerPoints').textContent = playerPoints;
            alert(`🎉 Task completed! +${task.reward} points`);
        }
    });
}

renderTasks();
document.getElementById('playerName').textContent = playerName;
document.getElementById('playerPoints').textContent = playerPoints;
document.getElementById('playerReferral').textContent = referralCode;
