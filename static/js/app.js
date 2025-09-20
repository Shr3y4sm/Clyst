
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