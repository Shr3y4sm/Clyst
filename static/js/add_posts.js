 
              function hasImageSelected() {
                const url = document.getElementById("post_image").value.trim();
                const file =
                  document.getElementById("post_image_file").files[0];
                return (url && url.length > 0) || !!file;
              }

              // Debug file upload
              document
                .getElementById("post_image_file")
                .addEventListener("change", function (e) {
                  console.log("File selected:", e.target.files[0]);
                  if (e.target.files[0]) {
                    console.log("File name:", e.target.files[0].name);
                    console.log("File size:", e.target.files[0].size);
                    console.log("File type:", e.target.files[0].type);
                  }
                });

                 document
                .getElementById("product_image_file")
                .addEventListener("change", function (e) {
                  console.log("File selected:", e.target.files[0]);
                  if (e.target.files[0]) {
                    console.log("File name:", e.target.files[0].name);
                    console.log("File size:", e.target.files[0].size);
                    console.log("File type:", e.target.files[0].type);
                  }
                });


              // Enforce image presence & debug form submission
              document
                .querySelector("form")
                .addEventListener("submit", function (e) {
                  console.log("Form submitting...");
                  if (!hasImageSelected()) {
                    e.preventDefault();
                    alert(
                      "Please provide an image URL or upload an image before submitting."
                    );
                    return;
                  }
                  const fileInput = document.getElementById("post_image_file");
                  if (fileInput.files[0]) {
                    console.log(
                      "File being submitted:",
                      fileInput.files[0].name
                    );
                  } else {
                    console.log("No file selected");
                  }
                });

              // AI generation logic
              document
                .getElementById("generate_ai")
                .addEventListener("click", async function () {
                  if (!hasImageSelected()) {
                    alert(
                      "Please provide an image URL or upload an image to generate suggestions."
                    );
                    return;
                  }

                  const suggestionsDiv =
                    document.getElementById("ai_suggestions");
                  suggestionsDiv.innerHTML = "Generating suggestions...";

                  const imageUrl = document
                    .getElementById("post_image")
                    .value.trim();
                  let payload = {
                    type: "post",
                    prompt: document.getElementById("ai_prompt").value.trim(),
                    description: document
                      .getElementById("description")
                      .value.trim(),
                    image_url: imageUrl,
                  };

                  // If file selected, we can still send only URL context for now. Server stub doesn't accept multipart.
                  // Now: also send base64 if a local file is selected.
                  const file =
                    document.getElementById("post_image_file").files[0];
                  if (!imageUrl && file) {
                    const b64 = await new Promise((resolve, reject) => {
                      const reader = new FileReader();
                      reader.onload = () =>
                        resolve(reader.result.split(",")[1]);
                      reader.onerror = reject;
                      reader.readAsDataURL(file);
                    });
                    payload.image_base64 = b64;
                    payload.image_mime = file.type || "image/jpeg";
                  }

                  try {
                    const res = await fetch("/api/generate_copy", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify(payload),
                    });
                    const data = await res.json();
                    if (!data.ok) {
                      suggestionsDiv.innerHTML = `<div style="color:#c62828;">${
                        data.error || "Failed to generate suggestions"
                      }</div>`;
                      return;
                    }
                    const items = data.suggestions || [];
                    suggestionsDiv.innerHTML = items
                      .map(
                        (s, idx) => `
                    <div style="border:1px solid #e9ecef; border-radius:8px; padding:12px; margin-bottom:8px;">
                      <div style="font-weight:300; margin-bottom:6px; color: #8e8e8e">Suggestion ${
                        idx + 1
                      }</div>
                      <div style="margin-bottom:6px; font-weight:600;">${
                        s.title
                      }</div>
                      <div style="margin-bottom:10px; color: #202020">${
                        s.description
                      }</div>
                      <button type="button" class="btn btn-primary" data-idx="${idx}">Use this</button>
                    </div>
                  `
                      )
                      .join("");

                    // Attach handlers
                    Array.from(
                      suggestionsDiv.querySelectorAll("button[data-idx]")
                    ).forEach((btn) => {
                      btn.addEventListener("click", () => {
                        const i = parseInt(btn.getAttribute("data-idx"));
                        const chosen = items[i];
                        document.getElementById("post_title").value =
                          chosen.title;
                        document.getElementById("description").value =
                          chosen.description;
                      });
                    });
                  } catch (err) {
                    console.error(err);
                    suggestionsDiv.innerHTML = `<div style="color:#c62828;">Error generating suggestions.</div>`;
                  }
                });

              // --- Translation UI (lightweight) ---
              const trWrap = document.createElement("div");
              trWrap.style.marginTop = "16px";
              trWrap.innerHTML = `
                  <div class="form-group">
                    <label class="form-label">Translate title & description</label>
                    <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                      <select id="tr_lang" class="form-input" style="max-width:200px;">
                        <option value="">Select language</option>
                        <option value="en">English (en)</option>
                        <option value="hi">Hindi (hi)</option>
                        <option value="bn">Bengali (bn)</option>
                        <option value="ta">Tamil (ta)</option>
                        <option value="te">Telugu (te)</option>
                        <option value="mr">Marathi (mr)</option>
                        <option value="gu">Gujarati (gu)</option>
                        <option value="kn">Kannada (kn)</option>
                        <option value="ml">Malayalam (ml)</option>
                        <option value="pa">Punjabi (pa)</option>
                        <option value="ur">Urdu (ur)</option>
                        <option value="es">Spanish (es)</option>
                        <option value="fr">French (fr)</option>
                        <option value="de">German (de)</option>
                        <option value="zh">Chinese (zh)</option>
                        <option value="ja">Japanese (ja)</option>
                      </select>
                      <button type="button" id="do_translate" class="btn btn-secondary">Translate</button>
                    </div>
                    <div id="tr_result" class="ai-suggestions"></div>
                  </div>
                `;
              document.querySelector(".form-card").appendChild(trWrap);

              document
                .getElementById("do_translate")
                .addEventListener("click", async function () {
                  const lang = document.getElementById("tr_lang").value.trim();
                  const title = document
                    .getElementById("post_title")
                    .value.trim();
                  const desc = document
                    .getElementById("description")
                    .value.trim();
                  if (!lang) {
                    alert("Choose a language");
                    return;
                  }
                  if (!(title || desc)) {
                    alert("Fill title or description first");
                    return;
                  }
                  const resBox = document.getElementById("tr_result");
                  resBox.innerHTML = "Translating...";
                  try {
                    const res = await fetch("/api/translate_listing", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({
                        type: "post",
                        title,
                        description: desc,
                        target_lang: lang,
                      }),
                    });
                    const data = await res.json();
                    if (!data.ok) {
                      resBox.innerHTML = `<div style="color:#c62828;">${
                        data.error || "Failed to translate"
                      }</div>`;
                      return;
                    }
                    const phrases = (data.seo_phrases || [])
                      .map(
                        (p) =>
                          `<span style="display:inline-block; margin:4px; padding:4px 8px; border:1px solid #e1e1e1; border-radius:12px; font-size:12px; color:#444;">${p}</span>`
                      )
                      .join("");
                    resBox.innerHTML = `
                      <div style="border:1px solid #e9ecef; border-radius:8px; padding:12px; margin-top:8px;">
                        <div style="font-weight:600; margin-bottom:6px;">Translated</div>
                        <div style="margin-bottom:6px;">Title: ${
                          data.title || ""
                        }</div>
                        <div style="margin-bottom:10px;">Description: ${
                          data.description || ""
                        }</div>
                        <div style="margin-bottom:6px; font-weight:600;">SEO phrases</div>
                        <div>${
                          phrases || '<i style="color:#888;">None</i>'
                        }</div>
                        <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;">
                          <button type="button" class="btn btn-primary" id="tr_apply">Apply</button>
                        </div>
                      </div>`;
                    const applyBtn = document.getElementById("tr_apply");
                    applyBtn?.addEventListener("click", () => {
                      document.getElementById("post_title").value =
                        data.title || title;
                      document.getElementById("description").value =
                        data.description || desc;
                    });
                  } catch (err) {
                    console.error(err);
                    resBox.innerHTML = `<div style="color:#c62828;">Error translating.</div>`;
                  }
                });
    