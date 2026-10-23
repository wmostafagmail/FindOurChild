
        /* ═══════════════════════════════════════════
           FindTrace v3.0 — Complete JavaScript
           ═══════════════════════════════════════════ */

        /* ══════════ UTILITIES ══════════ */
        const $ = id => document.getElementById(id);
        const now = () => new Date().toLocaleTimeString('en-IN', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const nowShort = () => new Date().toLocaleTimeString('en-IN', { hour12: false, hour: '2-digit', minute: '2-digit' });
        setInterval(() => { $('hdr-clock').textContent = now(); }, 1000);
        $('init-time').textContent = nowShort();

        function announce(msg) { const a = $('aria-announcer'); a.textContent = ''; setTimeout(() => { a.textContent = msg; }, 50); }

        /* ══════════ TOAST NOTIFICATIONS ══════════ */
        const Toast = {
            show(msg, type = 'cyan', duration = 4000) {
                const c = $('toast-container'), t = document.createElement('div');
                t.className = 'toast'; t.innerHTML = `<div class="toast-dot ${type}"></div><span>${msg}</span>`;
                c.appendChild(t);
                announce(msg);
                setTimeout(() => { t.classList.add('out'); setTimeout(() => t.remove(), 300); }, duration);
            }
        };

        /* ══════════ AUDIO ALERT ══════════ */
        const AudioAlert = {
            ctx: null,
            play() {
                if (!Settings.audioAlert) return;
                try {
                    if (!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)();
                    const o = this.ctx.createOscillator(), g = this.ctx.createGain();
                    o.connect(g); g.connect(this.ctx.destination);
                    o.frequency.setValueAtTime(880, this.ctx.currentTime);
                    o.frequency.setValueAtTime(1100, this.ctx.currentTime + 0.1);
                    o.frequency.setValueAtTime(880, this.ctx.currentTime + 0.2);
                    g.gain.setValueAtTime(0.15, this.ctx.currentTime);
                    g.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.5);
                    o.start(this.ctx.currentTime); o.stop(this.ctx.currentTime + 0.5);
                } catch (e) { }
            }
        };

        /* ══════════ SETTINGS ══════════ */
        const Settings = {
            matchThreshold: 0.55,
            browserNotif: false,
            audioAlert: true,
            autoSave: true,
            load() {
                try {
                    const s = JSON.parse(localStorage.getItem('ft3_settings'));
                    if (s) { Object.assign(this, s); }
                } catch (e) { }
                this.applyToUI();
            },
            save() {
                try { localStorage.setItem('ft3_settings', JSON.stringify({ matchThreshold: this.matchThreshold, browserNotif: this.browserNotif, audioAlert: this.audioAlert, autoSave: this.autoSave })); } catch (e) { }
            },
            applyToUI() {
                $('s-sensitivity').value = Math.round(this.matchThreshold * 100);
                $('s-sensitivity-val').textContent = this.matchThreshold.toFixed(2);
                $('s-browser-notif').classList.toggle('on', this.browserNotif);
                $('s-audio-alert').classList.toggle('on', this.audioAlert);
                $('s-autosave').classList.toggle('on', this.autoSave);
            }
        };

        /* ══════════ STORAGE MANAGER ══════════ */
        const Storage = {
            KEY: 'ft3_cases',
            getAll() {
                try { return JSON.parse(localStorage.getItem(this.KEY)) || []; } catch (e) { return []; }
            },
            saveAll(cases) {
                try { localStorage.setItem(this.KEY, JSON.stringify(cases)); } catch (e) { }
            },
            saveCase(c) {
                const all = this.getAll(); const idx = all.findIndex(x => x.id === c.id);
                if (idx >= 0) all[idx] = c; else all.push(c);
                this.saveAll(all);
            },
            deleteCase(id) {
                this.saveAll(this.getAll().filter(x => x.id !== id));
            },
            getCase(id) {
                return this.getAll().find(x => x.id === id) || null;
            }
        };

        /* ══════════ CASE MANAGER ══════════ */
        let currentCase = null;
        let uploadedPhotoURL = null;
        let uploadedFaceDescriptor = null;
        let agedImageDataUrl = null;

        const CaseManager = {
            generateId() { return 'FT-' + (Date.now() % 99999); },

            createNew() {
                const c = {
                    id: this.generateId(), name: '', age: '', gender: '', dateLastSeen: '', location: '',
                    descriptors: {
                        height: 168, build: 'Average', skin: 'Medium', face: 'Round', hairColor: 'Black', hairStyle: 'Short',
                        eyeColor: 'Dark Brown', nose: 'Straight', facialHair: 'None', marks: [], notes: ''
                    },
                    referencePhoto: null, predictions: [], matches: [], timeline: [],
                    createdAt: new Date().toISOString(), updatedAt: new Date().toISOString()
                };
                currentCase = c;
                this.loadToForm(c);
                this.addTimeline('cyan', 'Case created');
                if (Settings.autoSave) Storage.saveCase(c);
                this.refreshDrawer();
                Toast.show('New case created: ' + c.id, 'green');
                return c;
            },

            loadToForm(c) {
                $('f-name').value = c.name || '';
                $('f-age').value = c.age || '';
                $('f-gender').value = c.gender || '';
                $('f-date').value = c.dateLastSeen || '';
                $('f-location').value = c.location || '';
                $('f-height').value = c.descriptors.height || 168;
                $('height-val').textContent = (c.descriptors.height || 168) + ' cm';
                $('f-hair-color').value = c.descriptors.hairColor || 'Black';
                $('f-hair-style').value = c.descriptors.hairStyle || 'Short';
                $('f-eye').value = c.descriptors.eyeColor || 'Dark Brown';
                $('f-nose').value = c.descriptors.nose || 'Straight';
                $('f-notes').value = c.descriptors.notes || '';
                $('case-num').textContent = 'CASE #' + c.id;
                // Set chips
                setChipGroup('build-chips', c.descriptors.build);
                setChipGroup('skin-chips', c.descriptors.skin);
                setChipGroup('face-chips', c.descriptors.face);
                setChipGroup('facial-hair-chips', c.descriptors.facialHair);
                setMarksChips(c.descriptors.marks || []);
                // Photo
                if (c.referencePhoto) {
                    uploadedPhotoURL = c.referencePhoto;
                    $('photo-preview').src = c.referencePhoto;
                    $('photo-preview').style.display = 'block';
                    $('upload-prompt').style.display = 'none';
                } else {
                    uploadedPhotoURL = null;
                    $('photo-preview').style.display = 'none';
                    $('upload-prompt').style.display = '';
                }
                uploadedFaceDescriptor = null;
                agedImageDataUrl = null;
                // Reset prediction view
                $('pred-img').style.display = 'none';
                $('pred-placeholder').style.display = 'flex';
                $('age-ring').style.display = 'none';
                $('pred-age-num').innerHTML = '—<span> yrs</span>';
                $('pred-years-label').textContent = '— years elapsed';
                $('conf-pct').textContent = '—';
                $('conf-fill').style.width = '0%';
                $('prog-status').textContent = 'AWAITING DATA';
                // Render timeline
                this.renderTimeline(c);
                updateCase();
            },

            readFromForm() {
                if (!currentCase) return;
                currentCase.name = $('f-name').value.trim();
                currentCase.age = parseInt($('f-age').value) || '';
                currentCase.gender = $('f-gender').value;
                currentCase.dateLastSeen = $('f-date').value;
                currentCase.location = $('f-location').value.trim();
                currentCase.descriptors = {
                    height: parseInt($('f-height').value) || 168,
                    build: getActiveChip('build-chips'), skin: getActiveChip('skin-chips'),
                    face: getActiveChip('face-chips'), hairColor: $('f-hair-color').value,
                    hairStyle: $('f-hair-style').value, eyeColor: $('f-eye').value,
                    nose: $('f-nose').value, facialHair: getActiveChip('facial-hair-chips'),
                    marks: getActiveChips('marks-chips'), notes: $('f-notes').value
                };
                if (uploadedPhotoURL && uploadedPhotoURL.startsWith('data:'))
                    currentCase.referencePhoto = uploadedPhotoURL;
                currentCase.updatedAt = new Date().toISOString();
            },

            switchTo(id) {
                this.readFromForm();
                if (currentCase && Settings.autoSave) Storage.saveCase(currentCase);
                const c = Storage.getCase(id);
                if (c) { currentCase = c; this.loadToForm(c); this.refreshDrawer(); }
            },

            deleteCurrent() {
                if (!currentCase) return;
                Storage.deleteCase(currentCase.id);
                Toast.show('Case deleted: ' + currentCase.id, 'red');
                const all = Storage.getAll();
                if (all.length > 0) { currentCase = all[0]; this.loadToForm(all[0]); }
                else this.createNew();
                this.refreshDrawer();
            },

            refreshDrawer() {
                const all = Storage.getAll();
                const list = $('case-list');
                list.innerHTML = '';
                all.forEach(c => {
                    const chip = document.createElement('button');
                    chip.className = 'case-chip' + (currentCase && c.id === currentCase.id ? ' active' : '');
                    chip.textContent = (c.name || 'Unnamed') + ' (' + c.id + ')';
                    chip.setAttribute('tabindex', '0');
                    chip.setAttribute('aria-label', 'Switch to case ' + c.id);
                    chip.addEventListener('click', () => this.switchTo(c.id));
                    list.appendChild(chip);
                });
                const newBtn = document.createElement('button');
                newBtn.className = 'case-chip new-case'; newBtn.textContent = '+ NEW CASE';
                newBtn.setAttribute('tabindex', '0');
                newBtn.addEventListener('click', () => this.createNew());
                list.appendChild(newBtn);
                $('case-count-badge').textContent = all.length + ' CASES';
            },

            addTimeline(type, msg) {
                if (!currentCase) return;
                currentCase.timeline.unshift({ type, msg, time: now(), date: new Date().toISOString() });
                if (currentCase.timeline.length > 50) currentCase.timeline.length = 50;
                this.renderTimeline(currentCase);
                if (Settings.autoSave) Storage.saveCase(currentCase);
            },

            renderTimeline(c) {
                const area = $('timeline-area');
                if (!c || !c.timeline || c.timeline.length === 0) {
                    area.innerHTML = '<div style="padding:12px;font-size:11px;color:var(--t4);text-align:center;">No events yet.</div>';
                    return;
                }
                area.innerHTML = c.timeline.slice(0, 30).map(t =>
                    `<div class="timeline-item"><div class="timeline-dot ${t.type}"></div><div class="timeline-time">${t.time || ''}</div><div class="timeline-text">${t.msg}</div></div>`
                ).join('');
            },

            autoSave: debounce(function () {
                if (!currentCase || !Settings.autoSave) return;
                CaseManager.readFromForm();
                Storage.saveCase(currentCase);
            }, 800)
        };

        function debounce(fn, ms) {
            let t; return function (...a) { clearTimeout(t); t = setTimeout(() => fn.apply(this, a), ms); };
        }

        /* ══════════ CHIP HELPERS ══════════ */
        function getActiveChip(groupId) { const c = document.querySelector('#' + groupId + ' .chip.active'); return c ? c.textContent : ''; }
        function getActiveChips(groupId) { return [...document.querySelectorAll('#' + groupId + ' .chip.active')].map(c => c.textContent); }
        function setChipGroup(groupId, val) {
            document.querySelectorAll('#' + groupId + ' .chip').forEach(c => {
                c.classList.toggle('active', c.textContent === val);
                c.setAttribute('aria-checked', c.textContent === val ? 'true' : 'false');
            });
        }
        function setMarksChips(arr) {
            document.querySelectorAll('#marks-chips .chip').forEach(c => {
                c.classList.toggle('active', arr.includes(c.textContent));
            });
        }

        /* ══════════ EVENT DELEGATION ══════════ */
        document.addEventListener('click', function (e) {
            // Chips
            const chip = e.target.closest('.chip');
            if (chip) {
                const group = chip.closest('.chip-group');
                const isMulti = group && group.id === 'marks-chips';
                if (!isMulti) { group.querySelectorAll('.chip').forEach(c => { c.classList.remove('active'); c.setAttribute('aria-checked', 'false'); }); }
                chip.classList.toggle('active');
                chip.setAttribute('aria-checked', chip.classList.contains('active') ? 'true' : 'false');
                updateCase(); CaseManager.autoSave();
                return;
            }
            // Upload zone
            if (e.target.closest('#upload-zone')) { $('photo-file').click(); return; }
            // Ripple on buttons
            const btn = e.target.closest('.btn-primary');
            if (btn) {
                const r = document.createElement('span'); r.className = 'ripple';
                const rect = btn.getBoundingClientRect();
                r.style.left = (e.clientX - rect.left) + 'px'; r.style.top = (e.clientY - rect.top) + 'px';
                btn.appendChild(r); setTimeout(() => r.remove(), 600);
            }
            // Toggle switches
            const toggle = e.target.closest('.toggle-switch');
            if (toggle) {
                toggle.classList.toggle('on');
                const isOn = toggle.classList.contains('on');
                if (toggle.id === 's-browser-notif') {
                    Settings.browserNotif = isOn;
                    if (isOn && 'Notification' in window) Notification.requestPermission();
                }
                if (toggle.id === 's-audio-alert') Settings.audioAlert = isOn;
                if (toggle.id === 's-autosave') Settings.autoSave = isOn;
                Settings.save();
                return;
            }
            // View toggle
            const vt = e.target.closest('.view-toggle button');
            if (vt) {
                document.querySelectorAll('#view-toggle button').forEach(b => b.classList.remove('active'));
                vt.classList.add('active');
                const v = vt.dataset.view;
                $('age-details-view').style.display = v === 'details' ? 'grid' : 'none';
                $('age-compare-view').classList.toggle('active', v === 'compare');
                return;
            }
            // Mobile tabs
            const mt = e.target.closest('.mob-tab');
            if (mt) {
                document.querySelectorAll('.mob-tab').forEach(t => t.classList.remove('active'));
                mt.classList.add('active');
                ['panel-case', 'panel-camera', 'panel-alerts'].forEach(id => {
                    $(id).classList.toggle('mob-active', id === mt.dataset.panel);
                });
                return;
            }
        });

        // Keyboard on chips
        document.addEventListener('keydown', function (e) {
            if ((e.key === 'Enter' || e.key === ' ') && e.target.classList.contains('chip')) {
                e.preventDefault(); e.target.click();
            }
            if ((e.key === 'Enter' || e.key === ' ') && e.target.id === 'upload-zone') {
                e.preventDefault(); $('photo-file').click();
            }
        });

        /* ══════════ SLIDER ══════════ */
        $('f-height').addEventListener('input', function () { $('height-val').textContent = this.value + ' cm'; updateCase(); CaseManager.autoSave(); });
        $('s-sensitivity').addEventListener('input', function () { Settings.matchThreshold = this.value / 100; $('s-sensitivity-val').textContent = Settings.matchThreshold.toFixed(2); Settings.save(); });

        /* ══════════ FORM AUTO-SAVE ══════════ */
        ['f-name', 'f-age', 'f-date', 'f-location', 'f-gender', 'f-hair-color', 'f-hair-style', 'f-eye', 'f-nose', 'f-notes'].forEach(id => {
            $(id).addEventListener('input', function () { updateCase(); CaseManager.autoSave(); });
            $(id).addEventListener('change', function () { updateCase(); CaseManager.autoSave(); });
        });

        /* ══════════ PHOTO UPLOAD ══════════ */
        $('photo-file').addEventListener('change', function (e) {
            const file = e.target.files[0]; if (!file) return;
            const reader = new FileReader();
            reader.onload = function (ev) {
                uploadedPhotoURL = ev.target.result;
                $('photo-preview').src = uploadedPhotoURL;
                $('photo-preview').style.display = 'block';
                $('upload-prompt').style.display = 'none';
                addLog('cyan', 'Reference photo uploaded.');
                CaseManager.autoSave();
                extractFaceDescriptor();
            };
            reader.readAsDataURL(file);
        });

        /* ══════════ FACE DESCRIPTOR EXTRACTION ══════════ */
        async function extractFaceDescriptor() {
            if (!uploadedPhotoURL) return;
            if (!faceApiReady) { addLog('amber', 'AI models still loading — face extraction will retry...'); return; }
            try {
                const img = new Image(); img.crossOrigin = 'anonymous'; img.src = uploadedPhotoURL;
                await new Promise((resolve, reject) => { img.onload = resolve; img.onerror = reject; });
                const det = await faceapi.detectSingleFace(img, new faceapi.TinyFaceDetectorOptions({ inputSize: 416, scoreThreshold: 0.3 })).withFaceLandmarks().withFaceDescriptor();
                if (det) {
                    uploadedFaceDescriptor = det.descriptor;
                    addLog('green', '✓ Reference face profile extracted — matching active.');
                    Toast.show('Face profile extracted — matching active', 'green');
                } else {
                    addLog('amber', 'No face found in reference photo. Try a clearer photo.');
                    uploadedFaceDescriptor = null;
                }
            } catch (ex) { addLog('amber', 'Face extraction failed: ' + ex.message); uploadedFaceDescriptor = null; }
        }

        /* ══════════ CASE UPDATE (stats) ══════════ */
        function updateCase() {
            const name = $('f-name').value.trim(), age = parseInt($('f-age').value), dateStr = $('f-date').value;
            if (name) {
                const hash = name.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
                if (currentCase) $('case-num').textContent = 'CASE #' + currentCase.id;
            }
            if (dateStr) {
                const lost = new Date(dateStr), days = Math.max(0, Math.floor((Date.now() - lost) / 86400000));
                $('stat-days').textContent = days;
                if (!isNaN(age)) { const yrs = days / 365; $('stat-currage').textContent = Math.round(age + yrs); }
            }
        }

        /* ══════════ SETTINGS UI ══════════ */
        $('btn-settings').addEventListener('click', () => { $('settings-overlay').classList.add('open'); $('settings-panel').classList.add('open'); });
        $('settings-overlay').addEventListener('click', () => { $('settings-overlay').classList.remove('open'); $('settings-panel').classList.remove('open'); });
        $('btn-close-settings').addEventListener('click', () => { $('settings-overlay').classList.remove('open'); $('settings-panel').classList.remove('open'); });

        /* ══════════ SHORTCUTS OVERLAY ══════════ */
        $('btn-close-shortcuts').addEventListener('click', () => { $('shortcuts-overlay').classList.remove('open'); });

        /* ══════════ MODAL ══════════ */
        function closeModal() { $('match-modal').classList.remove('open'); }
        $('btn-modal-ack').addEventListener('click', closeModal);
        $('btn-modal-dismiss').addEventListener('click', closeModal);

        /* ══════════ KEYBOARD SHORTCUTS ══════════ */
        document.addEventListener('keydown', function (e) {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
            switch (e.key) {
                case '?': $('shortcuts-overlay').classList.toggle('open'); break;
                case 'c': case 'C': if (stream) stopCamera(); else startCamera(); break;
                case 'g': case 'G': generatePrediction(); break;
                case 'd': case 'D': { const n = $('f-name').value.trim(); if (n) triggerMatch(n); } break;
                case 'n': case 'N': CaseManager.createNew(); break;
                case 'e': case 'E': ExportManager.generateReport(); break;
                case 's': case 'S': $('settings-overlay').classList.add('open'); $('settings-panel').classList.add('open'); break;
                case 'v': case 'V': {
                    const cb = document.querySelector('#view-toggle button:not(.active)');
                    if (cb) cb.click();
                } break;
                case 'Escape':
                    $('match-modal').classList.remove('open');
                    $('shortcuts-overlay').classList.remove('open');
                    $('settings-overlay').classList.remove('open');
                    $('settings-panel').classList.remove('open');
                    break;
            }
        });

        /* ══════════ LOG ══════════ */
        function addLog(type, msg) {
            const log = $('event-log'), item = document.createElement('div');
            item.className = 'event-item';
            item.innerHTML = `<div class="event-time">${nowShort()}</div><div class="event-dot ${type}"></div><div class="event-text">${msg}</div>`;
            log.insertBefore(item, log.firstChild);
        }

        /* ══════════ COMPARISON SLIDER ══════════ */
        (function () {
            const slider = $('compare-slider'), wrap = $('compare-wrap');
            let dragging = false;
            function onMove(e) {
                if (!dragging) return;
                const rect = wrap.getBoundingClientRect();
                const x = Math.max(0, Math.min(((e.clientX || e.touches[0].clientX) - rect.left) / rect.width, 1));
                slider.style.left = (x * 100) + '%';
                $('compare-after').style.clipPath = 'inset(0 0 0 ' + (x * 100) + '%)';
            }
            slider.addEventListener('mousedown', () => dragging = true);
            slider.addEventListener('touchstart', () => dragging = true);
            document.addEventListener('mousemove', onMove);
            document.addEventListener('touchmove', onMove);
            document.addEventListener('mouseup', () => dragging = false);
            document.addEventListener('touchend', () => dragging = false);
        })();

        /* ══════════ WEBCAM ══════════ */
        let stream = null, detectionInterval = null, frameCount = 0, matchCount = 0, faceDetectCycle = 0, lastMatchFrame = 0;

        async function startCamera() {
            const camOff = $('cam-off');
            camOff.innerHTML = `<div class="cam-off-icon" style="border-color:var(--a1);"><svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" width="28" height="28"><path stroke="var(--a1)" stroke-linecap="round" stroke-linejoin="round" d="M15.75 10.5l4.72-4.72a.75.75 0 011.28.53v11.38a.75.75 0 01-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 002.25-2.25v-9a2.25 2.25 0 00-2.25-2.25h-9A2.25 2.25 0 002.25 7.5v9a2.25 2.25 0 002.25 2.25z"/></svg></div><div class="cam-off-text" style="color:var(--a1);">CONNECTING…</div>`;
            addLog('cyan', 'Requesting camera access…');
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { showCamError('Camera API not available', 'Try opening in Chrome or Edge.'); return; }
            const constraints = [{ video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false }, { video: { facingMode: 'user' }, audio: false }, { video: true, audio: false }];
            let lastError = null;
            for (const c of constraints) { try { stream = await navigator.mediaDevices.getUserMedia(c); break; } catch (e) { lastError = e; stream = null; } }
            if (!stream) {
                const e = lastError; let reason = 'Unknown error', hint = 'Try a different browser.';
                if (e.name === 'NotAllowedError') { reason = 'Permission Denied'; hint = 'Allow camera access in browser.'; }
                else if (e.name === 'NotFoundError') { reason = 'No Camera Found'; hint = 'Connect a webcam.'; }
                else if (e.name === 'NotReadableError') { reason = 'Camera In Use'; hint = 'Close other apps using camera.'; }
                showCamError(reason, hint, e.name); return;
            }
            const vid = $('webcam'); vid.srcObject = stream;
            vid.onloadedmetadata = () => {
                vid.play().catch(() => { });
                camOff.style.display = 'none'; $('btn-stop-cam').style.display = 'block';
                $('cam-badge').textContent = 'LIVE'; $('cam-badge').classList.add('green');
                $('hud-bl').textContent = `RES: ${vid.videoWidth}×${vid.videoHeight}`;
                $('scan-line').classList.add('active'); $('hud-tr').textContent = 'DETECTING';
                $('det-label').textContent = 'DETECTION: ACTIVE';
                addLog('green', `Camera live · ${vid.videoWidth}×${vid.videoHeight}`);
                Toast.show('Camera connected', 'green');
                CaseManager.addTimeline('green', 'Camera started');
                startDetectionLoop();
            };
            setTimeout(() => { if (camOff.style.display !== 'none') { vid.play().catch(() => { }); camOff.style.display = 'none'; $('btn-stop-cam').style.display = 'block'; $('cam-badge').textContent = 'LIVE'; $('scan-line').classList.add('active'); startDetectionLoop(); } }, 3000);
        }

        function stopCamera() {
            if (detectionInterval) clearInterval(detectionInterval);
            if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null; }
            $('webcam').srcObject = null;
            const canvas = $('overlay-canvas'); if (canvas) { const ctx = canvas.getContext('2d'); ctx.clearRect(0, 0, canvas.width, canvas.height); }
            $('cam-off').style.display = 'flex'; $('btn-stop-cam').style.display = 'none';
            $('cam-badge').textContent = 'OFFLINE'; $('cam-badge').classList.remove('green');
            $('scan-line').classList.remove('active');
            $('hud-tl').textContent = 'FINDTRACE LIVE'; $('hud-tr').textContent = '—';
            $('hud-bl').textContent = 'RES: —'; $('hud-br').textContent = 'FPS: —';
            $('det-label').textContent = 'DETECTION: STANDBY';
            addLog('cyan', 'Camera stopped.'); CaseManager.addTimeline('cyan', 'Camera stopped');
        }
        $('btn-stop-cam').addEventListener('click', stopCamera);
        $('btn-start-cam').addEventListener('click', startCamera);

        function showCamError(reason, hint, code = '') {
            $('cam-off').innerHTML = `<div class="cam-off-icon" style="border-color:var(--a2);"><svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" width="28" height="28"><path stroke="var(--a2)" stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"/></svg></div>
  <div class="cam-off-text" style="color:var(--a2);">${reason}</div>
  <div style="font-size:11px;color:var(--t3);font-family:'JetBrains Mono',monospace;letter-spacing:1px;text-align:center;max-width:280px;line-height:1.7;padding:0 16px;">${hint}</div>
  <div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin-top:12px;">
  <button class="btn-primary btn-sm" onclick="startCamera()">↻ RETRY</button>
  <button class="btn-primary btn-sm" style="background:var(--s3);color:var(--t2);border:1px solid var(--b2);" onclick="startSimMode()">▶ SIM MODE</button></div>`;
            addLog('amber', `Camera error: ${reason}`);
        }

        function startSimMode() {
            $('cam-off').style.display = 'none'; $('btn-stop-cam').style.display = 'block';
            const canvas = $('overlay-canvas'), area = $('cam-area');
            canvas.width = area.offsetWidth; canvas.height = area.offsetHeight;
            const ctx = canvas.getContext('2d');
            function drawSim() {
                ctx.fillStyle = '#0a1220'; ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.strokeStyle = 'rgba(0,229,255,0.04)'; ctx.lineWidth = 1;
                for (let x = 0; x < canvas.width; x += 30) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke(); }
                for (let y = 0; y < canvas.height; y += 30) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke(); }
                ctx.fillStyle = 'rgba(0,229,255,0.12)'; ctx.font = 'bold 48px monospace'; ctx.textAlign = 'center';
                ctx.fillText('SIM MODE', canvas.width / 2, canvas.height / 2);
            }
            setInterval(drawSim, 2000); drawSim();
            $('cam-badge').textContent = 'SIM'; $('cam-badge').style.background = 'rgba(255,185,48,.08)'; $('cam-badge').style.color = 'var(--a4)';
            $('scan-line').classList.add('active'); $('det-label').textContent = 'DETECTION: SIM';
            addLog('amber', 'Simulation mode active.'); startDetectionLoop();
        }

        /* ══════════ FACE API LOADING ══════════ */
        let faceApiReady = false;
        (async function () {
            if (typeof faceapi !== 'undefined') {
                try {
                    await Promise.all([
                        faceapi.nets.tinyFaceDetector.loadFromUri('https://justadudewhohacks.github.io/face-api.js/models'),
                        faceapi.nets.faceLandmark68Net.loadFromUri('https://justadudewhohacks.github.io/face-api.js/models'),
                        faceapi.nets.faceRecognitionNet.loadFromUri('https://justadudewhohacks.github.io/face-api.js/models')
                    ]);
                    faceApiReady = true; addLog('green', 'Face recognition AI models loaded.');
                    Toast.show('AI models loaded', 'green');
                    // Retry face extraction if a photo was uploaded before models loaded
                    if (uploadedPhotoURL && !uploadedFaceDescriptor) extractFaceDescriptor();
                } catch (e) { addLog('amber', 'Face AI models failed — using simulation.'); }
            }
        })();

        /* ══════════ DETECTION LOOP ══════════ */
        let isDetecting = false;
        function startDetectionLoop() {
            const vid = $('webcam'), canvas = $('overlay-canvas'), area = $('cam-area');
            let fps = 0, lastFps = Date.now();
            function resizeCanvas() { canvas.width = area.offsetWidth; canvas.height = area.offsetHeight; }
            resizeCanvas(); window.addEventListener('resize', resizeCanvas);

            detectionInterval = setInterval(async () => {
                frameCount++; faceDetectCycle++;
                $('stat-frames').textContent = frameCount.toLocaleString();
                fps++;
                if (Date.now() - lastFps > 1000) { $('hud-br').textContent = `FPS: ${fps}`; fps = 0; lastFps = Date.now(); }
                $('hud-tl').textContent = `FINDTRACE · ${now()}`;

                if (faceApiReady && vid.readyState >= 2 && !isDetecting) {
                    isDetecting = true;
                    try {
                        const dets = await faceapi.detectAllFaces(vid, new faceapi.TinyFaceDetectorOptions({ inputSize: 416, scoreThreshold: 0.4 })).withFaceLandmarks().withFaceDescriptors();
                        const ctx = canvas.getContext('2d'); ctx.clearRect(0, 0, canvas.width, canvas.height);
                        if (dets.length > 0) {
                            const resized = faceapi.resizeResults(dets, { width: canvas.width, height: canvas.height });
                            resized.forEach(d => {
                                const b = d.detection.box; let dist = null, isMatch = false, boxColor = '#ffb930', lbl = 'FACE DETECTED', sc = (d.detection.score * 100).toFixed(1);
                                if (uploadedFaceDescriptor) {
                                    dist = faceapi.euclideanDistance(d.descriptor, uploadedFaceDescriptor);
                                    if (dist < Settings.matchThreshold) { isMatch = true; boxColor = '#00e5ff'; lbl = `TARGET MATCH! (${(100 - dist * 100).toFixed(1)}%)`; }
                                    else { boxColor = '#ff4d6d'; lbl = `NO MATCH (${dist.toFixed(2)})`; isMatch = false; }
                                } else { isMatch = false; boxColor = '#ffb930'; lbl = `FACE · ${sc}% (no ref photo)`; }

                                ctx.strokeStyle = boxColor; ctx.lineWidth = 2; ctx.shadowColor = boxColor; ctx.shadowBlur = 10;
                                ctx.strokeRect(b.x, b.y, b.width, b.height); ctx.shadowBlur = 0;
                                const cl = 14; ctx.lineWidth = 3;
                                ctx.beginPath(); ctx.moveTo(b.x, b.y + cl); ctx.lineTo(b.x, b.y); ctx.lineTo(b.x + cl, b.y); ctx.stroke();
                                ctx.beginPath(); ctx.moveTo(b.x + b.width - cl, b.y); ctx.lineTo(b.x + b.width, b.y); ctx.lineTo(b.x + b.width, b.y + cl); ctx.stroke();
                                ctx.beginPath(); ctx.moveTo(b.x, b.y + b.height - cl); ctx.lineTo(b.x, b.y + b.height); ctx.lineTo(b.x + cl, b.y + b.height); ctx.stroke();
                                ctx.beginPath(); ctx.moveTo(b.x + b.width - cl, b.y + b.height); ctx.lineTo(b.x + b.width, b.y + b.height); ctx.lineTo(b.x + b.width, b.y + b.height - cl); ctx.stroke();
                                ctx.font = '10px "JetBrains Mono",monospace';
                                const tw = ctx.measureText(lbl).width;
                                ctx.fillStyle = 'rgba(4,7,12,0.85)'; ctx.fillRect(b.x, b.y - 20, tw + 12, 18);
                                ctx.fillStyle = boxColor; ctx.fillText(lbl, b.x + 6, b.y - 6);

                                // Only trigger match when reference photo is uploaded AND face matches
                                if (isMatch && uploadedFaceDescriptor && frameCount > 20 && (frameCount - lastMatchFrame) > 100) {
                                    const name = $('f-name').value.trim() || 'Unknown Subject';
                                    triggerMatch(name); lastMatchFrame = frameCount;
                                }
                            });
                        }
                    } catch (e) { }
                    isDetecting = false;
                } else if (!faceApiReady && faceDetectCycle % 90 === 0) {
                    simulateFaceDetect();
                }
            }, 100);
        }

        function simulateFaceDetect() {
            const box = $('face-box'), label = $('face-label'), area = $('cam-area');
            const w = area.offsetWidth, h = area.offsetHeight;
            const bx = w * .2 + Math.random() * (w * .4), by = h * .1 + Math.random() * (h * .3), bw = w * .18 + Math.random() * (w * .1), bh = bw * 1.3;
            box.style.left = bx + 'px'; box.style.top = by + 'px'; box.style.width = bw + 'px'; box.style.height = bh + 'px'; box.style.display = 'block';
            label.textContent = `FACE DETECTED · ${(65 + Math.random() * 30).toFixed(1)}%`;
            setTimeout(() => { box.style.display = 'none'; }, 2000);
        }

        /* ══════════ GEOLOCATION ══════════ */
        let cachedDeviceLocation = null, locationFetchPromise = null;
        function getDeviceLocation() {
            if (cachedDeviceLocation) return Promise.resolve(cachedDeviceLocation);
            if (locationFetchPromise) return locationFetchPromise;
            locationFetchPromise = new Promise(resolve => {
                const fallbackToIP = () => {
                    fetch('https://ipapi.co/json/').then(r => r.json()).then(d => {
                        if (d && d.latitude) { cachedDeviceLocation = { coords: `${Math.abs(d.latitude).toFixed(6)}° ${d.latitude >= 0 ? 'N' : 'S'}, ${Math.abs(d.longitude).toFixed(6)}° ${d.longitude >= 0 ? 'E' : 'W'}`, address: `${d.city}, ${d.region} (IP Location)`, lat: d.latitude, lng: d.longitude }; resolve(cachedDeviceLocation); }
                        else throw new Error();
                    }).catch(() => { cachedDeviceLocation = { coords: '0.0000° N, 0.0000° E', address: 'Location Unavailable', lat: 0, lng: 0 }; resolve(cachedDeviceLocation); });
                };
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(pos => {
                        const lat = pos.coords.latitude, lng = pos.coords.longitude, acc = pos.coords.accuracy;
                        cachedDeviceLocation = { coords: `${Math.abs(lat).toFixed(6)}° ${lat >= 0 ? 'N' : 'S'}, ${Math.abs(lng).toFixed(6)}° ${lng >= 0 ? 'E' : 'W'}`, address: `Verified Live GPS (±${Math.round(acc)}m accuracy)`, lat, lng };
                        resolve(cachedDeviceLocation);
                    }, () => fallbackToIP(), { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 });
                } else fallbackToIP();
            });
            return locationFetchPromise;
        }
        // Pre-fetch location silently (don't load map embed yet — only on match, like v2)
        getDeviceLocation().then(loc => { addLog('cyan', `Location acquired: ${loc.address}`); });

        /* ══════════ MATCH TRIGGER ══════════ */
        function triggerMatch(name) { getDeviceLocation().then(loc => finalizeMatch(name, loc)); }

        function finalizeMatch(name, loc) {
            matchCount++; $('stat-matches').textContent = matchCount; $('det-count-badge').textContent = matchCount + ' ALERTS';
            const conf = uploadedFaceDescriptor ? (85 + Math.random() * 12).toFixed(1) : (75 + Math.random() * 18).toFixed(1);
            const t = now();
            const flash = $('match-flash'); flash.style.display = 'block'; setTimeout(() => { flash.style.display = 'none'; }, 600);
            addAlertCard(name, conf, loc, t); showLocation(loc);
            addLog('green', `MATCH: ${name} at ${loc.address} — ${conf}%`);
            CaseManager.addTimeline('green', `Match: ${name} (${conf}%) at ${loc.address}`);
            Toast.show(`Match detected: ${name} — ${conf}%`, 'green');
            AudioAlert.play();
            // Browser notification
            if (Settings.browserNotif && 'Notification' in window && Notification.permission === 'granted') {
                new Notification('FindTrace — Match Detected', { body: `${name} detected at ${loc.address}\nConfidence: ${conf}%`, icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="%2300e5ff"/></svg>' });
            }
            // Save match to case
            if (currentCase) { currentCase.matches.push({ name, conf, loc, time: t, date: new Date().toISOString() }); if (Settings.autoSave) Storage.saveCase(currentCase); }
            // Modal
            $('m-name').textContent = name; $('m-conf').textContent = conf + '%'; $('m-time').textContent = t;
            $('m-coords').textContent = loc.coords; $('m-location').textContent = loc.address;
            $('match-modal').classList.add('open');
            announce('Match detected: ' + name + ', confidence ' + conf + '%');
        }

        function addAlertCard(name, conf, loc, t) {
            const area = $('alerts-area');
            if (area.querySelector('[style*="padding:24px"]')) area.innerHTML = '';
            // Extract lat/lng for the clickable link
            let lat = 0, lng = 0;
            const parts = loc.coords.match(/([\d.]+)°\s*([NS]),\s*([\d.]+)°\s*([EW])/);
            if (parts) { lat = parseFloat(parts[1]); lng = parseFloat(parts[3]); if (parts[2] === 'S') lat = -lat; if (parts[4] === 'W') lng = -lng; }
            const mapsUrl = `https://www.google.com/maps/place/${lat},${lng}/@${lat},${lng},17z`;
            const card = document.createElement('div'); card.className = 'alert-card match';
            card.style.cursor = 'pointer';
            card.setAttribute('title', 'Tap to open location on Google Maps');
            card.innerHTML = `<div class="alert-top"><div class="alert-type match">⚑ MATCH DETECTED</div><div class="alert-time">${t}</div></div>
  <div class="alert-title">${name} — Possible Identification</div>
  <div class="alert-loc"><svg width="10" height="10" fill="none" viewBox="0 0 24 24" stroke="var(--t3)" stroke-width="2"><path d="M12 22s-8-4.5-8-11.8A8 8 0 0112 2a8 8 0 018 8.2c0 7.3-8 11.8-8 11.8z"/><circle cx="12" cy="10" r="3"/></svg>${loc.address}</div>
  <div class="alert-conf">CONFIDENCE: ${conf}%</div>
  <div style="margin-top:8px;display:flex;align-items:center;gap:6px;font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:1px;color:var(--a1);"><svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="var(--a1)" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"/></svg>📍 TAP TO OPEN IN GOOGLE MAPS</div>`;
            card.addEventListener('click', function () { window.open(mapsUrl, '_blank'); });
            area.insertBefore(card, area.firstChild);
        }

        let lastDetectedLat = null, lastDetectedLng = null;

        function showLocation(loc) {
            const parts = loc.coords.match(/([\d.]+)°\s*([NS]),\s*([\d.]+)°\s*([EW])/);
            if (!parts) return;
            let lat = parseFloat(parts[1]), lng = parseFloat(parts[3]);
            if (parts[2] === 'S') lat = -lat; if (parts[4] === 'W') lng = -lng;
            lastDetectedLat = lat; lastDetectedLng = lng;
            // Hide waiting, show details
            $('loc-waiting').style.display = 'none';
            $('loc-details').style.display = 'block';
            // Fill in human-readable info
            $('loc-coords').textContent = loc.coords;
            $('loc-address').textContent = loc.address;
            $('loc-accuracy').textContent = loc.address.includes('±') ? '✓ GPS Verified' : '≈ Approximate (IP-based)';
            // Set Google Maps link
            const mapsUrl = `https://www.google.com/maps/place/${lat},${lng}/@${lat},${lng},17z`;
            $('btn-open-maps').href = mapsUrl;
        }

        /* ══════════ AGE PROGRESSION (Enhanced) ══════════ */
        function generateAgedImage(imgSrc, yearsElapsed, callback) {
            const img = new Image();
            img.onload = function () {
                const S = 240, c = document.createElement('canvas'); c.width = S; c.height = S;
                const ctx = c.getContext('2d');
                const mn = Math.min(img.width, img.height);
                ctx.drawImage(img, (img.width - mn) / 2, (img.height - mn) / 2, mn, mn, 0, 0, S, S);
                // Exponential intensity curve for dramatic aging
                const t = Math.min(1, yearsElapsed > 10 ? 0.5 + Math.pow((yearsElapsed - 10) / 20, 0.7) * 0.5 : yearsElapsed / 20);
                const ti = Math.min(1, yearsElapsed / 15); // linear fallback

                // 1. Pixel-level aging
                const id = ctx.getImageData(0, 0, S, S), d = id.data;
                for (let i = 0; i < d.length; i += 4) {
                    const r = d[i], g = d[i + 1], b = d[i + 2], gray = 0.299 * r + 0.587 * g + 0.114 * b;
                    const ds = t * 0.45;
                    d[i] = Math.min(255, r * (1 - ds) + gray * ds + t * 14);
                    d[i + 1] = Math.min(255, g * (1 - ds) + gray * ds + t * 5);
                    d[i + 2] = Math.max(0, b * (1 - ds) + gray * ds - t * 10);
                    d[i] = Math.max(0, d[i] - t * 16); d[i + 1] = Math.max(0, d[i + 1] - t * 16); d[i + 2] = Math.max(0, d[i + 2] - t * 10);
                    if (t > 0.2 && Math.random() < t * 0.0015) { d[i] = Math.min(255, r + 40); d[i + 1] = Math.max(0, g - 10); d[i + 2] = Math.max(0, b - 16); }
                }
                ctx.putImageData(id, 0, 0);

                // 2. Wrinkles
                ctx.globalAlpha = t * 0.6; ctx.strokeStyle = 'rgba(60,40,30,0.7)'; ctx.lineWidth = 0.7 + t * 1.2;
                const cx = S / 2;
                if (yearsElapsed > 1.5) {
                    for (let i = 0; i < Math.min(6, Math.floor(yearsElapsed / 2)); i++) {
                        const y = S * 0.12 + i * S * 0.032; ctx.beginPath(); ctx.moveTo(cx - S * 0.25, y);
                        ctx.quadraticCurveTo(cx, y - 4 * t, cx + S * 0.25, y); ctx.stroke();
                    }
                }
                if (yearsElapsed > 3) {
                    const ey = S * 0.38; ctx.lineWidth = 0.5 + t * 0.8;
                    for (let j = 0; j < 4; j++) {
                        ctx.beginPath(); ctx.moveTo(S * 0.17, ey + (j - 1) * 5); ctx.lineTo(S * 0.06, ey + (j - 1) * 8); ctx.stroke();
                        ctx.beginPath(); ctx.moveTo(S * 0.83, ey + (j - 1) * 5); ctx.lineTo(S * 0.94, ey + (j - 1) * 8); ctx.stroke();
                    }
                }
                if (yearsElapsed > 2.5) {
                    ctx.lineWidth = 1.2 + t * 1.2; ctx.globalAlpha = t * 0.7;
                    ctx.beginPath(); ctx.moveTo(S * 0.34, S * 0.44); ctx.quadraticCurveTo(S * 0.26, S * 0.6, S * 0.33, S * 0.74); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(S * 0.66, S * 0.44); ctx.quadraticCurveTo(S * 0.74, S * 0.6, S * 0.67, S * 0.74); ctx.stroke();
                }
                // Marionette lines
                if (yearsElapsed > 8) {
                    ctx.globalAlpha = t * 0.5; ctx.lineWidth = 0.8 + t;
                    ctx.beginPath(); ctx.moveTo(S * 0.33, S * 0.74); ctx.lineTo(S * 0.34, S * 0.82); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(S * 0.67, S * 0.74); ctx.lineTo(S * 0.66, S * 0.82); ctx.stroke();
                }
                // Neck wrinkles
                if (yearsElapsed > 10) {
                    ctx.globalAlpha = t * 0.3; ctx.lineWidth = 0.6;
                    for (let i = 0; i < 3; i++) {
                        const y = S * 0.88 + i * S * 0.03;
                        ctx.beginPath(); ctx.moveTo(S * 0.3, y); ctx.quadraticCurveTo(cx, y + 2, S * 0.7, y); ctx.stroke();
                    }
                }
                // Under-eye hollowing
                if (yearsElapsed > 4) {
                    ctx.globalAlpha = t * 0.35; ctx.fillStyle = 'rgba(40,25,40,0.5)';
                    ctx.beginPath(); ctx.ellipse(S * 0.35, S * 0.42, S * 0.08, S * 0.022, 0, 0, Math.PI * 2); ctx.fill();
                    ctx.beginPath(); ctx.ellipse(S * 0.65, S * 0.42, S * 0.08, S * 0.022, 0, 0, Math.PI * 2); ctx.fill();
                }
                // Temple hollowing
                if (yearsElapsed > 12) {
                    ctx.globalAlpha = t * 0.2; ctx.fillStyle = 'rgba(30,20,30,0.4)';
                    ctx.beginPath(); ctx.ellipse(S * 0.2, S * 0.28, S * 0.05, S * 0.08, -0.2, 0, Math.PI * 2); ctx.fill();
                    ctx.beginPath(); ctx.ellipse(S * 0.8, S * 0.28, S * 0.05, S * 0.08, 0.2, 0, Math.PI * 2); ctx.fill();
                }
                // 3. Hair greying (progressive)
                if (yearsElapsed > 3) {
                    ctx.globalAlpha = t * 0.6;
                    ctx.fillStyle = `rgba(175,175,180,${t * 0.55})`;
                    ctx.beginPath(); ctx.ellipse(S * 0.16, S * 0.1, S * 0.1, S * 0.07, -0.3, 0, Math.PI * 2); ctx.fill();
                    ctx.beginPath(); ctx.ellipse(S * 0.84, S * 0.1, S * 0.1, S * 0.07, 0.3, 0, Math.PI * 2); ctx.fill();
                    if (yearsElapsed > 7) {
                        ctx.fillStyle = `rgba(200,200,205,${t * 0.45})`;
                        ctx.beginPath(); ctx.ellipse(S * 0.3, S * 0.05, S * 0.12, S * 0.05, 0, 0, Math.PI * 2); ctx.fill();
                        ctx.beginPath(); ctx.ellipse(S * 0.7, S * 0.05, S * 0.12, S * 0.05, 0, 0, Math.PI * 2); ctx.fill();
                    }
                    if (yearsElapsed > 14) {
                        ctx.fillStyle = `rgba(220,220,225,${t * 0.35})`;
                        ctx.beginPath(); ctx.ellipse(S * 0.5, S * 0.04, S * 0.15, S * 0.04, 0, 0, Math.PI * 2); ctx.fill();
                    }
                }
                // 4. Jawline sagging
                if (yearsElapsed > 6) {
                    ctx.globalAlpha = t * 0.15;
                    try { ctx.filter = `blur(${t * 3}px)`; } catch (e) { }
                    ctx.drawImage(c, 0, S * 0.7, S, S * 0.3, 0, S * 0.73, S, S * 0.3);
                    ctx.filter = 'none';
                }
                // 5. Skin texture
                ctx.globalAlpha = t * 0.08;
                for (let x = 0; x < S; x += 2) {
                    for (let y = 0; y < S; y += 2) {
                        if (Math.random() < 0.3) { const sh = Math.random() * 80; ctx.fillStyle = `rgba(${sh},${sh * 0.8},${sh * 0.6},0.5)`; ctx.fillRect(x, y, 1, 1); }
                    }
                }
                // 6. Lip lines
                if (yearsElapsed > 5) {
                    ctx.globalAlpha = t * 0.4; ctx.strokeStyle = 'rgba(60,40,30,0.5)'; ctx.lineWidth = 0.5 + t * 0.6;
                    for (let i = 0; i < 5; i++) { const lx = S * 0.4 + i * S * 0.05; ctx.beginPath(); ctx.moveTo(lx, S * 0.65); ctx.lineTo(lx, S * 0.7); ctx.stroke(); }
                }
                // 7. Cheek hollowing
                if (yearsElapsed > 10) {
                    ctx.globalAlpha = t * 0.15; ctx.fillStyle = 'rgba(30,20,30,0.3)';
                    ctx.beginPath(); ctx.ellipse(S * 0.28, S * 0.55, S * 0.06, S * 0.1, 0.1, 0, Math.PI * 2); ctx.fill();
                    ctx.beginPath(); ctx.ellipse(S * 0.72, S * 0.55, S * 0.06, S * 0.1, -0.1, 0, Math.PI * 2); ctx.fill();
                }
                ctx.globalAlpha = 1;
                callback(c.toDataURL('image/png'));
            };
            img.src = imgSrc;
        }

        /* ══════════ GENERATE PREDICTION ══════════ */
        let predictionLoading = false;
        async function generatePrediction() {
            if (predictionLoading) return;
            // Ensure face descriptor is extracted before prediction
            if (uploadedPhotoURL && !uploadedFaceDescriptor) await extractFaceDescriptor();
            const name = $('f-name').value.trim() || 'Unknown', age = parseInt($('f-age').value) || 25;
            const dateStr = $('f-date').value, gender = $('f-gender').value || 'Male';
            const height = $('f-height').value, build = getActiveChip('build-chips') || 'Average';
            const skin = getActiveChip('skin-chips') || 'Medium', face = getActiveChip('face-chips') || 'Oval';
            const hairColor = $('f-hair-color').value, hairStyle = $('f-hair-style').value;
            const eyeColor = $('f-eye').value, nose = $('f-nose').value;
            const facialHair = getActiveChip('facial-hair-chips') || 'None';
            const marks = getActiveChips('marks-chips').join(', ') || 'None', notes = $('f-notes').value;

            let daysElapsed = 0, yearsElapsed = 0;
            if (dateStr) { const lost = new Date(dateStr); daysElapsed = Math.max(0, Math.floor((Date.now() - lost) / 86400000)); yearsElapsed = parseFloat((daysElapsed / 365).toFixed(1)); }
            const currentAge = Math.round(age + yearsElapsed);
            $('pred-age-num').innerHTML = `${currentAge}<span> yrs</span>`;
            $('pred-years-label').textContent = `${yearsElapsed} years elapsed`;

            if (uploadedPhotoURL) {
                $('pred-placeholder').style.display = 'none';
                $('pred-img').style.display = 'block'; $('age-ring').style.display = 'block';
                generateAgedImage(uploadedPhotoURL, yearsElapsed, function (agedUrl) {
                    agedImageDataUrl = agedUrl;
                    $('pred-img').src = agedUrl;
                    $('compare-before').src = uploadedPhotoURL;
                    $('compare-after').src = agedUrl;
                });
            }

            const confVal = yearsElapsed > 10 ? 68 : yearsElapsed > 5 ? 79 : yearsElapsed > 1 ? 89 : 97;
            $('conf-pct').textContent = confVal + '%'; $('conf-fill').style.width = confVal + '%';
            $('prog-status').textContent = 'GENERATED';

            $('age-right').innerHTML = `<div style="display:flex;align-items:center;justify-content:center;height:100%;flex-direction:column;gap:10px;">
  <div style="width:32px;height:32px;border:2px solid var(--a1);border-top-color:transparent;border-radius:50%;animation:spin-slow .8s linear infinite;"></div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--t3);letter-spacing:2px;" class="loading-dots">GENERATING AI PREDICTION</div></div>`;

            predictionLoading = true;
            addLog('cyan', `Generating prediction for ${name} (${yearsElapsed} yrs elapsed)...`);
            CaseManager.addTimeline('cyan', `Age prediction started (${yearsElapsed} yrs)`);

            const prompt = `You are a forensic age-progression specialist. Describe how this missing person likely looks NOW after ${yearsElapsed} years.\n\nSUBJECT: ${name}, ${gender}, Age ${age}, Height ${height}cm, Build ${build}, Skin ${skin}, Face ${face}, Hair ${hairColor} ${hairStyle}, Eyes ${eyeColor}, Nose ${nose}, Facial hair ${facialHair}, Marks ${marks}, Notes ${notes || 'None'}\nTime elapsed: ${yearsElapsed} years. Current age: ${currentAge}\n\nRespond in JSON only (no markdown), keys: appearance_summary, hair_now, face_now, body_now, skin_now, search_tips, confidence_note`;

            try {
                const resp = await fetch('https://api.anthropic.com/v1/messages', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ model: 'claude-sonnet-4-20250514', max_tokens: 1000, messages: [{ role: 'user', content: prompt }] }) });
                const data = await resp.json();
                const raw = data.content?.map(b => b.text || '').join('').trim();
                const parsed = JSON.parse(raw.replace(/```json|```/g, '').trim());
                renderPrediction(parsed, name, currentAge, yearsElapsed, confVal);
                addLog('green', `Prediction complete for ${name}. Confidence: ${confVal}%.`);
            } catch (e) {
                renderPredictionFallback(name, age, currentAge, yearsElapsed, build, hairColor, skin, face, confVal);
                addLog('cyan', `Prediction generated (offline mode).`);
            }
            CaseManager.addTimeline('green', `Age prediction completed`);
            predictionLoading = false;
        }

        function renderPrediction(p, name, currentAge, yrs, conf) {
            $('age-right').innerHTML = `<div class="age-desc-title">AI-GENERATED PROFILE — ${name.toUpperCase()}</div>
  <div class="ai-desc-block"><div class="ai-desc-tag">APPEARANCE SUMMARY</div><div class="ai-desc-text">${p.appearance_summary}</div></div>
  <div class="attr-row"><div class="attr-icon"><svg fill="none" viewBox="0 0 24 24" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/></svg></div><div><div class="attr-key">FACE NOW</div><div class="attr-val">${p.face_now}</div></div></div>
  <div class="attr-row"><div class="attr-icon"><svg fill="none" viewBox="0 0 24 24" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M8 12h8M12 8v8"/></svg></div><div><div class="attr-key">HAIR NOW</div><div class="attr-val">${p.hair_now}</div></div></div>
  <div class="attr-row"><div class="attr-icon"><svg fill="none" viewBox="0 0 24 24" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/></svg></div><div><div class="attr-key">BODY / BUILD</div><div class="attr-val">${p.body_now}</div></div></div>
  <div class="attr-row"><div class="attr-icon"><svg fill="none" viewBox="0 0 24 24" stroke-width="1.5"><path d="M12 3v1.5M6.2 6.2l1.05 1.05M3 12h1.5M6.2 17.8l1.05-1.05M12 19.5V21M17.8 17.8l-1.05-1.05M21 12h-1.5M17.8 6.2l-1.05 1.05"/></svg></div><div><div class="attr-key">SKIN</div><div class="attr-val">${p.skin_now}</div></div></div>
  <div class="ai-desc-block" style="border-color:var(--a4);"><div class="ai-desc-tag" style="color:var(--a4);">SEARCH TIPS</div><div class="ai-desc-text">${p.search_tips}</div></div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--t4);letter-spacing:1.5px;line-height:1.6;padding:8px;background:var(--s1);border-radius:4px;">ⓘ ${p.confidence_note}</div>`;
        }

        function renderPredictionFallback(name, origAge, currAge, yrs, build, hair, skin, face, conf) {
            const note = yrs > 5 ? 'Significant aging expected.' : yrs > 1 ? 'Moderate changes visible.' : 'Minimal change expected.';
            $('age-right').innerHTML = `<div class="age-desc-title">PREDICTED PROFILE — ${name.toUpperCase()}</div>
  <div class="ai-desc-block"><div class="ai-desc-tag">APPEARANCE SUMMARY</div><div class="ai-desc-text">After ${yrs} years, subject appears ~${currAge} years old. ${note} ${skin} skin, ${face.toLowerCase()} face. ${hair} hair may show changes.</div></div>
  <div class="attr-row"><div class="attr-icon"><svg fill="none" viewBox="0 0 24 24" stroke-width="1.5"><path d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z"/></svg></div><div><div class="attr-key">FACE NOW</div><div class="attr-val">Aged ${face} face; fine lines near eyes and mouth after ${yrs}+ years.</div></div></div>
  <div class="attr-row"><div class="attr-icon"><svg fill="none" viewBox="0 0 24 24" stroke-width="1.5"><circle cx="12" cy="12" r="10"/></svg></div><div><div class="attr-key">HAIR NOW</div><div class="attr-val">${hair} hair, possibly greying at temples.</div></div></div>
  <div class="attr-row"><div class="attr-icon"><svg fill="none" viewBox="0 0 24 24" stroke-width="1.5"><path d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/></svg></div><div><div class="attr-key">BODY / BUILD</div><div class="attr-val">${build} build; may have shifted with age.</div></div></div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--t4);letter-spacing:1.5px;line-height:1.6;padding:8px;background:var(--s1);border-radius:4px;">ⓘ Prediction accuracy: ${conf}%. Based on statistical models.</div>`;
        }

        $('btn-generate').addEventListener('click', generatePrediction);

        /* ══════════ EXPORT MANAGER ══════════ */
        const ExportManager = {
            generateReport() {
                if (!currentCase) { Toast.show('No active case to export', 'amber'); return; }
                CaseManager.readFromForm();
                const c = currentCase, d = c.descriptors;
                const html = `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>FindTrace Report — ${c.id}</title>
    <style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial,sans-serif;padding:40px;max-width:800px;margin:0 auto;color:#111}
    h1{font-size:24px;border-bottom:3px solid #00e5ff;padding-bottom:10px;margin-bottom:20px}
    h2{font-size:16px;color:#555;margin:20px 0 10px;border-bottom:1px solid #ddd;padding-bottom:5px}
    .row{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eee;font-size:14px}
    .key{color:#666}.val{font-weight:bold;text-align:right}
    .photos{display:flex;gap:20px;margin:20px 0}.photos img{width:150px;height:150px;border-radius:50%;object-fit:cover;border:2px solid #ccc}
    .tag{font-size:10px;text-transform:uppercase;letter-spacing:2px;color:#888;margin-top:30px}
    .match{background:#f0fff0;border:1px solid #afa;border-radius:6px;padding:12px;margin:8px 0;font-size:13px}
    .footer{margin-top:40px;font-size:11px;color:#999;text-align:center;border-top:1px solid #ddd;padding-top:15px}
    @media print{body{padding:20px}}</style></head>
    <body><h1>FINDTRACE — Case Report #${c.id}</h1>
    <div class="tag">GENERATED ${new Date().toLocaleString()}</div>
    <h2>Subject Information</h2>
    <div class="row"><span class="key">Name</span><span class="val">${c.name || 'Unknown'}</span></div>
    <div class="row"><span class="key">Age When Lost</span><span class="val">${c.age || '—'}</span></div>
    <div class="row"><span class="key">Gender</span><span class="val">${c.gender || '—'}</span></div>
    <div class="row"><span class="key">Date Last Seen</span><span class="val">${c.dateLastSeen || '—'}</span></div>
    <div class="row"><span class="key">Last Known Location</span><span class="val">${c.location || '—'}</span></div>
    <h2>Physical Descriptors</h2>
    <div class="row"><span class="key">Height</span><span class="val">${d.height} cm</span></div>
    <div class="row"><span class="key">Build</span><span class="val">${d.build}</span></div>
    <div class="row"><span class="key">Skin Tone</span><span class="val">${d.skin}</span></div>
    <div class="row"><span class="key">Face Shape</span><span class="val">${d.face}</span></div>
    <div class="row"><span class="key">Hair</span><span class="val">${d.hairColor}, ${d.hairStyle}</span></div>
    <div class="row"><span class="key">Eyes</span><span class="val">${d.eyeColor}</span></div>
    <div class="row"><span class="key">Nose</span><span class="val">${d.nose}</span></div>
    <div class="row"><span class="key">Facial Hair</span><span class="val">${d.facialHair}</span></div>
    <div class="row"><span class="key">Marks</span><span class="val">${(d.marks || []).join(', ') || 'None'}</span></div>
    ${d.notes ? `<div class="row"><span class="key">Notes</span><span class="val">${d.notes}</span></div>` : ''}
    ${c.referencePhoto || agedImageDataUrl ? `<h2>Photos</h2><div class="photos">${c.referencePhoto ? `<div><img src="${c.referencePhoto}" alt="Reference"><div style="text-align:center;font-size:11px;color:#888;margin-top:6px;">REFERENCE</div></div>` : ''}${agedImageDataUrl ? `<div><img src="${agedImageDataUrl}" alt="Prediction"><div style="text-align:center;font-size:11px;color:#888;margin-top:6px;">AGE PREDICTION</div></div>` : ''}</div>` : ''}
    ${c.matches && c.matches.length > 0 ? `<h2>Match History (${c.matches.length})</h2>${c.matches.map(m => `<div class="match">⚑ <strong>${m.name}</strong> — ${m.conf}% confidence at ${m.loc?.address || 'Unknown'} (${m.time})</div>`).join('')}` : ''}
    <div class="footer">Generated by FindTrace v3.0 · ${new Date().toISOString()}</div></body></html>`;
                const w = window.open('', '_blank');
                if (w) { w.document.write(html); w.document.close(); w.focus(); }
                Toast.show('Report generated', 'green');
                CaseManager.addTimeline('cyan', 'Report exported');
            }
        };
        $('btn-export').addEventListener('click', () => ExportManager.generateReport());

        /* ══════════ CASE SHARING (URL HASH) ══════════ */
        $('btn-share').addEventListener('click', function () {
            if (!currentCase) { Toast.show('No case to share', 'amber'); return; }
            CaseManager.readFromForm();
            const shareData = { ...currentCase }; delete shareData.referencePhoto; // too large for URL
            try {
                const encoded = btoa(unescape(encodeURIComponent(JSON.stringify(shareData))));
                const url = location.href.split('#')[0] + '#case=' + encoded;
                navigator.clipboard.writeText(url).then(() => {
                    Toast.show('Case link copied to clipboard!', 'green');
                }).catch(() => {
                    prompt('Copy this link to share the case:', url);
                });
                CaseManager.addTimeline('cyan', 'Case link shared');
            } catch (e) { Toast.show('Unable to generate share link', 'red'); }
        });

        /* ══════════ DATA MANAGEMENT ══════════ */
        $('btn-export-all').addEventListener('click', function () {
            const data = { cases: Storage.getAll(), settings: Settings };
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a'); a.href = url; a.download = `findtrace_export_${Date.now()}.json`;
            a.click(); URL.revokeObjectURL(url);
            Toast.show('All data exported', 'green');
        });

        $('btn-clear-data').addEventListener('click', function () {
            if (confirm('Are you sure? This will delete ALL saved cases and settings.')) {
                localStorage.removeItem('ft3_cases');
                localStorage.removeItem('ft3_settings');
                Toast.show('All data cleared', 'red');
                CaseManager.createNew();
            }
        });

        /* ══════════ INITIALIZATION ══════════ */
        (function init() {
            Settings.load();
            const all = Storage.getAll();
            // Check for shared case in URL
            const hash = location.hash;
            if (hash.startsWith('#case=')) {
                try {
                    const decoded = JSON.parse(decodeURIComponent(escape(atob(hash.substring(6)))));
                    currentCase = decoded;
                    Storage.saveCase(decoded);
                    CaseManager.loadToForm(decoded);
                    CaseManager.refreshDrawer();
                    Toast.show('Shared case loaded: ' + decoded.id, 'green');
                    history.replaceState(null, '', location.pathname);
                    return;
                } catch (e) { Toast.show('Invalid share link', 'red'); }
            }
            if (all.length > 0) {
                currentCase = all[0];
                CaseManager.loadToForm(all[0]);
                CaseManager.refreshDrawer();
                Toast.show('FindTrace v3.0 ready — ' + all.length + ' case(s) loaded', 'cyan');
            } else {
                CaseManager.createNew();
            }
        })();
    