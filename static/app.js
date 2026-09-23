document.addEventListener("DOMContentLoaded", () => {
    // -------------------------------------------------------------
    // DOM ELEMENTS
    // -------------------------------------------------------------
    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    // TTS Elements
    const ttsText = document.getElementById("tts-text");
    const charCount = document.getElementById("char-count");
    const filterLang = document.getElementById("tts-filter-lang");
    const filterGender = document.getElementById("tts-filter-gender");
    const filterEngine = document.getElementById("tts-filter-engine");
    const filterSearch = document.getElementById("tts-filter-search");
    const voiceMatchCount = document.getElementById("voice-match-count");
    const btnResetVoiceFilters = document.getElementById("btn-reset-voice-filters");
    const ttsVoice = document.getElementById("tts-voice");
    const btnPreviewVoice = document.getElementById("btn-preview-voice");
    const btnPreviewVoiceDetail = document.getElementById("btn-preview-voice-detail");
    const voiceDetailCard = document.getElementById("voice-detail-card");
    const voiceDetailTitle = document.getElementById("voice-detail-title");
    const voiceDetailCode = document.getElementById("voice-detail-code");
    const voiceTagList = document.getElementById("voice-tag-list");
    const voiceDetailLang = document.getElementById("voice-detail-lang");
    const voiceDetailGender = document.getElementById("voice-detail-gender");
    const voiceDetailEngine = document.getElementById("voice-detail-engine");
    const voiceDetailRid = document.getElementById("voice-detail-rid");
    const voiceDetailEngineHelp = document.getElementById("voice-detail-engine-help");
    const engineHelpActive = document.getElementById("engine-help-active");
    const rateSlider = document.getElementById("tts-rate-slider");
    const rateValue = document.getElementById("rate-value");
    const ttsPitchSlider = document.getElementById("tts-pitch-slider");
    const pitchValue = document.getElementById("pitch-value");
    const btnGenerateTts = document.getElementById("btn-generate-tts");
    const ttsResult = document.getElementById("tts-result");
    const audioPlayer = document.getElementById("audio-player");
    const btnDownloadAudio = document.getElementById("btn-download-audio");
    const ttsNeedTimestamp = document.getElementById("tts-need-timestamp");
    const btnDownloadSrtTts = document.getElementById("btn-download-srt-tts");
    const btnDownloadTxtTts = document.getElementById("btn-download-txt-tts");
    const ttsSubtitlesContainer = document.getElementById("tts-subtitles-container");
    const ttsSrtPreview = document.getElementById("tts-srt-preview");
    const btnUploadTtsFile = document.getElementById("btn-upload-tts-file");
    const ttsFileInput = document.getElementById("tts-file-input");
    const ttsProgressContainer = document.getElementById("tts-progress-container");
    const ttsProgressStatus = document.getElementById("tts-progress-status");
    const ttsProgressPercent = document.getElementById("tts-progress-percent");
    const ttsProgressBarFill = document.getElementById("tts-progress-bar-fill");

    // STT Elements
    const sttLang = document.getElementById("stt-lang");
    const sttTxtStyle = document.getElementById("stt-txt-style");
    const sttMergeCues = document.getElementById("stt-merge-cues");
    const sttMaxGap = document.getElementById("stt-max-gap");
    const sttMaxGapValue = document.getElementById("stt-max-gap-value");
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const selectedFileInfo = document.getElementById("selected-file-info");
    const fileName = document.getElementById("file-name");
    const fileSize = document.getElementById("file-size");
    const btnRemoveFile = document.getElementById("btn-remove-file");
    const btnTranscribe = document.getElementById("btn-transcribe");
    const progressContainer = document.getElementById("stt-progress-container");
    const progressStatus = document.getElementById("progress-status");
    const progressPercent = document.getElementById("progress-percent");
    const progressBarFill = document.getElementById("progress-bar-fill");
    const sttResult = document.getElementById("stt-result");
    const sttResultSummary = document.getElementById("stt-result-summary");
    const srtPreview = document.getElementById("srt-preview");
    const srtPreviewAlt = document.getElementById("srt-preview-alt");
    const btnDownloadSrt = document.getElementById("btn-download-srt");
    const btnDownloadTxt = document.getElementById("btn-download-txt");

    // TikTok Scraper Elements
    const tiktokUrl = document.getElementById("tiktok-url");
    const tiktokLang = document.getElementById("tiktok-lang");
    const tiktokLimit = document.getElementById("tiktok-limit");
    const tiktokLimitValue = document.getElementById("tiktok-limit-value");
    const tiktokLimitMode = document.getElementById("tiktok-limit-mode");
    const tiktokSliderRow = document.getElementById("tiktok-slider-row");
    const tiktokMinViews = document.getElementById("tiktok-min-views");
    const tiktokMinLikes = document.getElementById("tiktok-min-likes");
    const tiktokMinDuration = document.getElementById("tiktok-min-duration");
    const tiktokMaxDuration = document.getElementById("tiktok-max-duration");
    const tiktokPlaylistUrl = document.getElementById("tiktok-playlist-url");
    const btnScanPlaylists = document.getElementById("btn-scan-playlists");
    const tiktokPlaylistsDropdownContainer = document.getElementById("tiktok-playlists-dropdown-container");
    const tiktokPlaylistsDropdown = document.getElementById("tiktok-playlists-dropdown");
    const btnStartScraper = document.getElementById("btn-start-scraper");
    const btnExportCsv = document.getElementById("btn-export-csv");
    const tiktokConsoleCard = document.getElementById("tiktok-console-card");
    const consoleLogs = document.getElementById("console-logs");
    const btnDownloadZip = document.getElementById("btn-download-zip");

    // Script → Video VO elements
    const scriptText = document.getElementById("script-text");
    const scriptCharCount = document.getElementById("script-char-count");
    const scriptProjectName = document.getElementById("script-project-name");
    const scriptPresetSelect = document.getElementById("script-preset-select");
    const btnScriptSavePreset = document.getElementById("btn-script-save-preset");
    const btnScriptDeletePreset = document.getElementById("btn-script-delete-preset");
    const scriptSplitMode = document.getElementById("script-split-mode");
    const scriptMaxChars = document.getElementById("script-max-chars");
    const scriptMaxCharsValue = document.getElementById("script-max-chars-value");
    const scriptVoice = document.getElementById("script-voice");
    const scriptRate = document.getElementById("script-rate");
    const scriptRateValue = document.getElementById("script-rate-value");
    const scriptGapMs = document.getElementById("script-gap-ms");
    const scriptGapValue = document.getElementById("script-gap-value");
    const scriptNeedTimestamp = document.getElementById("script-need-timestamp");
    const btnScriptPreview = document.getElementById("btn-script-preview");
    const btnScriptRender = document.getElementById("btn-script-render");
    const scriptPreviewCard = document.getElementById("script-preview-card");
    const scriptPreviewList = document.getElementById("script-preview-list");
    const scriptPreviewSummary = document.getElementById("script-preview-summary");
    const scriptConsoleCard = document.getElementById("script-console-card");
    const scriptConsoleLogs = document.getElementById("script-console-logs");
    const scriptProgressLabel = document.getElementById("script-progress-label");
    const scriptProgressPercent = document.getElementById("script-progress-percent");
    const scriptProgressFill = document.getElementById("script-progress-fill");
    const btnScriptDownload = document.getElementById("btn-script-download");

    // Toast Notification
    const toast = document.getElementById("toast");

    let selectedFile = null;
    let srtContentData = "";
    let timestampedTxtData = "";
    let sttSourceFilename = "transcript";
    const PRESET_STORAGE_KEY = "capcut_script_voice_presets_v1";
    let scriptEventSource = null;

    // -------------------------------------------------------------
    // TAB SWITCHING
    // -------------------------------------------------------------
    tabButtons.forEach(button => {
        button.addEventListener("click", () => {
            const targetTab = button.getAttribute("data-tab");
            const targetElem = document.getElementById(targetTab);

            if (!targetElem) return;

            tabButtons.forEach(btn => btn.classList.remove("active"));
            tabContents.forEach(content => content.classList.remove("active"));

            button.classList.add("active");
            targetElem.classList.add("active");
        });
    });

    // -------------------------------------------------------------
    // TOAST HELPER
    // -------------------------------------------------------------
    function showToast(message, type = "success") {
        toast.textContent = message;
        toast.className = `toast show ${type}`;
        
        setTimeout(() => {
            toast.classList.remove("show");
        }, 4000);
    }

    // -------------------------------------------------------------
    // TEXT TO SPEECH (TTS) FLOW
    // -------------------------------------------------------------
    
    // Character Counter
    if (ttsText && charCount) {
        ttsText.addEventListener("input", () => {
            const count = ttsText.value.length;
            const chunks = Math.ceil(count / 4000);
            charCount.textContent = chunks > 1 ? `${count} kí tự (tự động chia làm ${chunks} luồng ghép audio)` : `${count} kí tự`;
        });
    }

    // Rate Slider value sync
    if (rateSlider && rateValue) {
        rateSlider.addEventListener("input", (e) => {
            rateValue.textContent = parseFloat(e.target.value).toFixed(1);
        });
    }

    // allVoicesByLang: { "vi-VN": [voiceObj, ...], ... }
    let allVoicesByLang = {};
    let voiceIndex = {}; // voice_type -> voiceObj
    let langLabelsMap = {};
    let voiceStats = null;
    let previewAudio = null;
    let lastSelectedVoiceType = null;

    const PREFERRED_LANG_ORDER = [
        "vi-VN", "en-US", "zh-CN", "zh-HK", "ja-JP", "ko-KR",
        "id-ID", "th-TH", "es-ES", "es-MX", "pt-BR", "fr-FR",
        "de-DE", "it-IT", "ms-MY", "ru-RU", "multi", "und"
    ];

    // Short copy for engine types (shown under filter + on voice detail)
    const ENGINE_HELP = {
        all: "Tất cả họ mã speaker. BV = classic ổn định; ICL = character/persona; DiT/Multi/SAMI = họ khác trên cùng pipeline TTS CapCut (SAMI).",
        BV: "BV — catalog classic (vd: BV074_streaming). Giọng đọc sạch, ổn định; hợp VO, tutorial, kịch bản dài, batch render.",
        ICL: "ICL — character/persona (vd: ICL_en_male_matthew). Biểu cảm hơn, dễ lọc lang/gender; hợp shorts, storytelling, vai diễn.",
        DiT: "DiT — mã DiT_… (Diffusion Transformer stack). Style/lang trong tên; cùng API TTS SAMI như BV/ICL.",
        Multi: "Multi — multi_…_bigtts. Một speaker đa ngôn ngữ tốt hơn BV đơn; hợp content nhiều ngôn ngữ.",
        SAMI: "SAMI/lang-prefix — en_male_…, zh_female_… (không BV/ICL). Vẫn TTS qua platform SAMI + resource_id.",
        Other: "Other — không khớp BV/ICL/DiT/Multi/SAMI. Nên nghe thử trước khi dùng hàng loạt."
    };

    function normalizeGender(g) {
        if (!g || g === "Unknown" || g === "") return "Khác";
        return g;
    }

    function updateEngineHelp(engineKey) {
        const key = engineKey || (filterEngine ? filterEngine.value : "all") || "all";
        const text = ENGINE_HELP[key] || ENGINE_HELP.all;
        if (engineHelpActive) {
            engineHelpActive.textContent = text;
        }
        document.querySelectorAll(".engine-legend-item").forEach((el) => {
            const eng = el.getAttribute("data-engine");
            if (key === "all") {
                el.classList.remove("is-active", "is-dimmed");
            } else if (eng === key) {
                el.classList.add("is-active");
                el.classList.remove("is-dimmed");
            } else {
                el.classList.add("is-dimmed");
                el.classList.remove("is-active");
            }
        });
    }

    function populateLangFilterOptions() {
        const prev = filterLang.value || "all";
        const keys = Object.keys(allVoicesByLang);
        keys.sort((a, b) => {
            const ia = PREFERRED_LANG_ORDER.indexOf(a);
            const ib = PREFERRED_LANG_ORDER.indexOf(b);
            if (ia === -1 && ib === -1) return a.localeCompare(b);
            if (ia === -1) return 1;
            if (ib === -1) return -1;
            return ia - ib;
        });

        filterLang.innerHTML = '<option value="all">Tất cả ngôn ngữ</option>';
        keys.forEach((lang) => {
            const count = (allVoicesByLang[lang] || []).length;
            const label = langLabelsMap[lang] || lang;
            const opt = document.createElement("option");
            opt.value = lang;
            opt.textContent = `${label} (${count})`;
            filterLang.appendChild(opt);
        });
        // restore if still valid
        if ([...filterLang.options].some((o) => o.value === prev)) {
            filterLang.value = prev;
        }
    }

    function getFilteredVoicesFlat() {
        const langFilter = filterLang.value;
        const genderFilter = filterGender.value;
        const engineFilter = filterEngine ? filterEngine.value : "all";
        const q = (filterSearch ? filterSearch.value : "").trim().toLowerCase();

        const out = [];
        for (const [langKey, voices] of Object.entries(allVoicesByLang)) {
            if (langFilter !== "all" && langKey !== langFilter) continue;
            for (const voice of voices) {
                const gender = normalizeGender(voice.gender);
                if (genderFilter !== "all" && gender !== genderFilter) continue;
                if (engineFilter !== "all" && (voice.engine || "Other") !== engineFilter) continue;
                if (q) {
                    const hay = [
                        voice.display_name,
                        voice.voice_type,
                        voice.option_label,
                        voice.lang_label,
                        gender,
                        voice.engine,
                        ...(voice.styles || []),
                        ...(voice.tags || [])
                    ].join(" ").toLowerCase();
                    if (!hay.includes(q)) continue;
                }
                out.push(voice);
            }
        }
        return out;
    }

    function renderFilteredVoices() {
        const filtered = getFilteredVoicesFlat();
        const prevSelected = ttsVoice.value || lastSelectedVoiceType;

        ttsVoice.innerHTML = "";

        // group for optgroups
        const byLang = {};
        filtered.forEach((v) => {
            const lang = v.lang || "und";
            if (!byLang[lang]) byLang[lang] = [];
            byLang[lang].push(v);
        });

        const langKeys = Object.keys(byLang).sort((a, b) => {
            const ia = PREFERRED_LANG_ORDER.indexOf(a);
            const ib = PREFERRED_LANG_ORDER.indexOf(b);
            if (ia === -1 && ib === -1) return a.localeCompare(b);
            if (ia === -1) return 1;
            if (ib === -1) return -1;
            return ia - ib;
        });

        let hasSelected = false;
        langKeys.forEach((langKey) => {
            const group = document.createElement("optgroup");
            const label = langLabelsMap[langKey] || langKey;
            group.label = `${label} (${byLang[langKey].length})`;

            byLang[langKey].forEach((voice) => {
                const option = document.createElement("option");
                option.value = voice.voice_type;
                option.textContent = voice.option_label || `${voice.display_name} - ${voice.voice_type} | ${voice.lang || langKey}`;
                option.dataset.lang = langKey;
                option.dataset.name = voice.display_name || voice.voice_type;
                option.dataset.gender = normalizeGender(voice.gender);
                option.dataset.engine = voice.engine || "";
                if (voice.voice_type === prevSelected || voice.voice_type === "BV074_streaming") {
                    // prefer previous selection; BV074 only if nothing else later selected
                }
                if (voice.voice_type === prevSelected) {
                    option.selected = true;
                    hasSelected = true;
                }
                group.appendChild(option);
            });
            ttsVoice.appendChild(group);
        });

        // Always set selected value correctly
        const validPrev = prevSelected && [...ttsVoice.options].some((o) => o.value === prevSelected);
        if (validPrev) {
            ttsVoice.value = prevSelected;
        } else if (filtered.length > 0) {
            const bv = filtered.find((v) => v.voice_type === "BV074_streaming");
            const pick = bv || filtered[0];
            ttsVoice.value = pick.voice_type;
        }
        lastSelectedVoiceType = ttsVoice.value;

        if (voiceMatchCount) {
            const total = voiceStats ? voiceStats.total : Object.values(allVoicesByLang).reduce((n, a) => n + a.length, 0);
            voiceMatchCount.textContent = filtered.length
                ? `Hiển thị ${filtered.length} / ${total} giọng`
                : `Không có giọng khớp bộ lọc (tổng ${total})`;
        }

        if (filtered.length === 0) {
            ttsVoice.innerHTML = `<option value="" disabled selected>Không tìm thấy giọng đọc nào khớp bộ lọc</option>`;
            if (voiceDetailCard) voiceDetailCard.classList.add("hidden");
            return;
        }

        updateVoiceDetailCard();
    }

    function updateVoiceDetailCard() {
        if (!voiceDetailCard) return;
        const vt = ttsVoice.value;
        const voice = voiceIndex[vt];
        if (!voice) {
            voiceDetailCard.classList.add("hidden");
            return;
        }
        lastSelectedVoiceType = vt;
        voiceDetailCard.classList.remove("hidden");
        if (voiceDetailTitle) voiceDetailTitle.textContent = voice.display_name || vt;
        if (voiceDetailCode) voiceDetailCode.textContent = vt;
        if (voiceDetailLang) voiceDetailLang.textContent = voice.lang_label || voice.lang || "—";
        if (voiceDetailGender) voiceDetailGender.textContent = normalizeGender(voice.gender);
        if (voiceDetailEngine) voiceDetailEngine.textContent = voice.engine || "—";
        if (voiceDetailRid) voiceDetailRid.textContent = voice.resource_id || "—";
        if (voiceDetailEngineHelp) {
            const eng = voice.engine || "Other";
            const help = ENGINE_HELP[eng];
            if (help) {
                voiceDetailEngineHelp.textContent = help;
                voiceDetailEngineHelp.classList.remove("hidden");
            } else {
                voiceDetailEngineHelp.classList.add("hidden");
            }
        }

        if (voiceTagList) {
            voiceTagList.innerHTML = "";
            const tags = voice.tags && voice.tags.length
                ? voice.tags
                : [voice.lang_label, normalizeGender(voice.gender), voice.engine].filter(Boolean);
            tags.forEach((tag) => {
                const span = document.createElement("span");
                span.className = "voice-tag";
                if (tag === "Nam" || tag === "Nữ" || tag === "Trẻ em" || tag === "Khác") {
                    span.classList.add("tag-gender");
                } else if (["BV", "ICL", "DiT", "Multi", "SAMI", "Other"].includes(tag)) {
                    span.classList.add("tag-engine");
                } else if ((voice.lang_label && tag === voice.lang_label) || tag === voice.lang) {
                    span.classList.add("tag-lang");
                } else {
                    span.classList.add("tag-style");
                }
                span.textContent = tag;
                voiceTagList.appendChild(span);
            });
        }
    }

    // Fetch Voice List
    async function loadVoices() {
        try {
            const response = await fetch("/api/voices");
            if (!response.ok) throw new Error("Không thể tải danh sách giọng đọc");

            const data = await response.json();

            // Backward compatible: old API returned { lang: [voices] } only
            if (data.languages) {
                allVoicesByLang = data.languages;
                langLabelsMap = data.lang_labels || {};
                voiceStats = data.stats || null;
            } else {
                allVoicesByLang = data;
                langLabelsMap = {};
                voiceStats = null;
            }

            voiceIndex = {};
            Object.values(allVoicesByLang).forEach((list) => {
                (list || []).forEach((v) => {
                    // normalize legacy fields
                    if (!v.option_label) {
                        v.option_label = `${v.display_name || v.voice_type} - ${v.voice_type} | ${v.lang || 'und'}`;
                    }
                    if (!v.lang && v.lang !== "") {
                        // find lang from grouping key later
                    }
                    voiceIndex[v.voice_type] = v;
                });
            });
            // attach lang from group key if missing
            Object.entries(allVoicesByLang).forEach(([lang, list]) => {
                (list || []).forEach((v) => {
                    if (!v.lang) v.lang = lang;
                    if (!v.lang_label) v.lang_label = langLabelsMap[lang] || lang;
                    voiceIndex[v.voice_type] = v;
                });
            });

            populateLangFilterOptions();
            renderFilteredVoices();
            populateScriptVoiceSelect();
        } catch (error) {
            console.error(error);
            showToast("Lỗi khi tải danh sách giọng đọc từ server", "error");
            ttsVoice.innerHTML = `<option value="BV074_streaming" selected>Cô Gái Hoạt Ngôn (Default)</option>`;
            if (voiceMatchCount) voiceMatchCount.textContent = "Không tải được danh sách giọng";
        }
    }

    // Dialogue Tab Elements
    const dialogueText = document.getElementById("dialogue-text");
    const dialogueCharCount = document.getElementById("dialogue-char-count");
    const btnUploadDialogueFile = document.getElementById("btn-upload-dialogue-file");
    const dialogueFileInput = document.getElementById("dialogue-file-input");
    const dialogueRateSlider = document.getElementById("dialogue-rate-slider");
    const dialogueRateValue = document.getElementById("dialogue-rate-value");
    const dialoguePitchSlider = document.getElementById("dialogue-pitch-slider");
    const dialoguePitchValue = document.getElementById("dialogue-pitch-value");
    const dialogueNeedTimestamp = document.getElementById("dialogue-need-timestamp");
    const btnGenerateDialogue = document.getElementById("btn-generate-dialogue");
    const dialogueResult = document.getElementById("dialogue-result");
    const dialogueAudioPlayer = document.getElementById("dialogue-audio-player");
    const btnDownloadDialogueAudio = document.getElementById("btn-download-dialogue-audio");
    const btnDownloadSrtDialogue = document.getElementById("btn-download-srt-dialogue");
    const btnDownloadTxtDialogue = document.getElementById("btn-download-txt-dialogue");
    const dialogueSubtitlesContainer = document.getElementById("dialogue-subtitles-container");
    const dialogueSrtPreview = document.getElementById("dialogue-srt-preview");
    const dialogueProgressContainer = document.getElementById("dialogue-progress-container");
    const dialogueProgressStatus = document.getElementById("dialogue-progress-status");
    const dialogueProgressPercent = document.getElementById("dialogue-progress-percent");
    const dialogueProgressBarFill = document.getElementById("dialogue-progress-bar-fill");

    // Dual Voice Config Elements
    const dualVoiceConfigCard = document.getElementById("dual-voice-config-card");
    const dualChar1Name = document.getElementById("dual-char-1-name");
    const dualChar1Lang = document.getElementById("dual-char-1-lang");
    const dualChar1Gender = document.getElementById("dual-char-1-gender");
    const dualChar1Voice = document.getElementById("dual-char-1-voice");
    const dualChar2Name = document.getElementById("dual-char-2-name");
    const dualChar2Lang = document.getElementById("dual-char-2-lang");
    const dualChar2Gender = document.getElementById("dual-char-2-gender");
    const dualChar2Voice = document.getElementById("dual-char-2-voice");

    // File Upload Handler for TTS Tab
    if (btnUploadTtsFile && ttsFileInput) {
        btnUploadTtsFile.addEventListener("click", () => {
            ttsFileInput.click();
        });

        ttsFileInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const ext = file.name.split('.').pop().toLowerCase();
            if (ext !== 'txt' && ext !== 'md') {
                showToast("Vui lòng chọn file dạng .txt hoặc .md!", "error");
                return;
            }

            const reader = new FileReader();
            reader.onload = (event) => {
                const text = event.target.result;
                ttsText.value = text;
                const chunks = Math.ceil(text.length / 4000);
                charCount.textContent = chunks > 1 ? `${text.length} kí tự (tự động chia làm ${chunks} luồng ghép audio)` : `${text.length} kí tự`;
                showToast(`Đã tải kịch bản từ file ${file.name}!`);
            };
            reader.onerror = () => {
                showToast("Lỗi khi đọc nội dung file", "error");
            };
            reader.readAsText(file, "UTF-8");
            ttsFileInput.value = "";
        });
    }

    if (ttsText && charCount) {
        ttsText.addEventListener("input", () => {
            const len = ttsText.value.length;
            const chunks = Math.ceil(len / 4000);
            charCount.textContent = chunks > 1 ? `${len} kí tự (tự động chia làm ${chunks} luồng ghép audio)` : `${len} kí tự`;
        });
    }

    // File Upload Handler for Dialogue Tab
    if (btnUploadDialogueFile && dialogueFileInput) {
        btnUploadDialogueFile.addEventListener("click", () => {
            dialogueFileInput.click();
        });

        dialogueFileInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const ext = file.name.split('.').pop().toLowerCase();
            if (ext !== 'txt' && ext !== 'md') {
                showToast("Vui lòng chọn file dạng .txt hoặc .md!", "error");
                return;
            }

            const reader = new FileReader();
            reader.onload = (event) => {
                const text = event.target.result;
                if (dialogueText) {
                    dialogueText.value = text;
                    if (dialogueCharCount) dialogueCharCount.textContent = `${text.length} kí tự`;
                }
                showToast(`Đã tải kịch bản từ file ${file.name}!`);
            };
            reader.onerror = () => {
                showToast("Lỗi khi đọc nội dung file", "error");
            };
            reader.readAsText(file, "UTF-8");
            dialogueFileInput.value = "";
        });
    }

    if (dialogueText && dialogueCharCount) {
        dialogueText.addEventListener("input", () => {
            dialogueCharCount.textContent = `${dialogueText.value.length} kí tự`;
        });
    }

    if (dialogueRateSlider && dialogueRateValue) {
        dialogueRateSlider.addEventListener("input", (e) => {
            dialogueRateValue.textContent = parseFloat(e.target.value).toFixed(1);
        });
    }

    function populateDualLangFilterOptions() {
        const langSelects = [dualChar1Lang, dualChar2Lang].filter(Boolean);
        if (!langSelects.length) return;

        const keys = Object.keys(allVoicesByLang || {});
        keys.sort((a, b) => {
            const ia = PREFERRED_LANG_ORDER.indexOf(a);
            const ib = PREFERRED_LANG_ORDER.indexOf(b);
            if (ia === -1 && ib === -1) return a.localeCompare(b);
            if (ia === -1) return 1;
            if (ib === -1) return -1;
            return ia - ib;
        });

        langSelects.forEach((sel) => {
            const prev = sel.value || "vi-VN";
            sel.innerHTML = '<option value="all">Tất cả ngôn ngữ</option>';
            keys.forEach((lang) => {
                const count = (allVoicesByLang[lang] || []).length;
                const label = langLabelsMap[lang] || lang;
                const opt = document.createElement("option");
                opt.value = lang;
                opt.textContent = `${label} (${count})`;
                sel.appendChild(opt);
            });
            if ([...sel.options].some((o) => o.value === prev)) {
                sel.value = prev;
            } else if ([...sel.options].some((o) => o.value === "vi-VN")) {
                sel.value = "vi-VN";
            }
        });
    }

    function filterVoicesForCharacter(langValue, genderValue) {
        const out = [];
        for (const [langKey, voices] of Object.entries(allVoicesByLang || {})) {
            if (langValue !== "all" && langKey !== langValue) continue;
            for (const voice of voices) {
                const gender = normalizeGender(voice.gender);
                if (genderValue !== "all" && gender !== genderValue) continue;
                out.push(voice);
            }
        }
        return out;
    }

    function renderDualVoiceChar1() {
        if (!dualChar1Voice) return;
        const langVal = dualChar1Lang ? dualChar1Lang.value : "all";
        const genderVal = dualChar1Gender ? dualChar1Gender.value : "all";
        const filtered = filterVoicesForCharacter(langVal, genderVal);
        const prev = dualChar1Voice.value;

        dualChar1Voice.innerHTML = "";
        if (!filtered.length) {
            dualChar1Voice.innerHTML = '<option value="" disabled selected>Không có giọng khớp bộ lọc</option>';
            return;
        }

        filtered.forEach((v) => {
            const opt = document.createElement("option");
            opt.value = v.voice_type;
            opt.textContent = v.option_label || v.display_name || v.voice_type;
            dualChar1Voice.appendChild(opt);
        });

        if (prev && [...dualChar1Voice.options].some((o) => o.value === prev)) {
            dualChar1Voice.value = prev;
        } else if (filtered.length > 0) {
            dualChar1Voice.value = filtered[0].voice_type;
        }
    }

    function renderDualVoiceChar2() {
        if (!dualChar2Voice) return;
        const langVal = dualChar2Lang ? dualChar2Lang.value : "all";
        const genderVal = dualChar2Gender ? dualChar2Gender.value : "all";
        const filtered = filterVoicesForCharacter(langVal, genderVal);
        const prev = dualChar2Voice.value;

        dualChar2Voice.innerHTML = "";
        if (!filtered.length) {
            dualChar2Voice.innerHTML = '<option value="" disabled selected>Không có giọng khớp bộ lọc</option>';
            return;
        }

        filtered.forEach((v) => {
            const opt = document.createElement("option");
            opt.value = v.voice_type;
            opt.textContent = v.option_label || v.display_name || v.voice_type;
            dualChar2Voice.appendChild(opt);
        });

        if (prev && [...dualChar2Voice.options].some((o) => o.value === prev)) {
            dualChar2Voice.value = prev;
        } else if (filtered.length > 0) {
            dualChar2Voice.value = filtered[0].voice_type;
        }
    }

    if (dualChar1Lang) dualChar1Lang.addEventListener("change", renderDualVoiceChar1);
    if (dualChar1Gender) dualChar1Gender.addEventListener("change", renderDualVoiceChar1);
    if (dualChar2Lang) dualChar2Lang.addEventListener("change", renderDualVoiceChar2);
    if (dualChar2Gender) dualChar2Gender.addEventListener("change", renderDualVoiceChar2);

    function populateScriptVoiceSelect() {
        // Populate Dual Voice language filters and render options regardless of scriptVoice
        populateDualLangFilterOptions();
        renderDualVoiceChar1();
        renderDualVoiceChar2();

        if (!scriptVoice) return;
        const prev = scriptVoice.value || "BV074_streaming";
        scriptVoice.innerHTML = "";

        const preferred = ["vi-VN", "en-US", "zh-CN", "ja-JP", "ko-KR"];
        const langs = Object.keys(allVoicesByLang || {}).sort((a, b) => {
            const ia = preferred.indexOf(a);
            const ib = preferred.indexOf(b);
            if (ia === -1 && ib === -1) return a.localeCompare(b);
            if (ia === -1) return 1;
            if (ib === -1) return -1;
            return ia - ib;
        });

        langs.forEach((lang) => {
            const group = document.createElement("optgroup");
            group.label = langLabelsMap[lang] || lang;

            (allVoicesByLang[lang] || []).forEach((v) => {
                const opt = document.createElement("option");
                opt.value = v.voice_type;
                opt.textContent = v.option_label || v.display_name || v.voice_type;

                group.appendChild(opt.cloneNode(true));
            });

            if (group.children.length) scriptVoice.appendChild(group);
        });

        if ([...scriptVoice.options].some((o) => o.value === prev)) {
            scriptVoice.value = prev;
        } else if ([...scriptVoice.options].some((o) => o.value === "BV074_streaming")) {
            scriptVoice.value = "BV074_streaming";
        }

        // Set default voices for character 1 and character 2 if not set
        if (dualChar1Voice && (!dualChar1Voice.value || dualChar1Voice.value === "")) {
            const bvMale = Object.values(allVoicesByLang["vi-VN"] || []).find(v => v.gender === "Nam" || v.voice_type.includes("075") || v.voice_type.includes("562"));
            if (bvMale) dualChar1Voice.value = bvMale.voice_type;
        }
        if (dualChar2Voice && (!dualChar2Voice.value || dualChar2Voice.value === "")) {
            const bvFemale = Object.values(allVoicesByLang["vi-VN"] || []).find(v => v.voice_type === "BV074_streaming" || v.gender === "Nữ");
            if (bvFemale) dualChar2Voice.value = bvFemale.voice_type;
        }
    }

    // Listen to changes on filters
    if (filterLang) filterLang.addEventListener("change", () => { lastSelectedVoiceType = null; renderFilteredVoices(); });
    if (filterGender) filterGender.addEventListener("change", () => { lastSelectedVoiceType = null; renderFilteredVoices(); });
    if (filterEngine) {
        filterEngine.addEventListener("change", () => {
            lastSelectedVoiceType = null;
            updateEngineHelp(filterEngine.value);
            renderFilteredVoices();
        });
        updateEngineHelp(filterEngine.value || "all");
    }
    // Click a legend row to set engine filter
    document.querySelectorAll(".engine-legend-item").forEach((el) => {
        el.addEventListener("click", () => {
            const eng = el.getAttribute("data-engine");
            if (!filterEngine || !eng) return;
            lastSelectedVoiceType = null;
            filterEngine.value = eng;
            updateEngineHelp(eng);
            renderFilteredVoices();
        });
    });
    if (filterSearch) {
        let searchTimer = null;
        filterSearch.addEventListener("input", () => {
            clearTimeout(searchTimer);
            lastSelectedVoiceType = null;
            searchTimer = setTimeout(renderFilteredVoices, 180);
        });
    }
    if (btnResetVoiceFilters) {
        btnResetVoiceFilters.addEventListener("click", () => {
            filterLang.value = "all";
            filterGender.value = "all";
            if (filterEngine) filterEngine.value = "all";
            if (filterSearch) filterSearch.value = "";
            updateEngineHelp("all");
            renderFilteredVoices();
        });
    }
    if (ttsVoice) {
        ttsVoice.addEventListener("change", () => {
            lastSelectedVoiceType = ttsVoice.value;
            updateVoiceDetailCard();
        });
    }

    async function previewSelectedVoice(triggerBtn) {
        const selectedOption = ttsVoice.options[ttsVoice.selectedIndex];
        if (!selectedOption || !selectedOption.value) {
            showToast("Vui lòng chọn giọng đọc để nghe thử!", "error");
            return;
        }

        const voiceType = selectedOption.value;
        const voice = voiceIndex[voiceType] || {};
        const lang = selectedOption.dataset.lang || voice.lang || "en-US";
        const cleanName = selectedOption.dataset.name || voice.display_name || voiceType;

        const previewTexts = {
            "vi-VN": "Xin chào, tôi là giọng đọc ",
            "en-US": "Hello, I am ",
            "zh-CN": "你好，我是 ",
            "zh-HK": "你好，我是 ",
            "ja-JP": "こんにちは、私は ",
            "ko-KR": "안녕하세요, 저는 ",
            "id-ID": "Halo, saya adalah suara ",
            "th-TH": "สวัสดี ฉันคือเสียง ",
            "es-ES": "Hola, soy la voz ",
            "es-MX": "Hola, soy la voz ",
            "pt-BR": "Olá, eu sou a voz ",
            "fr-FR": "Bonjour, je suis la voix ",
            "de-DE": "Hallo, ich bin die Stimme ",
            "multi": "Hello, I am "
        };

        const prefix = previewTexts[lang] || "Hello, I am ";
        const previewText = `${prefix}${cleanName}`;

        if (previewAudio) {
            previewAudio.pause();
            previewAudio = null;
        }

        const buttons = [btnPreviewVoice, btnPreviewVoiceDetail].filter(Boolean);
        buttons.forEach((b) => {
            b.disabled = true;
            if (b === triggerBtn || !triggerBtn) b.textContent = "⏳ Đang tải...";
        });

        try {
            const response = await fetch("/api/tts", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: previewText,
                    voice: voiceType,
                    rate: parseFloat(rateSlider.value) || 1.0,
                    pitch: ttsPitchSlider ? parseInt(ttsPitchSlider.value) || 0 : 0
                })
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "Không thể tạo âm thanh thử nghiệm");

            previewAudio = new Audio(data.speech_url);
            buttons.forEach((b) => {
                if (b === triggerBtn || !triggerBtn) b.textContent = "🔊 Đang đọc...";
            });

            const restore = () => {
                buttons.forEach((b) => {
                    b.disabled = false;
                    b.textContent = "🔊 Nghe thử";
                });
                previewAudio = null;
            };

            previewAudio.addEventListener("ended", restore);
            previewAudio.addEventListener("error", () => {
                showToast("Lỗi khi phát âm thanh nghe thử", "error");
                restore();
            });

            await previewAudio.play();
        } catch (error) {
            console.error(error);
            showToast(`Lỗi nghe thử: ${error.message}`, "error");
            buttons.forEach((b) => {
                b.disabled = false;
                b.textContent = "🔊 Nghe thử";
            });
        }
    }

    btnPreviewVoice.addEventListener("click", () => previewSelectedVoice(btnPreviewVoice));
    if (btnPreviewVoiceDetail) {
        btnPreviewVoiceDetail.addEventListener("click", () => previewSelectedVoice(btnPreviewVoiceDetail));
    }

    if (ttsPitchSlider && pitchValue) {
        ttsPitchSlider.addEventListener("input", (e) => {
            const val = parseInt(e.target.value);
            pitchValue.textContent = val > 0 ? `+${val}` : `${val}`;
        });
    }

    if (dialoguePitchSlider && dialoguePitchValue) {
        dialoguePitchSlider.addEventListener("input", (e) => {
            const val = parseInt(e.target.value);
            dialoguePitchValue.textContent = val > 0 ? `+${val}` : `${val}`;
        });
    }

    // Single TTS submit handler
    btnGenerateTts.addEventListener("click", async () => {
        const text = ttsText.value.trim();
        const voice = ttsVoice.value;
        const rate = parseFloat(rateSlider.value);
        const pitch = ttsPitchSlider ? parseInt(ttsPitchSlider.value) || 0 : 0;
        const need_timestamp = ttsNeedTimestamp.checked;

        if (!text) {
            showToast("Vui lòng nhập văn bản cần đọc!", "error");
            return;
        }

        // UI Loading state
        btnGenerateTts.disabled = true;
        btnGenerateTts.querySelector(".btn-text").textContent = "Đang xử lý...";
        btnGenerateTts.querySelector(".btn-loader").classList.remove("hidden");
        ttsResult.classList.add("hidden");
        
        // Reset and Show Progress Bar
        if (ttsProgressContainer) {
            ttsProgressContainer.classList.remove("hidden");
            ttsProgressStatus.textContent = "Đang kết nối CapCut AI TTS...";
            ttsProgressPercent.textContent = "20%";
            ttsProgressBarFill.style.width = "20%";
        }

        // Hide subtitles by default
        ttsSubtitlesContainer.classList.add("hidden");
        btnDownloadSrtTts.classList.add("hidden");
        if (btnDownloadTxtTts) btnDownloadTxtTts.classList.add("hidden");

        let progressInterval = setInterval(() => {
            if (ttsProgressBarFill) {
                let currentPct = parseInt(ttsProgressBarFill.style.width) || 20;
                if (currentPct < 90) {
                    currentPct += 10;
                    ttsProgressBarFill.style.width = `${currentPct}%`;
                    ttsProgressPercent.textContent = `${currentPct}%`;
                    ttsProgressStatus.textContent = currentPct > 60 ? "Đang ghép nối âm thanh..." : "Đang tạo giọng nói AI...";
                }
            }
        }, 500);

        try {
            const response = await fetch("/api/tts", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ text, voice, rate, pitch, need_timestamp })
            });

            clearInterval(progressInterval);
            if (ttsProgressBarFill) {
                ttsProgressBarFill.style.width = "100%";
                ttsProgressPercent.textContent = "100%";
                ttsProgressStatus.textContent = "Hoàn thành!";
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Không thể tạo giọng nói AI");
            }

            // On Success
            showToast("Tạo giọng nói AI thành công!");
            audioPlayer.src = data.speech_url;
            btnDownloadAudio.href = data.speech_url;
            
            // Generate filename based on first 15 chars of text
            const cleanText = text.substring(0, 15).replace(/[^\w\s\d]/gi, '').trim().replace(/\s+/g, '-');
            const downloadName = `tts-${cleanText || "audio"}.mp3`;
            btnDownloadAudio.setAttribute("download", downloadName);

            // Handle subtitles/timestamps if generated
            if (data.srt) {
                ttsSrtPreview.textContent = data.srt;
                ttsSubtitlesContainer.classList.remove("hidden");
                
                const srtBlob = new Blob([data.srt], { type: "text/srt;charset=utf-8" });
                const srtUrl = URL.createObjectURL(srtBlob);
                btnDownloadSrtTts.href = srtUrl;
                btnDownloadSrtTts.setAttribute("download", `tts-${cleanText || "audio"}.srt`);
                btnDownloadSrtTts.classList.remove("hidden");

                // TXT format download button
                const txtBlob = new Blob([data.srt], { type: "text/plain;charset=utf-8" });
                const txtUrl = URL.createObjectURL(txtBlob);
                if (btnDownloadTxtTts) {
                    btnDownloadTxtTts.href = txtUrl;
                    btnDownloadTxtTts.setAttribute("download", `tts-${cleanText || "audio"}.txt`);
                    btnDownloadTxtTts.classList.remove("hidden");
                }
            }

            ttsResult.classList.remove("hidden");
            audioPlayer.play();
        } catch (error) {
            clearInterval(progressInterval);
            if (ttsProgressStatus) ttsProgressStatus.textContent = "Lỗi xử lý!";
            console.error(error);
            showToast(`Lỗi: ${error.message}`, "error");
        } finally {
            setTimeout(() => {
                if (ttsProgressContainer) ttsProgressContainer.classList.add("hidden");
            }, 1200);

            // Restore button state
            btnGenerateTts.disabled = false;
            btnGenerateTts.querySelector(".btn-text").textContent = "Tạo Giọng Nói AI";
            btnGenerateTts.querySelector(".btn-loader").classList.add("hidden");
        }
    });

    // Dialogue 2 Voices submit handler
    if (btnGenerateDialogue) {
        btnGenerateDialogue.addEventListener("click", async () => {
            const text = dialogueText ? dialogueText.value.trim() : "";
            const rate = dialogueRateSlider ? parseFloat(dialogueRateSlider.value) : 1.0;
            const pitch = dialoguePitchSlider ? parseInt(dialoguePitchSlider.value) || 0 : 0;
            const need_timestamp = dialogueNeedTimestamp ? dialogueNeedTimestamp.checked : false;

            if (!text) {
                showToast("Vui lòng nhập kịch bản đối thoại!", "error");
                return;
            }

            // UI Loading state
            btnGenerateDialogue.disabled = true;
            btnGenerateDialogue.querySelector(".btn-text").textContent = "Đang tạo hội thoại 2 giọng...";
            btnGenerateDialogue.querySelector(".btn-loader").classList.remove("hidden");
            if (dialogueResult) dialogueResult.classList.add("hidden");
            
            if (dialogueProgressContainer) {
                dialogueProgressContainer.classList.remove("hidden");
                dialogueProgressStatus.textContent = "Đang kết nối 2 giọng nói AI...";
                dialogueProgressPercent.textContent = "25%";
                dialogueProgressBarFill.style.width = "25%";
            }

            if (dialogueSubtitlesContainer) dialogueSubtitlesContainer.classList.add("hidden");
            if (btnDownloadSrtDialogue) btnDownloadSrtDialogue.classList.add("hidden");
            if (btnDownloadTxtDialogue) btnDownloadTxtDialogue.classList.add("hidden");

            let dialogueInterval = setInterval(() => {
                if (dialogueProgressBarFill) {
                    let currentPct = parseInt(dialogueProgressBarFill.style.width) || 25;
                    if (currentPct < 90) {
                        currentPct += 15;
                        dialogueProgressBarFill.style.width = `${currentPct}%`;
                        dialogueProgressPercent.textContent = `${currentPct}%`;
                        dialogueProgressStatus.textContent = currentPct > 60 ? "Đang ghép nối lượt thoại đối thoại..." : "Đang xử lý tạo từng giọng nói...";
                    }
                }
            }, 600);

            try {
                const reqBody = {
                    text,
                    char1_name: dualChar1Name ? dualChar1Name.value.trim() : "Hùng",
                    char1_voice: dualChar1Voice ? dualChar1Voice.value : "BV074_streaming",
                    char2_name: dualChar2Name ? dualChar2Name.value.trim() : "Lan",
                    char2_voice: dualChar2Voice ? dualChar2Voice.value : "BV074_streaming",
                    rate,
                    pitch,
                    need_timestamp
                };

                const response = await fetch("/api/tts-dialogue", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(reqBody)
                });

                clearInterval(dialogueInterval);
                if (dialogueProgressBarFill) {
                    dialogueProgressBarFill.style.width = "100%";
                    dialogueProgressPercent.textContent = "100%";
                    dialogueProgressStatus.textContent = "Hoàn tất đối thoại!";
                }

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || "Không thể tạo giọng nói đối thoại");
                }

                // On Success
                showToast(`Tạo kịch bản đối thoại (${data.turn_count || 2} lượt) thành công!`);
                if (dialogueAudioPlayer) dialogueAudioPlayer.src = data.speech_url;
                if (btnDownloadDialogueAudio) btnDownloadDialogueAudio.href = data.speech_url;
                
                const cleanText = text.substring(0, 15).replace(/[^\w\s\d]/gi, '').trim().replace(/\s+/g, '-');
                const downloadName = `dialogue-${cleanText || "audio"}.mp3`;
                if (btnDownloadDialogueAudio) btnDownloadDialogueAudio.setAttribute("download", downloadName);

                // Handle subtitles/timestamps if generated
                if (data.srt && dialogueSrtPreview) {
                    dialogueSrtPreview.textContent = data.srt;
                    if (dialogueSubtitlesContainer) dialogueSubtitlesContainer.classList.remove("hidden");
                    
                    const srtBlob = new Blob([data.srt], { type: "text/srt;charset=utf-8" });
                    const srtUrl = URL.createObjectURL(srtBlob);
                    if (btnDownloadSrtDialogue) {
                        btnDownloadSrtDialogue.href = srtUrl;
                        btnDownloadSrtDialogue.setAttribute("download", `dialogue-${cleanText || "audio"}.srt`);
                        btnDownloadSrtDialogue.classList.remove("hidden");
                    }

                    // TXT format download button
                    const txtBlob = new Blob([data.srt], { type: "text/plain;charset=utf-8" });
                    const txtUrl = URL.createObjectURL(txtBlob);
                    if (btnDownloadTxtDialogue) {
                        btnDownloadTxtDialogue.href = txtUrl;
                        btnDownloadTxtDialogue.setAttribute("download", `dialogue-${cleanText || "audio"}.txt`);
                        btnDownloadTxtDialogue.classList.remove("hidden");
                    }
                }

                if (dialogueResult) dialogueResult.classList.remove("hidden");
                if (dialogueAudioPlayer) dialogueAudioPlayer.play();
            } catch (error) {
                clearInterval(dialogueInterval);
                if (dialogueProgressStatus) dialogueProgressStatus.textContent = "Lỗi xử lý!";
                console.error(error);
                showToast(`Lỗi đối thoại: ${error.message}`, "error");
            } finally {
                setTimeout(() => {
                    if (dialogueProgressContainer) dialogueProgressContainer.classList.add("hidden");
                }, 1200);

                // Restore button state
                btnGenerateDialogue.disabled = false;
                btnGenerateDialogue.querySelector(".btn-text").textContent = "Tạo Giọng Nói Đối Thoại";
                btnGenerateDialogue.querySelector(".btn-loader").classList.add("hidden");
            }
        });
    }

    // -------------------------------------------------------------
    // SPEECH TO TEXT (STT) FLOW
    // -------------------------------------------------------------

    if (sttMaxGap && sttMaxGapValue) {
        sttMaxGap.addEventListener("input", () => {
            sttMaxGapValue.textContent = sttMaxGap.value;
        });
    }

    // Drag & Drop handlers
    ["dragenter", "dragover"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add("dragover");
        }, false);
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove("dragover");
        }, false);
    });

    dropZone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleSelectedFile(files[0]);
        }
    });

    dropZone.addEventListener("click", () => {
        fileInput.click();
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleSelectedFile(e.target.files[0]);
        }
    });

    function handleSelectedFile(file) {
        const validTypes = ["audio/", "video/"];
        const isCompatible = validTypes.some(type => file.type.startsWith(type)) ||
                             /\.(mp3|mp4|m4a|wav|aac|flac|ogg|webm|mov|avi|mkv)$/i.test(file.name);

        if (!isCompatible) {
            showToast("Định dạng không hợp lệ! Hỗ trợ MP3, WAV, M4A, MP4, MOV, AVI, MKV...", "error");
            return;
        }

        // Limit size to 200MB (backend auto-extracts audio stream using FFmpeg)
        if (file.size > 200 * 1024 * 1024) {
            showToast("Dung lượng file tối đa là 200MB!", "error");
            return;
        }

        selectedFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = formatBytes(file.size);
        sttSourceFilename = file.name;

        // Show info panel
        selectedFileInfo.classList.remove("hidden");
        dropZone.classList.add("hidden");

        // Enable button
        btnTranscribe.disabled = false;

        // Hide previous result
        sttResult.classList.add("hidden");
        timestampedTxtData = "";
        srtContentData = "";
    }

    btnRemoveFile.addEventListener("click", () => {
        resetSttState();
    });

    function resetSttState() {
        selectedFile = null;
        fileInput.value = "";
        selectedFileInfo.classList.add("hidden");
        dropZone.classList.remove("hidden");
        btnTranscribe.disabled = true;
        progressContainer.classList.add("hidden");
        sttResult.classList.add("hidden");
        srtContentData = "";
        timestampedTxtData = "";
        if (sttResultSummary) sttResultSummary.textContent = "";
        if (srtPreviewAlt) srtPreviewAlt.textContent = "";
    }

    function downloadTextFile(content, filename, mime) {
        const blob = new Blob([content], { type: mime || "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function baseNameFromUpload() {
        const origName = selectedFile ? selectedFile.name : sttSourceFilename || "transcript";
        return origName.replace(/\.[^.]+$/, "") || "transcript";
    }

    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // Transcribe / timestamp Button Click
    btnTranscribe.addEventListener("click", () => {
        if (!selectedFile) return;

        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("language", sttLang ? sttLang.value : "auto");
        formData.append("txt_style", sttTxtStyle ? sttTxtStyle.value : "start");
        formData.append("merge_cues", sttMergeCues && sttMergeCues.checked ? "true" : "false");
        formData.append("max_gap_ms", sttMaxGap ? String(sttMaxGap.value) : "450");
        formData.append("max_chars", "100");

        // UI Updates
        btnTranscribe.disabled = true;
        btnRemoveFile.disabled = true;
        btnTranscribe.querySelector(".btn-text").textContent = "Đang xử lý...";
        btnTranscribe.querySelector(".btn-loader").classList.remove("hidden");

        progressContainer.classList.remove("hidden");
        sttResult.classList.add("hidden");

        progressStatus.textContent = "Đang chuẩn bị file để tải lên...";
        updateProgressBar(0);

        // Use XMLHttpRequest to track upload progress
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/stt", true);

        // Upload progress listener
        xhr.upload.addEventListener("progress", (e) => {
            if (e.lengthComputable) {
                const percentComplete = Math.round((e.loaded / e.total) * 100);
                // Keep 95% limit for upload, last 5% is processing
                const progressVal = Math.min(Math.round(percentComplete * 0.95), 95);
                updateProgressBar(progressVal);
                progressStatus.textContent = `Đang tải file lên máy chủ CapCut... (${percentComplete}%)`;
            }
        });

        // Response listener
        xhr.onload = function() {
            btnTranscribe.disabled = false;
            btnRemoveFile.disabled = false;
            btnTranscribe.querySelector(".btn-text").textContent = "Tạo timestamp từ audio";
            btnTranscribe.querySelector(".btn-loader").classList.add("hidden");

            if (xhr.status === 200) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    if (data.status === "success") {
                        updateProgressBar(100);
                        progressStatus.textContent = "Hoàn thành tạo timestamp!";
                        showToast("Đã tạo transcript + timestamp!");

                        srtContentData = data.srt || "";
                        timestampedTxtData = data.timestamped_txt || "";
                        if (data.source_filename) sttSourceFilename = data.source_filename;

                        // Main preview = timestamped TXT (what user asked for)
                        if (!timestampedTxtData.trim()) {
                            srtPreview.textContent = "[Không phát hiện lời thoại nào trong file này]";
                        } else {
                            srtPreview.textContent = timestampedTxtData;
                        }
                        if (srtPreviewAlt) {
                            srtPreviewAlt.textContent = srtContentData.trim()
                                ? srtContentData
                                : "[Không có SRT]";
                        }
                        if (sttResultSummary) {
                            const n = data.line_count != null ? data.line_count : (timestampedTxtData.split("\n").filter(Boolean).length);
                            const raw = data.raw_utterance_count != null ? data.raw_utterance_count : n;
                            const dur = data.duration_ms ? ` · ~${(data.duration_ms / 1000).toFixed(1)}s` : "";
                            const mergeNote = data.merge_cues
                                ? ` · gộp ${raw} cue → ${n} câu`
                                : ` · ${n} câu (không gộp)`;
                            sttResultSummary.textContent = `${n} dòng timestamp${mergeNote}${dur}`;
                        }

                        sttResult.classList.remove("hidden");
                    } else {
                        throw new Error("Lỗi không xác định từ máy chủ");
                    }
                } catch (e) {
                    showToast(`Lỗi phân tích kết quả: ${e.message}`, "error");
                    progressStatus.textContent = "Gặp lỗi khi xử lý kết quả.";
                }
            } else {
                let errMsg = "Lỗi kết nối máy chủ";
                try {
                    const resJson = JSON.parse(xhr.responseText);
                    errMsg = resJson.detail || errMsg;
                } catch (e) {}
                showToast(`Lỗi trích xuất: ${errMsg}`, "error");
                progressStatus.textContent = "Gặp lỗi trong quá trình bóc băng.";
            }
        };

        xhr.onerror = function() {
            btnTranscribe.disabled = false;
            btnRemoveFile.disabled = false;
            btnTranscribe.querySelector(".btn-text").textContent = "Tạo timestamp từ audio";
            btnTranscribe.querySelector(".btn-loader").classList.add("hidden");
            showToast("Lỗi kết nối mạng, vui lòng kiểm tra lại server.", "error");
            progressStatus.textContent = "Lỗi kết nối mạng.";
        };

        // Fake processing step after upload reaches 100% (95% displayed)
        // Since backend processing of STT with CapCut can take a few seconds
        let waitInterval = setInterval(() => {
            const currentWidth = parseFloat(progressBarFill.style.width);
            if (currentWidth >= 95 && currentWidth < 99) {
                progressBarFill.style.width = (currentWidth + 0.5) + "%";
                progressPercent.textContent = Math.round(currentWidth + 0.5) + "%";
                progressStatus.textContent = "AI CapCut đang nhận diện & gắn timestamp (có thể mất vài giây)...";
            }
        }, 1000);

        xhr.onloadend = function() {
            clearInterval(waitInterval);
        };

        xhr.send(formData);
    });

    function updateProgressBar(percent) {
        progressBarFill.style.width = percent + "%";
        progressPercent.textContent = percent + "%";
    }

    function downloadTextFile(content, filename, mimeType = "text/plain;charset=utf-8") {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    function baseNameFromUpload() {
        if (!sttSourceFilename) return "transcript";
        return sttSourceFilename.replace(/\.[^/.]+$/, "");
    }

    // Download timestamped TXT (primary)
    if (btnDownloadTxt) {
        btnDownloadTxt.addEventListener("click", () => {
            if (!timestampedTxtData || !timestampedTxtData.trim()) {
                showToast("Chưa có nội dung TXT để tải", "error");
                return;
            }
            downloadTextFile(timestampedTxtData, `${baseNameFromUpload()}_timestamped.txt`, "text/plain;charset=utf-8");
            showToast("Đã tải file TXT timestamp");
        });
    }

    // Client-side Download SRT File
    if (btnDownloadSrt) {
        btnDownloadSrt.addEventListener("click", () => {
            if (!srtContentData || !srtContentData.trim()) {
                showToast("Chưa có SRT để tải", "error");
                return;
            }
            downloadTextFile(srtContentData, `${baseNameFromUpload()}.srt`, "text/plain;charset=utf-8");
        });
    }

    // -------------------------------------------------------------
    // TIKTOK SCRAPER FLOW
    // -------------------------------------------------------------
    // Toggle slider visibility based on download mode
    tiktokLimitMode.addEventListener("change", () => {
        if (tiktokLimitMode.value === "all") {
            tiktokSliderRow.classList.add("hidden");
        } else {
            tiktokSliderRow.classList.remove("hidden");
        }
    });

    // Sync slider value
    tiktokLimit.addEventListener("input", (e) => {
        tiktokLimitValue.textContent = e.target.value;
    });

    // Scan Playlists event listener
    btnScanPlaylists.addEventListener("click", async () => {
        const channelUrl = tiktokUrl.value.trim();
        if (!channelUrl) {
            showToast("Vui lòng nhập đường dẫn kênh TikTok để quét danh sách phát!", "error");
            return;
        }

        btnScanPlaylists.disabled = true;
        btnScanPlaylists.querySelector(".btn-text").textContent = "Đang quét...";
        btnScanPlaylists.querySelector(".btn-loader").classList.remove("hidden");

        try {
            const response = await fetch("/api/tiktok/playlists", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ channel_url: channelUrl })
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || "Không thể quét danh sách phát");
            }

            // Clear previous options
            tiktokPlaylistsDropdown.innerHTML = '<option value="">-- Chọn danh sách phát --</option>';

            if (data.playlists && data.playlists.length > 0) {
                data.playlists.forEach(pl => {
                    const option = document.createElement("option");
                    option.value = pl.url;
                    option.textContent = `${pl.title} (${pl.count} video)`;
                    tiktokPlaylistsDropdown.appendChild(option);
                });
                tiktokPlaylistsDropdownContainer.classList.remove("hidden");
                showToast(`Đã tìm thấy ${data.playlists.length} danh sách phát!`);
            } else {
                tiktokPlaylistsDropdownContainer.classList.add("hidden");
                showToast("Không tìm thấy danh sách phát nào công khai trên kênh này.", "warning");
            }
        } catch (error) {
            console.error(error);
            showToast(`Lỗi: ${error.message}`, "error");
        } finally {
            btnScanPlaylists.disabled = false;
            btnScanPlaylists.querySelector(".btn-text").textContent = "🔍 Quét danh sách phát";
            btnScanPlaylists.querySelector(".btn-loader").classList.add("hidden");
        }
    });

    // Dropdown change listener
    tiktokPlaylistsDropdown.addEventListener("change", (e) => {
        const selectedUrl = e.target.value;
        if (selectedUrl) {
            tiktokPlaylistUrl.value = selectedUrl;
            showToast("Đã chọn danh sách phát. Nhấn 'Xuất danh sách' hoặc 'Bắt đầu cào' để tiến hành.");
        } else {
            tiktokPlaylistUrl.value = "";
        }
    });

    let scraperEventSource = null;

    // Start extraction (batch transcription) click handler
    btnStartScraper.addEventListener("click", async () => {
        const urlVal = tiktokUrl.value.trim();
        const playlistUrlVal = tiktokPlaylistUrl.value.trim();
        const langVal = tiktokLang.value;
        const limitVal = parseInt(tiktokLimit.value);
        const limitModeVal = tiktokLimitMode.value;
        
        const minViewsVal = parseInt(tiktokMinViews.value) || 0;
        const minLikesVal = parseInt(tiktokMinLikes.value) || 0;
        const minDurationVal = parseInt(tiktokMinDuration.value) || 0;
        const maxDurationVal = parseInt(tiktokMaxDuration.value) || 0;

        if (!urlVal && !playlistUrlVal) {
            showToast("Vui lòng nhập đường dẫn kênh hoặc danh sách phát TikTok!", "error");
            return;
        }

        // Clean up previous event source if active
        if (scraperEventSource) {
            scraperEventSource.close();
            scraperEventSource = null;
        }

        // Reset UI
        btnStartScraper.disabled = true;
        btnExportCsv.disabled = true;
        btnStartScraper.querySelector(".btn-text").textContent = "Đang xử lý...";
        btnStartScraper.querySelector(".btn-loader").classList.remove("hidden");
        
        tiktokConsoleCard.classList.remove("hidden");
        btnDownloadZip.classList.add("hidden");
        consoleLogs.textContent = "Đang kết nối tới server...\n";

        try {
            const response = await fetch("/api/tiktok/extract", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    channel_url: urlVal,
                    playlist_url: playlistUrlVal,
                    language: langVal,
                    limit: limitVal,
                    limit_mode: limitModeVal,
                    min_views: minViewsVal,
                    min_likes: minLikesVal,
                    min_duration: minDurationVal,
                    max_duration: maxDurationVal
                })
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || "Không thể khởi tạo tiến trình cào kênh");
            }

            const taskId = data.task_id;
            consoleLogs.textContent += `Khởi tạo task thành công. ID: ${taskId}\nĐang mở luồng EventSource nhận log tiến trình...\n`;

            // Connect to EventSource
            scraperEventSource = new EventSource(`/api/tiktok/progress/${taskId}`);
            const consoleBox = document.querySelector(".console-box");

            scraperEventSource.onmessage = (event) => {
                try {
                    const eventData = JSON.parse(event.data);
                    
                    if (eventData.log) {
                        consoleLogs.textContent += eventData.log + "\n";
                        // Scroll to bottom
                        if (consoleBox) {
                            consoleBox.scrollTop = consoleBox.scrollHeight;
                        }
                    }

                    if (eventData.done) {
                        scraperEventSource.close();
                        scraperEventSource = null;

                        // Restore UI state
                        btnStartScraper.disabled = false;
                        btnExportCsv.disabled = false;
                        btnStartScraper.querySelector(".btn-text").textContent = "Bắt đầu cào & Trích kịch bản";
                        btnStartScraper.querySelector(".btn-loader").classList.add("hidden");

                        if (eventData.status === "completed") {
                            showToast("Trích xuất kịch bản TikTok thành công!");
                            btnDownloadZip.href = eventData.download_url;
                            btnDownloadZip.classList.remove("hidden");
                        } else {
                            showToast("Quá trình cào kênh bị lỗi hoặc thất bại!", "error");
                        }
                    }
                } catch (e) {
                    console.error("Error parsing EventSource data:", e);
                }
            };

            scraperEventSource.onerror = (err) => {
                console.error("EventSource error:", err);
                consoleLogs.textContent += "❌ Lỗi kết nối luồng SSE từ máy chủ.\n";
                if (scraperEventSource) {
                    scraperEventSource.close();
                    scraperEventSource = null;
                }
                
                btnStartScraper.disabled = false;
                btnExportCsv.disabled = false;
                btnStartScraper.querySelector(".btn-text").textContent = "Bắt đầu cào & Trích kịch bản";
                btnStartScraper.querySelector(".btn-loader").classList.add("hidden");
                showToast("Mất kết nối với tiến trình cào kênh!", "error");
            };

        } catch (error) {
            console.error(error);
            consoleLogs.textContent += `❌ Lỗi: ${error.message}\n`;
            btnStartScraper.disabled = false;
            btnExportCsv.disabled = false;
            btnStartScraper.querySelector(".btn-text").textContent = "Bắt đầu cào & Trích kịch bản";
            btnStartScraper.querySelector(".btn-loader").classList.add("hidden");
            showToast(`Lỗi: ${error.message}`, "error");
        }
    });

    // Export CSV click handler
    btnExportCsv.addEventListener("click", async () => {
        const urlVal = tiktokUrl.value.trim();
        const playlistUrlVal = tiktokPlaylistUrl.value.trim();
        const minViewsVal = parseInt(tiktokMinViews.value) || 0;
        const minLikesVal = parseInt(tiktokMinLikes.value) || 0;
        const minDurationVal = parseInt(tiktokMinDuration.value) || 0;
        const maxDurationVal = parseInt(tiktokMaxDuration.value) || 0;

        if (!urlVal && !playlistUrlVal) {
            showToast("Vui lòng nhập đường dẫn kênh hoặc danh sách phát TikTok!", "error");
            return;
        }

        // Reset UI
        btnStartScraper.disabled = true;
        btnExportCsv.disabled = true;
        btnExportCsv.querySelector(".btn-text").textContent = "Đang quét...";
        btnExportCsv.querySelector(".btn-loader").classList.remove("hidden");
        
        tiktokConsoleCard.classList.remove("hidden");
        btnDownloadZip.classList.add("hidden");
        consoleLogs.textContent = "Đang tải danh sách video (quá trình này có thể mất vài giây)...\n";

        try {
            const response = await fetch("/api/tiktok/list", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    channel_url: urlVal,
                    playlist_url: playlistUrlVal
                })
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || "Không thể tải danh sách video");
            }

            consoleLogs.textContent += "✅ Đã tải xong danh sách của kênh. Tiến hành lọc...\n";
            
            // Client-side filtering
            const filteredVideos = data.videos.filter(v => {
                if (minViewsVal && v.view_count < minViewsVal) return false;
                if (minLikesVal && v.like_count < minLikesVal) return false;
                if (minDurationVal && v.duration < minDurationVal) return false;
                if (maxDurationVal && v.duration > maxDurationVal) return false;
                return true;
            });

            consoleLogs.textContent += `- Tổng số video cào được: ${data.videos.length}\n`;
            consoleLogs.textContent += `- Số video khớp bộ lọc: ${filteredVideos.length}\n`;

            if (filteredVideos.length === 0) {
                consoleLogs.textContent += "⚠️ Không tìm thấy video nào khớp bộ lọc để xuất danh sách.\n";
                showToast("Không tìm thấy video nào khớp bộ lọc!", "error");
                
                btnStartScraper.disabled = false;
                btnExportCsv.disabled = false;
                btnExportCsv.querySelector(".btn-text").textContent = "Xuất danh sách (.csv)";
                btnExportCsv.querySelector(".btn-loader").classList.add("hidden");
                return;
            }

            // Generate CSV (with UTF-8 BOM for MS Excel compatibility)
            let csvContent = "\uFEFF";
            csvContent += "ID Video,Tiêu đề,Đường dẫn,Thời lượng (giây),Lượt xem,Lượt thích,Bình luận,Chia sẻ,Ngày đăng\n";

            filteredVideos.forEach(v => {
                const dateStr = v.timestamp ? new Date(v.timestamp * 1000).toLocaleDateString("vi-VN") : "N/A";
                const escapedTitle = `"${v.title.replace(/"/g, '""')}"`;
                csvContent += `${v.id},${escapedTitle},${v.url},${v.duration},${v.view_count},${v.like_count},${v.comment_count},${v.repost_count},${dateStr}\n`;
            });

            // Trigger download
            const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
            const csvUrl = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = csvUrl;
            
            const uploader = filteredVideos[0]?.uploader || "tiktok";
            a.download = `tiktok_videos_${uploader}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(csvUrl);

            consoleLogs.textContent += "🎉 Đã xuất và tải xuống file danh sách CSV thành công!\n";
            showToast("Xuất danh sách CSV thành công!");

        } catch (error) {
            console.error(error);
            consoleLogs.textContent += `❌ Lỗi: ${error.message}\n`;
            showToast(`Lỗi: ${error.message}`, "error");
        } finally {
            // Restore buttons
            btnStartScraper.disabled = false;
            btnExportCsv.disabled = false;
            btnExportCsv.querySelector(".btn-text").textContent = "Xuất danh sách (.csv)";
            btnExportCsv.querySelector(".btn-loader").classList.add("hidden");
        }
    });

    // -------------------------------------------------------------
    // SCRIPT → VIDEO VO (multi-scene TTS)
    // -------------------------------------------------------------
    function loadPresets() {
        try {
            return JSON.parse(localStorage.getItem(PRESET_STORAGE_KEY) || "{}") || {};
        } catch (e) {
            return {};
        }
    }

    function savePresets(map) {
        localStorage.setItem(PRESET_STORAGE_KEY, JSON.stringify(map));
    }

    function refreshPresetSelect() {
        if (!scriptPresetSelect) return;
        const presets = loadPresets();
        const prev = scriptPresetSelect.value;
        scriptPresetSelect.innerHTML = '<option value="">— Chọn preset đã lưu —</option>';
        Object.keys(presets).sort().forEach((name) => {
            const opt = document.createElement("option");
            opt.value = name;
            opt.textContent = name;
            scriptPresetSelect.appendChild(opt);
        });
        if (prev && presets[prev]) scriptPresetSelect.value = prev;
    }

    function applyPreset(name) {
        const presets = loadPresets();
        const p = presets[name];
        if (!p) return;
        if (scriptProjectName && p.project_name) scriptProjectName.value = p.project_name;
        if (scriptSplitMode && p.split_mode) scriptSplitMode.value = p.split_mode;
        if (scriptMaxChars && p.max_chars) {
            scriptMaxChars.value = p.max_chars;
            if (scriptMaxCharsValue) scriptMaxCharsValue.textContent = p.max_chars;
        }
        if (scriptVoice && p.voice) scriptVoice.value = p.voice;
        if (scriptRate && p.rate != null) {
            scriptRate.value = p.rate;
            if (scriptRateValue) scriptRateValue.textContent = Number(p.rate).toFixed(1);
        }
        if (scriptGapMs && p.gap_ms != null) {
            scriptGapMs.value = p.gap_ms;
            if (scriptGapValue) scriptGapValue.textContent = p.gap_ms;
        }
        if (scriptNeedTimestamp) scriptNeedTimestamp.checked = !!p.need_timestamp;
        showToast(`Đã áp dụng preset "${name}"`);
    }

    function collectScriptOptions() {
        return {
            script: (scriptText && scriptText.value) || "",
            project_name: (scriptProjectName && scriptProjectName.value.trim()) || "script_project",
            voice: (scriptVoice && scriptVoice.value) || "BV074_streaming",
            rate: scriptRate ? parseFloat(scriptRate.value) : 1.0,
            split_mode: (scriptSplitMode && scriptSplitMode.value) || "auto",
            max_chars: scriptMaxChars ? parseInt(scriptMaxChars.value, 10) : 400,
            gap_ms: scriptGapMs ? parseInt(scriptGapMs.value, 10) : 300,
            need_timestamp: !!(scriptNeedTimestamp && scriptNeedTimestamp.checked)
        };
    }

    if (scriptText) {
        scriptText.addEventListener("input", () => {
            if (scriptCharCount) scriptCharCount.textContent = `${scriptText.value.length} ký tự`;
        });
    }
    if (scriptMaxChars) {
        scriptMaxChars.addEventListener("input", () => {
            if (scriptMaxCharsValue) scriptMaxCharsValue.textContent = scriptMaxChars.value;
        });
    }
    if (scriptRate) {
        scriptRate.addEventListener("input", () => {
            if (scriptRateValue) scriptRateValue.textContent = parseFloat(scriptRate.value).toFixed(1);
        });
    }
    if (scriptGapMs) {
        scriptGapMs.addEventListener("input", () => {
            if (scriptGapValue) scriptGapValue.textContent = scriptGapMs.value;
        });
    }

    refreshPresetSelect();

    if (scriptPresetSelect) {
        scriptPresetSelect.addEventListener("change", () => {
            if (scriptPresetSelect.value) applyPreset(scriptPresetSelect.value);
        });
    }

    if (btnScriptSavePreset) {
        btnScriptSavePreset.addEventListener("click", () => {
            const name = prompt("Tên preset:", (scriptProjectName && scriptProjectName.value) || "preset_1");
            if (!name || !name.trim()) return;
            const presets = loadPresets();
            const opts = collectScriptOptions();
            presets[name.trim()] = {
                project_name: opts.project_name,
                voice: opts.voice,
                rate: opts.rate,
                split_mode: opts.split_mode,
                max_chars: opts.max_chars,
                gap_ms: opts.gap_ms,
                need_timestamp: opts.need_timestamp
            };
            savePresets(presets);
            refreshPresetSelect();
            scriptPresetSelect.value = name.trim();
            showToast(`Đã lưu preset "${name.trim()}"`);
        });
    }

    if (btnScriptDeletePreset) {
        btnScriptDeletePreset.addEventListener("click", () => {
            const name = scriptPresetSelect && scriptPresetSelect.value;
            if (!name) {
                showToast("Chọn preset cần xóa trước", "error");
                return;
            }
            const presets = loadPresets();
            delete presets[name];
            savePresets(presets);
            refreshPresetSelect();
            showToast(`Đã xóa preset "${name}"`);
        });
    }

    if (btnScriptPreview) {
        btnScriptPreview.addEventListener("click", async () => {
            const opts = collectScriptOptions();
            if (!opts.script.trim()) {
                showToast("Vui lòng dán kịch bản!", "error");
                return;
            }
            btnScriptPreview.disabled = true;
            btnScriptPreview.querySelector(".btn-text").textContent = "Đang phân tích...";
            btnScriptPreview.querySelector(".btn-loader").classList.remove("hidden");
            try {
                const res = await fetch("/api/script/preview", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(opts)
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Preview failed");

                scriptPreviewCard.classList.remove("hidden");
                scriptPreviewSummary.textContent =
                    `${data.scene_count} cảnh · ${data.segment_count} đoạn TTS · ${data.total_chars} ký tự`;
                scriptPreviewList.innerHTML = "";
                (data.segments || []).forEach((seg) => {
                    const el = document.createElement("div");
                    el.className = "script-seg-item";
                    const previewText = (seg.text || "").length > 220
                        ? seg.text.slice(0, 220) + "…"
                        : (seg.text || "");
                    el.innerHTML = `
                        <header>
                            <div class="seg-title">#${seg.index} · ${escapeHtml(seg.title || "")}</div>
                            <div class="seg-meta">${seg.char_count || 0} ký tự</div>
                        </header>
                        <div class="seg-body">${escapeHtml(previewText)}</div>
                    `;
                    scriptPreviewList.appendChild(el);
                });
                showToast("Đã tách đoạn kịch bản");
            } catch (e) {
                console.error(e);
                showToast(`Lỗi preview: ${e.message}`, "error");
            } finally {
                btnScriptPreview.disabled = false;
                btnScriptPreview.querySelector(".btn-text").textContent = "👁️ Xem trước tách đoạn";
                btnScriptPreview.querySelector(".btn-loader").classList.add("hidden");
            }
        });
    }

    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    if (btnScriptRender) {
        btnScriptRender.addEventListener("click", async () => {
            const opts = collectScriptOptions();
            if (!opts.script.trim()) {
                showToast("Vui lòng dán kịch bản!", "error");
                return;
            }

            if (scriptEventSource) {
                scriptEventSource.close();
                scriptEventSource = null;
            }

            btnScriptRender.disabled = true;
            btnScriptPreview.disabled = true;
            btnScriptRender.querySelector(".btn-text").textContent = "Đang render...";
            btnScriptRender.querySelector(".btn-loader").classList.remove("hidden");

            scriptConsoleCard.classList.remove("hidden");
            btnScriptDownload.classList.add("hidden");
            scriptConsoleLogs.textContent = "Khởi tạo job render...\n";
            scriptProgressLabel.textContent = "Đang xếp hàng...";
            scriptProgressPercent.textContent = "0%";
            scriptProgressFill.style.width = "0%";

            try {
                const res = await fetch("/api/script/render", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(opts)
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Không tạo được job render");

                const taskId = data.task_id;
                scriptConsoleLogs.textContent += `Task ID: ${taskId}\n`;
                scriptEventSource = new EventSource(`/api/script/progress/${taskId}`);

                scriptEventSource.onmessage = (event) => {
                    try {
                        const ev = JSON.parse(event.data);
                        if (ev.log) {
                            scriptConsoleLogs.textContent += ev.log + "\n";
                            const box = scriptConsoleLogs.parentElement;
                            if (box) box.scrollTop = box.scrollHeight;
                        }
                        if (ev.total) {
                            const pct = Math.min(100, Math.round(((ev.done || 0) / ev.total) * 100));
                            scriptProgressFill.style.width = pct + "%";
                            scriptProgressPercent.textContent = pct + "%";
                            scriptProgressLabel.textContent = `Đoạn ${ev.done || 0}/${ev.total}`;
                        }
                        if (ev.finished) {
                            scriptEventSource.close();
                            scriptEventSource = null;
                            btnScriptRender.disabled = false;
                            btnScriptPreview.disabled = false;
                            btnScriptRender.querySelector(".btn-text").textContent = "🎬 Render TTS → ZIP";
                            btnScriptRender.querySelector(".btn-loader").classList.add("hidden");

                            if (ev.status === "completed") {
                                scriptProgressFill.style.width = "100%";
                                scriptProgressPercent.textContent = "100%";
                                scriptProgressLabel.textContent = "Hoàn tất";
                                btnScriptDownload.href = ev.download_url;
                                btnScriptDownload.classList.remove("hidden");
                                showToast("Render kịch bản thành công — tải ZIP!");
                            } else {
                                scriptProgressLabel.textContent = "Thất bại";
                                showToast(ev.error || "Render thất bại", "error");
                            }
                        }
                    } catch (err) {
                        console.error(err);
                    }
                };

                scriptEventSource.onerror = () => {
                    if (scriptEventSource) {
                        scriptEventSource.close();
                        scriptEventSource = null;
                    }
                    btnScriptRender.disabled = false;
                    btnScriptPreview.disabled = false;
                    btnScriptRender.querySelector(".btn-text").textContent = "🎬 Render TTS → ZIP";
                    btnScriptRender.querySelector(".btn-loader").classList.add("hidden");
                    scriptConsoleLogs.textContent += "❌ Mất kết nối SSE\n";
                    showToast("Mất kết nối tiến trình render", "error");
                };
            } catch (e) {
                console.error(e);
                showToast(`Lỗi: ${e.message}`, "error");
                btnScriptRender.disabled = false;
                btnScriptPreview.disabled = false;
                btnScriptRender.querySelector(".btn-text").textContent = "🎬 Render TTS → ZIP";
                btnScriptRender.querySelector(".btn-loader").classList.add("hidden");
            }
        });
    }

    // Initialize voices loading
    loadVoices();
});
