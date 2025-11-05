
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
            reddit: `https://www.reddit.com/submit?url=${u}&title=${subject}`,
          };
        }

        function iconHTML(name){
          // Uses Font Awesome if available; otherwise simple text fallback
          const map = {
            whatsapp: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M7.25361 18.4944L7.97834 18.917C9.18909 19.623 10.5651 20 12.001 20C16.4193 20 20.001 16.4183 20.001 12C20.001 7.58172 16.4193 4 12.001 4C7.5827 4 4.00098 7.58172 4.00098 12C4.00098 13.4363 4.37821 14.8128 5.08466 16.0238L5.50704 16.7478L4.85355 19.1494L7.25361 18.4944ZM2.00516 22L3.35712 17.0315C2.49494 15.5536 2.00098 13.8345 2.00098 12C2.00098 6.47715 6.47813 2 12.001 2C17.5238 2 22.001 6.47715 22.001 12C22.001 17.5228 17.5238 22 12.001 22C10.1671 22 8.44851 21.5064 6.97086 20.6447L2.00516 22ZM8.39232 7.30833C8.5262 7.29892 8.66053 7.29748 8.79459 7.30402C8.84875 7.30758 8.90265 7.31384 8.95659 7.32007C9.11585 7.33846 9.29098 7.43545 9.34986 7.56894C9.64818 8.24536 9.93764 8.92565 10.2182 9.60963C10.2801 9.76062 10.2428 9.95633 10.125 10.1457C10.0652 10.2428 9.97128 10.379 9.86248 10.5183C9.74939 10.663 9.50599 10.9291 9.50599 10.9291C9.50599 10.9291 9.40738 11.0473 9.44455 11.1944C9.45903 11.25 9.50521 11.331 9.54708 11.3991C9.57027 11.4368 9.5918 11.4705 9.60577 11.4938C9.86169 11.9211 10.2057 12.3543 10.6259 12.7616C10.7463 12.8783 10.8631 12.9974 10.9887 13.108C11.457 13.5209 11.9868 13.8583 12.559 14.1082L12.5641 14.1105C12.6486 14.1469 12.692 14.1668 12.8157 14.2193C12.8781 14.2457 12.9419 14.2685 13.0074 14.2858C13.0311 14.292 13.0554 14.2955 13.0798 14.2972C13.2415 14.3069 13.335 14.2032 13.3749 14.1555C14.0984 13.279 14.1646 13.2218 14.1696 13.2222V13.2238C14.2647 13.1236 14.4142 13.0888 14.5476 13.097C14.6085 13.1007 14.6691 13.1124 14.7245 13.1377C15.2563 13.3803 16.1258 13.7587 16.1258 13.7587L16.7073 14.0201C16.8047 14.0671 16.8936 14.1778 16.8979 14.2854C16.9005 14.3523 16.9077 14.4603 16.8838 14.6579C16.8525 14.9166 16.7738 15.2281 16.6956 15.3913C16.6406 15.5058 16.5694 15.6074 16.4866 15.6934C16.3743 15.81 16.2909 15.8808 16.1559 15.9814C16.0737 16.0426 16.0311 16.0714 16.0311 16.0714C15.8922 16.159 15.8139 16.2028 15.6484 16.2909C15.391 16.428 15.1066 16.5068 14.8153 16.5218C14.6296 16.5313 14.4444 16.5447 14.2589 16.5347C14.2507 16.5342 13.6907 16.4482 13.6907 16.4482C12.2688 16.0742 10.9538 15.3736 9.85034 14.402C9.62473 14.2034 9.4155 13.9885 9.20194 13.7759C8.31288 12.8908 7.63982 11.9364 7.23169 11.0336C7.03043 10.5884 6.90299 10.1116 6.90098 9.62098C6.89729 9.01405 7.09599 8.4232 7.46569 7.94186C7.53857 7.84697 7.60774 7.74855 7.72709 7.63586C7.85348 7.51651 7.93392 7.45244 8.02057 7.40811C8.13607 7.34902 8.26293 7.31742 8.39232 7.30833Z"></path></svg>',
            facebook: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M14 13.5H16.5L17.5 9.5H14V7.5C14 6.47062 14 5.5 16 5.5H17.5V2.1401C17.1743 2.09685 15.943 2 14.6429 2C11.9284 2 10 3.65686 10 6.69971V9.5H7V13.5H10V22H14V13.5Z"></path></svg>',
            x: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M10.4883 14.651L15.25 21H22.25L14.3917 10.5223L20.9308 3H18.2808L13.1643 8.88578L8.75 3H1.75L9.26086 13.0145L2.31915 21H4.96917L10.4883 14.651ZM16.25 19L5.75 5H7.75L18.25 19H16.25Z"></path></svg>',
            reddit: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12.001 22C6.47813 22 2.00098 17.5228 2.00098 12C2.00098 6.47715 6.47813 2 12.001 2C17.5238 2 22.001 6.47715 22.001 12C22.001 17.5228 17.5238 22 12.001 22ZM18.671 12C18.65 11.425 18.2932 10.916 17.7598 10.7C17.2265 10.4841 16.6161 10.6016 16.201 11C15.0634 10.2267 13.7262 9.7995 12.351 9.77L13.001 6.65L15.141 7.1C15.1935 7.58851 15.5932 7.96647 16.0839 7.99172C16.5745 8.01696 17.0109 7.68201 17.1133 7.20147C17.2157 6.72094 16.9538 6.23719 16.4955 6.06019C16.0372 5.88318 15.5181 6.06536 15.271 6.49L12.821 6C12.74 5.98224 12.6554 5.99763 12.5858 6.04272C12.5163 6.08781 12.4678 6.15886 12.451 6.24L11.711 9.71C10.3189 9.73099 8.96325 10.1585 7.81098 10.94C7.38972 10.5436 6.77418 10.4333 6.2415 10.6588C5.70882 10.8842 5.35944 11.4028 5.35067 11.9812C5.3419 12.5595 5.67538 13.0885 6.20098 13.33C6.18972 13.4765 6.18972 13.6235 6.20098 13.77C6.20098 16.01 8.81098 17.83 12.031 17.83C15.251 17.83 17.861 16.01 17.861 13.77C17.8722 13.6235 17.8722 13.4765 17.861 13.33C18.3646 13.0797 18.6797 12.5623 18.671 12ZM8.67098 13C8.67098 12.4477 9.11869 12 9.67098 12C10.2233 12 10.671 12.4477 10.671 13C10.671 13.5523 10.2233 14 9.67098 14C9.40576 14 9.15141 13.8946 8.96387 13.7071C8.77633 13.5196 8.67098 13.2652 8.67098 13ZM14.481 15.75C13.7715 16.2847 12.8986 16.5568 12.011 16.52C11.1234 16.5568 10.2505 16.2847 9.54098 15.75C9.45288 15.6427 9.46057 15.486 9.55877 15.3878C9.65696 15.2896 9.81363 15.2819 9.92098 15.37C10.5222 15.811 11.2561 16.0333 12.001 16C12.7468 16.0406 13.4841 15.8254 14.091 15.39C14.1624 15.3203 14.2656 15.2941 14.3617 15.3211C14.4577 15.3482 14.5321 15.4244 14.5567 15.5211C14.5813 15.6178 14.5524 15.7203 14.481 15.79V15.75ZM14.301 14.04C13.7487 14.04 13.301 13.5923 13.301 13.04C13.301 12.4877 13.7487 12.04 14.301 12.04C14.8533 12.04 15.301 12.4877 15.301 13.04C15.312 13.3138 15.2101 13.5802 15.0192 13.7767C14.8282 13.9733 14.565 14.083 14.291 14.08L14.301 14.04Z"></path></svg>',
            //share: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M13.5759 17.2714L8.46576 14.484C7.83312 15.112 6.96187 15.5 6 15.5C4.067 15.5 2.5 13.933 2.5 12C2.5 10.067 4.067 8.5 6 8.5C6.96181 8.5 7.83301 8.88796 8.46564 9.51593L13.5759 6.72855C13.5262 6.49354 13.5 6.24983 13.5 6C13.5 4.067 15.067 2.5 17 2.5C18.933 2.5 20.5 4.067 20.5 6C20.5 7.933 18.933 9.5 17 9.5C16.0381 9.5 15.1669 9.11201 14.5343 8.48399L9.42404 11.2713C9.47382 11.5064 9.5 11.7501 9.5 12C9.5 12.2498 9.47383 12.4935 9.42408 12.7285L14.5343 15.516C15.167 14.888 16.0382 14.5 17 14.5C18.933 14.5 20.5 16.067 20.5 18C20.5 19.933 18.933 21.5 17 21.5C15.067 21.5 13.5 19.933 13.5 18C13.5 17.7502 13.5262 17.5064 13.5759 17.2714Z"></path></svg>'
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