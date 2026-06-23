/* ================================================================
   content-display.js — Shared rich content display logic
   Used by: main/detail.html, users/goods_detail.html, users/product_detail.html
   ================================================================ */

(function() {
    'use strict';

    var langNames = {
        'javascript': 'JavaScript', 'js': 'JavaScript', 'typescript': 'TypeScript', 'ts': 'TypeScript',
        'python': 'Python', 'py': 'Python', 'css': 'CSS', 'html': 'HTML', 'markup': 'HTML',
        'json': 'JSON', 'bash': 'Bash', 'sh': 'Bash', 'shell': 'Bash', 'sql': 'SQL',
        'php': 'PHP', 'java': 'Java', 'csharp': 'C#', 'cs': 'C#', 'c': 'C', 'cpp': 'C++',
        'rust': 'Rust', 'go': 'Go', 'ruby': 'Ruby', 'rb': 'Ruby', 'swift': 'Swift',
        'kotlin': 'Kotlin', 'kt': 'Kotlin', 'yaml': 'YAML', 'yml': 'YAML', 'markdown': 'Markdown',
        'md': 'Markdown', 'dockerfile': 'Docker', 'nginx': 'Nginx', 'xml': 'XML',
        'scss': 'SCSS', 'sass': 'Sass', 'less': 'Less', 'graphql': 'GraphQL',
        'toml': 'TOML', 'ini': 'INI', 'properties': 'Properties'
    };

    function detectLanguage(code) {
        var t = code.trim();
        if (/^\s*\{[\s\S]*:\s*[\s\S]*\}/.test(t) && /"[^"]+"\s*:/.test(t)) return 'json';
        if (/^\s*<(!DOCTYPE|html|head|body|div|span|p|a|img|ul|ol|li|table|form|input|button|script|style|link|meta|h[1-6])\b/i.test(t)) return 'html';
        if (/^\s*<!DOCTYPE\s+html/i.test(t)) return 'html';
        if (/^\s*#include\s*[<"]/.test(t)) return 'c';
        if (/^\s*import\s+[\s\S]+from\s+['"]/.test(t)) return 'typescript';
        if (/\bfunction\s+\w+\s*\(/.test(t) || /=>\s*\{/.test(t) || /const\s+\w+\s*=/.test(t) || /let\s+\w+\s*=/.test(t) || /var\s+\w+\s*=/.test(t)) return 'javascript';
        if (/^\s*(def|class)\s+\w+/.test(t)) return 'python';
        if (/^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\s/i.test(t)) return 'sql';
        if (/^\s*(fn|let|mut|pub|impl|struct|enum|use|mod)\s/.test(t)) return 'rust';
        if (/^\s*(func|package|import)\s/.test(t)) return 'go';
        if (/^\s*server\s*\{/.test(t) || /listen\s+\d+/.test(t)) return 'nginx';
        if (/^\s*(FROM|RUN|COPY|CMD|ENTRYPOINT|EXPOSE|ENV)\s/.test(t)) return 'dockerfile';
        if (/<\?php/.test(t)) return 'php';
        if (/^\s*\[[\w.-]+\]/.test(t) && /^\s*\w+\s*=/.test(t.split('\n')[1] || '')) return 'ini';
        if (/^\s*\w+\s*=\s*[\w{]/.test(t) && !/[;{}]/.test(t)) return 'yaml';
        return 'javascript';
    }

    function svgCopy() {
        return '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
    }

    function svgCode() {
        return '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>';
    }

    function getCode(block) {
        var lines = block.querySelectorAll('.ql-code-block');
        if (lines.length > 0) {
            return Array.from(lines).map(function(el) {
                return el.innerHTML.replace(/<br\s*\/?>/gi, '').replace(/<[^>]+>/g, '');
            }).join('\n');
        }
        var codeEl = block.querySelector('code') || block;
        var raw = codeEl.innerHTML || codeEl.textContent || '';
        return raw.replace(/<br\s*\/?>/gi, '\n').replace(/<[^>]+>/g, '');
    }

    function enhanceCodeBlocks(root) {
        var selector = '.pre-content .ql-code-block-container, .pre-content pre:not(.code-enhanced)';
        var blocks = (root || document).querySelectorAll(selector);
        blocks.forEach(function(block) {
            if (block.classList.contains('code-enhanced')) return;
            block.classList.add('code-enhanced');

            var code = getCode(block);
            var lang = detectLanguage(code);
            var langLabel = langNames[lang] || lang.toUpperCase();

            var wrapper = document.createElement('div');
            wrapper.className = 'code-block-wrapper';

            var header = document.createElement('div');
            header.className = 'code-block-header';
            header.innerHTML =
                '<span class="code-block-lang">' + svgCode() + ' ' + langLabel + '</span>' +
                '<button type="button" class="code-block-copy" data-code="' + encodeURIComponent(code) + '">' +
                svgCopy() + ' Копировать</button>';

            var body = document.createElement('div');
            body.className = 'code-block-body';

            var pre = document.createElement('pre');
            pre.className = 'language-' + lang;
            pre.style.margin = '0';
            pre.style.background = 'none';

            var codeForPrism = document.createElement('code');
            codeForPrism.className = 'language-' + lang;
            codeForPrism.textContent = code;
            pre.appendChild(codeForPrism);
            body.appendChild(pre);

            wrapper.appendChild(header);
            wrapper.appendChild(body);

            block.parentNode.insertBefore(wrapper, block);
            block.style.display = 'none';
        });

        if (typeof Prism !== 'undefined') {
            Prism.highlightAll();
        }
    }

    function initVideoPlayer() {
        var tag = document.createElement('script');
        tag.src = 'https://www.youtube.com/iframe_api';
        document.head.appendChild(tag);
    }

    function handleDocumentClick(e) {
        var copyBtn = e.target.closest('.code-block-copy');
        if (copyBtn) {
            var code = decodeURIComponent(copyBtn.dataset.code);
            navigator.clipboard.writeText(code).then(function() {
                copyBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> Скопировано';
                copyBtn.classList.add('copied');
                setTimeout(function() {
                    copyBtn.innerHTML = svgCopy() + ' Копировать';
                    copyBtn.classList.remove('copied');
                }, 2000);
            });
            return;
        }

        var player = e.target.closest('.vplayer');
        if (!player || player.dataset.loaded) return;
        player.dataset.loaded = '1';
        var videoId = player.dataset.video;
        var embedUrl = player.dataset.embed;
        if (embedUrl) {
            var iframe = document.createElement('iframe');
            iframe.src = embedUrl;
            iframe.setAttribute('frameborder', '0');
            iframe.setAttribute('allowfullscreen', '');
            iframe.setAttribute('allow', 'autoplay; fullscreen');
            iframe.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;border:0;';
            player.innerHTML = '';
            player.appendChild(iframe);
            return;
        }
        if (!videoId) return;
        var div = document.createElement('div');
        div.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;';
        player.innerHTML = '';
        player.appendChild(div);
        if (typeof YT !== 'undefined' && YT.Player) {
            new YT.Player(div, {
                height: '100%', width: '100%', videoId: videoId,
                playerVars: { autoplay: 1, rel: 0 },
                events: {
                    onError: function(ev) {
                        if (ev.data === 101 || ev.data === 150 || ev.data === 153) {
                            div.innerHTML =
                                '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;background:#000;padding:24px;text-align:center;gap:12px;">' +
                                '<p style="color:#999;font-size:14px;margin:0;">Видео недоступно для встраивания</p>' +
                                '<a href="https://youtu.be/' + videoId + '" target="_blank" rel="noopener" ' +
                                'style="display:inline-flex;align-items:center;gap:8px;padding:10px 24px;border-radius:8px;background:#ff4444;color:#fff;text-decoration:none;font-size:14px;font-weight:600;">' +
                                'Смотреть на YouTube</a></div>';
                        }
                    }
                }
            });
        } else {
            var fb = document.createElement('iframe');
            fb.src = 'https://www.youtube-nocookie.com/embed/' + videoId + '?autoplay=1&rel=0';
            fb.setAttribute('frameborder', '0');
            fb.setAttribute('allowfullscreen', '');
            fb.setAttribute('allow', 'autoplay; fullscreen');
            fb.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;border:0;';
            div.appendChild(fb);
        }
    }

    document.addEventListener('click', handleDocumentClick);

    function init() {
        enhanceCodeBlocks();
        initVideoPlayer();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window.ContentDisplay = { enhanceCodeBlocks: enhanceCodeBlocks };
})();
