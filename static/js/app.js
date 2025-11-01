
          function toggleMenu(e) {
        e?.stopPropagation?.();
        const menu = document.getElementById("mobileMenu");
        const now = menu.style.display === "flex" ? "none" : "flex";
        menu.style.display = now;
            if (now === "flex")
              document.getElementById("searchBelow").classList.remove("open");
      }

          function toggleSearch() {
        const bar = document.getElementById("searchBelow");
        bar.classList.toggle("open");
        const menu = document.getElementById("mobileMenu");
            if (menu.style.display === "flex") menu.style.display = "none";
            if (bar.classList.contains("open")) {
              requestAnimationFrame(() =>
                document.getElementById("globalSearchInput").focus()
              );
        }
      }
function googleTranslateElementInit() {
        new google.translate.TranslateElement(
          {
            pageLanguage: "en", // Set your website's default language
            includedLanguages:
              "en,hi,bi,ta,te,mr,gu,kn,ml,pa,ur,es,fr,de,zh,ja,ko", // Optional: Specify languages to include in the dropdown
            layout: google.translate.TranslateElement.InlineLayout.SIMPLE, // Optional: Customize widget layout
          },
          "google_translate_element"
        );
      }

      // --- Share Modal ---
      // Lightweight, reusable share dialog with common social targets
      // Usage: openShareModal(url, title, text)
      (function(){
        function ensureShareStyles(){
          if (document.getElementById('share-modal-styles')) return;
          const style = document.createElement('style');
          style.id = 'share-modal-styles';
          style.textContent = `
            .share-overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:1100;opacity:0;transition:opacity .2s ease}
            .share-overlay.open{opacity:1}
            .share-modal{background:var(--card);color:var(--text);border-radius:8px;max-width:560px;width:92vw;box-shadow:0 10px 30px rgba(0,0,0,.25);overflow:hidden}
            .share-header{display:flex;align-items:center;justify-content:space-between;padding:14px 16px;border-bottom:1px solid var(--border)}
            .share-title{font-weight:700;font-size:16px}
            .share-close{background:none;border:none;cursor:pointer;color:var(--text);padding:4px}
            .share-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;padding:16px}
            .share-item{display:flex;flex-direction:column;align-items:center;text-decoration:none;color:inherit}
            .share-icon{width:46px;height:46px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff}
            .share-item span{margin-top:8px;font-size:12px;color:var(--muted)}
            .share-copy{padding:12px 16px;border-top:1px solid var(--border);display:flex;gap:8px;align-items:center}
            .share-copy input{flex:1;border:1px solid var(--border);background:var(--bg);color:var(--text);padding:8px;border-radius:6px}
            .share-copy .btn{height:36px}
            @media (max-width: 560px){.share-grid{grid-template-columns:repeat(3,1fr)}}
          `;
          document.head.appendChild(style);
        }

        function buildLinks(url, title, text){
          const u = encodeURIComponent(url);
          const t = encodeURIComponent(text || title || '');
          const subject = encodeURIComponent(title || 'Check this out');
          return {
            whatsapp: `https://api.whatsapp.com/send?text=${t}%20${u}`,
            facebook: `https://www.facebook.com/sharer/sharer.php?u=${u}`,
            x: `https://twitter.com/intent/tweet?url=${u}&text=${t}`,
            email: `mailto:?subject=${subject}&body=${t}%20${u}`,
            kakao: url, // Fallback: open the link; KakaoTalk needs SDK for deep share
            reddit: `https://www.reddit.com/submit?url=${u}&title=${subject}`,
          };
        }

        function iconHTML(name){
          // Uses Font Awesome if available; otherwise simple text fallback
          const map = {
            whatsapp: '<i class="fa-brands fa-whatsapp"></i>',
            facebook: '<i class="fa-brands fa-facebook-f"></i>',
            x: '<i class="fa-brands fa-x-twitter"></i>',
            email: '<i class="fa-solid fa-envelope"></i>',
            kakao: 'K',
            reddit: '<i class="fa-brands fa-reddit-alien"></i>',
            share: '<i class="fa-solid fa-share-nodes"></i>'
          };
          return map[name] || name[0].toUpperCase();
        }

        window.openShareModal = function(url, title, text){
          try{
            ensureShareStyles();
            // Web Share API shortcut (mobile)
            if (navigator.share){
              navigator.share({title: title||document.title, text: text||'', url}).catch(()=>{});
            }
            const links = buildLinks(url, title, text);
            const overlay = document.createElement('div');
            overlay.className = 'share-overlay';
            overlay.innerHTML = `
              <div class="share-modal" role="dialog" aria-modal="true">
                <div class="share-header">
                  <div class="share-title">Share</div>
                  <button class="share-close" aria-label="Close" onclick="this.closest('.share-overlay').remove()">✕</button>
                </div>
                <div class="share-grid">
                  <a class="share-item" target="_blank" rel="noopener" href="${links.whatsapp}">
                    <div class="share-icon" style="background:#25D366">${iconHTML('whatsapp')}</div>
                    <span>WhatsApp</span>
                  </a>
                  <a class="share-item" target="_blank" rel="noopener" href="${links.facebook}">
                    <div class="share-icon" style="background:#1877F2">${iconHTML('facebook')}</div>
                    <span>Facebook</span>
                  </a>
                  <a class="share-item" target="_blank" rel="noopener" href="${links.x}">
                    <div class="share-icon" style="background:#000">${iconHTML('x')}</div>
                    <span>X</span>
                  </a>
                  <a class="share-item" target="_blank" rel="noopener" href="${links.email}">
                    <div class="share-icon" style="background:#6B7280">${iconHTML('email')}</div>
                    <span>Email</span>
                  </a>
                  <a class="share-item" target="_blank" rel="noopener" href="${links.kakao}">
                    <div class="share-icon" style="background:#FEE500;color:#000">${iconHTML('kakao')}</div>
                    <span>KakaoTalk</span>
                  </a>
                  <a class="share-item" target="_blank" rel="noopener" href="${links.reddit}">
                    <div class="share-icon" style="background:#FF4500">${iconHTML('reddit')}</div>
                    <span>Reddit</span>
                  </a>
                </div>
                <div class="share-copy">
                  <input type="text" value="${url}" readonly aria-label="Share link" />
                  <button class="btn btn-secondary" type="button">Copy</button>
                </div>
              </div>`;
            overlay.addEventListener('click', (e)=>{ if(e.target===overlay) overlay.remove(); });
            document.body.appendChild(overlay);
            requestAnimationFrame(()=> overlay.classList.add('open'));

            // Copy button
            const copyBtn = overlay.querySelector('.share-copy .btn');
            const input = overlay.querySelector('.share-copy input');
            copyBtn.addEventListener('click', async ()=>{
              try{ await navigator.clipboard.writeText(input.value); copyBtn.textContent='Copied'; setTimeout(()=>copyBtn.textContent='Copy',1200);}catch(err){ alert('Failed to copy'); }
            });
          }catch(err){
            // Fallback to basic copy
            try{ navigator.clipboard.writeText(url); alert('Link copied to clipboard'); }catch(e){ console.log(err); }
          }
        }
        window.openShareFromEl = function(el){
          if (!el) return;
          let url = el.getAttribute('data-share-url') || el.getAttribute('data-url') || '';
          const title = el.getAttribute('data-share-title') || el.getAttribute('data-title') || document.title;
          const text = el.getAttribute('data-share-text') || '';
          if (url && url.startsWith('/')) url = window.location.origin + url;
          if (!url) url = window.location.href;
          return window.openShareModal(url, title, text);
        }
      })();

      
          function sayAloud(text) {
            const message = new SpeechSynthesisUtterance();
            message.text = `The title of the artwork is ${text.title}. It is created by ${text.artist}. The price of the artwork is Rs.${text.price}. The description says it is ${text.description}.`;
            window.speechSynthesis.speak(message); // Start speaking
          }

          async function copyToClipboard(textToCopy) {
            try {
              await navigator.clipboard.writeText(textToCopy);
              alert("Text copied to clipboard");
            } catch (err) {
              alert("Failed to copy text: " + err);
            }
          }

          
      // Highlight active nav link
      document.addEventListener("DOMContentLoaded", function () {
        const path = window.location.pathname.split("/").pop();
        document
          .querySelectorAll(".nav-center a, .mobile-menu a")
          .forEach((link) => {
            if (link.getAttribute("href") === path) {
              link.classList.add("active");
            } else {
              link.classList.remove("active");
            }
          });
      });

      // Submit search to products page
      document.addEventListener("DOMContentLoaded", function () {
        const global = document.getElementById("globalSearchInput");
        if (global) {
          global.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
              const q = global.value.trim();
              const url = new URL(window.location.origin + "/products");
              if (q) url.searchParams.set("q", q);
              window.location.href = url.toString();
            }
          });
        }
        const quick = document.getElementById("quickSearchInput");
        if (quick) {
          quick.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
              const q = quick.value.trim();
              const url = new URL(window.location.origin + "/products");
              if (q) url.searchParams.set("q", q);
              window.location.href = url.toString();
            }
          });
        }
      });

      
      function getPrompt(){
        alert("Voice mode still in development. Please use text input for now.");
      }