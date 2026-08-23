// Common Utility Functions
function checkAuth() {
    const userId = localStorage.getItem('userId');
    if (!userId && window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
        return false;
    }
    return true;
}

async function logout() {
    try {
        await fetch('/api/logout', { method: 'POST' });
    } catch (e) {
        console.error(e);
    }
    localStorage.removeItem('userId');
    localStorage.removeItem('userName');
    window.location.href = '/login';
}

// Authentication Forms
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();
            
            if (res.ok) {
                localStorage.setItem('userId', data.userId);
                localStorage.setItem('userName', data.name);
                window.location.href = '/dashboard';
            } else {
                document.getElementById('authError').textContent = data.error || 'Login failed';
            }
        } catch (err) {
            document.getElementById('authError').textContent = 'Network error';
        }
    });
}

const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('regName').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;
        const confirm = document.getElementById('regConfirmPassword').value;
        
        if (password !== confirm) {
            document.getElementById('authError').textContent = 'Passwords do not match';
            return;
        }
        
        try {
            const res = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            });
            const data = await res.json();
            
            if (res.ok) {
                window.location.href = '/login';
            } else {
                document.getElementById('authError').textContent = data.error || 'Registration failed';
            }
        } catch (err) {
            document.getElementById('authError').textContent = 'Network error';
        }
    });
}

// Dashboard Functions
async function loadVideos() {
    try {
        const res = await fetch('/api/videos');
        if (res.status === 401) { logout(); return; }
        
        const data = await res.json();
        if (res.ok) {
            const tbody = document.getElementById('videoTableBody');
            tbody.innerHTML = '';
            
            data.videos.forEach(v => {
                const tr = document.createElement('tr');
                let actionBtn = `<a href="/result/${v.videoId}" class="btn btn-sm btn-primary">View</a>`;
                
                tr.innerHTML = `
                    <td>${v.fileName}</td>
                    <td>${v.language}</td>
                    <td>${v.status}</td>
                    <td>${actionBtn}</td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) {
        console.error('Error loading videos', err);
    }
}

// Upload Functions
async function handleUpload(e) {
    e.preventDefault();
    const file = document.getElementById('videoFile').files[0];
    const lang = document.getElementById('language').value;
    const btn = document.getElementById('uploadBtn');
    const statusMsg = document.getElementById('uploadStatus');
    
    if (!file) return;
    
    btn.disabled = true;
    btn.textContent = 'Uploading...';
    statusMsg.textContent = 'Uploading video to server...';
    
    const formData = new FormData();
    formData.append('video', file);
    formData.append('language', lang);
    
    try {
        const res = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (res.status === 401) { logout(); return; }
        
        const data = await res.json();
        if (res.ok) {
            window.location.href = `/result/${data.videoId}`;
        } else {
            statusMsg.textContent = data.error || 'Upload failed';
            statusMsg.style.color = 'red';
            btn.disabled = false;
            btn.textContent = 'Upload & Process';
        }
    } catch (err) {
        statusMsg.textContent = 'Network error';
        statusMsg.style.color = 'red';
        btn.disabled = false;
        btn.textContent = 'Upload & Process';
    }
}

// Result Functions
let pollingInterval;

async function startPollingStatus(videoId) {
    await fetchVideoInfo(videoId);
    await fetchStatus(videoId);
    
    pollingInterval = setInterval(async () => {
        await fetchStatus(videoId);
    }, 5000);
}

async function fetchVideoInfo(videoId) {
    try {
        const res = await fetch(`/api/video/${videoId}`);
        if (res.status === 401) { logout(); return; }
        
        if (res.ok) {
            const data = await res.json();
            document.getElementById('videoInfo').innerHTML = `
                <p><strong>Original File:</strong> ${data.fileName}</p>
                <p><strong>Language:</strong> ${data.language}</p>
                <p><strong>Status:</strong> <span id="currentStatus">${data.status}</span></p>
            `;
        }
    } catch (e) { console.error(e); }
}

async function fetchStatus(videoId) {
    try {
        const res = await fetch(`/api/status/${videoId}`);
        if (res.status === 401) { logout(); return; }
        
        if (res.ok) {
            const data = await res.json();
            const list = document.getElementById('logList');
            list.innerHTML = '';
            
            data.logs.forEach(log => {
                const li = document.createElement('li');
                li.textContent = `${log.processingStage} - ${log.message}`;
                if (log.status === 'FAILED') li.className = 'error';
                list.appendChild(li);
            });
            
            const curStatus = document.getElementById('currentStatus');
            if (curStatus) curStatus.textContent = data.status;
            
            if (data.status === 'COMPLETED') {
                clearInterval(pollingInterval);
                document.getElementById('downloadSection').style.display = 'block';
            } else if (data.status === 'ERROR') {
                clearInterval(pollingInterval);
            }
        }
    } catch (e) { console.error(e); }
}

async function downloadVideo(videoId) {
    try {
        const res = await fetch(`/api/download/${videoId}`);
        if (res.status === 401) { logout(); return; }
        
        if (res.ok) {
            const data = await res.json();
            const a = document.createElement('a');
            a.href = data.downloadUrl;
            a.download = true;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } else {
            alert('Failed to get download link');
        }
    } catch (e) {
        alert('Network error');
    }
}
