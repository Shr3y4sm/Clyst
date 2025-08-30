  // Import Firebase SDKs from CDN (v12 modular)
  import { initializeApp } from "https://www.gstatic.com/firebasejs/12.1.0/firebase-app.js";
  import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, RecaptchaVerifier, signInWithPhoneNumber, updateProfile } from "https://www.gstatic.com/firebasejs/12.1.0/firebase-auth.js";

  // Firebase configuration
  const firebaseConfig = {
    apiKey: "Your API key",
    authDomain: "loginexample-21a86.firebaseapp.com",
    projectId: "loginexample-21a86",
    storageBucket: "loginexample-21a86.firebasestorage.app",
    messagingSenderId: "599115471797",
    appId: "1:599115471797:web:7503d4b1c119e47402d7fc"
  };

  // Initialize Firebase and Auth
  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);

  const roleStep = document.getElementById("role-step");
  const chooseUserBtn = document.getElementById("choose-user");
  const chooseArtistBtn = document.getElementById("choose-artist");

  // User email/password form
  const form = document.getElementById("auth-form");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const errorText = document.getElementById("error-text");
  // User signup form
  const signupForm = document.getElementById("signup-form");
  const showSignupBtn = document.getElementById("show-signup");
  const showLoginBtn = document.getElementById("show-login");
  const fullNameInput = document.getElementById("full-name");
  const phoneUserInput = document.getElementById("phone-user");
  const genderSelect = document.getElementById("gender");
  const emailSignupInput = document.getElementById("email-signup");
  const password1Input = document.getElementById("password1");
  const password2Input = document.getElementById("password2");
  const errorTextSignup = document.getElementById("error-text-signup");

  // Artisan phone form
  const artistForm = document.getElementById("artist-form");
  const phoneInput = document.getElementById("phone");
  const sendOtpBtn = document.getElementById("send-otp");
  const otpSection = document.getElementById("otp-section");
  const otpInput = document.getElementById("otp");
  const verifyOtpBtn = document.getElementById("verify-otp");
  const errorTextArtist = document.getElementById("error-text-artist");
  // Artisan signup form
  const artistSignupForm = document.getElementById('artist-signup-form');
  const showArtistSignupBtn = document.getElementById('show-artist-signup');
  const showArtistLoginBtn = document.getElementById('show-artist-login');
  const fullNameArtistInput = document.getElementById('full-name-artist');
  const genderArtistSelect = document.getElementById('gender-artist');
  const phoneArtistSignupInput = document.getElementById('phone-artist-signup');
  const artistSendOtpBtn = document.getElementById('artist-send-otp');
  const artistOtpSection = document.getElementById('artist-otp-section');
  const artistOtpInput = document.getElementById('artist-otp');
  const artistVerifyOtpBtn = document.getElementById('artist-verify-otp');
  const errorTextArtistSignup = document.getElementById('error-text-artist-signup');

  function showError(message) {
    errorText.textContent = message || "";
    errorText.hidden = !message;
  }

  // Step 1 handlers
  chooseUserBtn?.addEventListener('click', () => {
    roleStep.style.display = 'none';
    form.style.display = 'grid';
  });

  chooseArtistBtn?.addEventListener('click', () => {
    roleStep.style.display = 'none';
    artistForm.style.display = 'grid';
    ensureRecaptcha();
  });

  // User email/password flow
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    showError("");

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (!/\S+@\S+\.\S+/.test(email)) {
      showError("Please enter a valid email address.");
      emailInput.focus();
      return;
    }
    if (password.length < 6) {
      showError("Password must be at least 6 characters.");
      passwordInput.focus();
      return;
    }

    try {
      // Try sign in first; if user doesn't exist, create account
      await signInWithEmailAndPassword(auth, email, password)
        .catch(async (err) => {
          if (err?.code === 'auth/user-not-found') {
            await createUserWithEmailAndPassword(auth, email, password);
          } else {
            throw err;
          }
        });

      // Redirect to User feed
      window.location.href = '../Clyst-FrontEnd/UsermainPages/feed.html';
    } catch (err) {
      showError(err?.message || "Authentication failed.");
    }
  });

  // Artisan phone flow
  let recaptchaVerifier;
  let confirmationResult;
  const testingBypass = true; // TEMP: bypass phone auth for testing

  function showArtistError(message){
    errorTextArtist.textContent = message || "";
    errorTextArtist.hidden = !message;
  }

  function ensureRecaptcha(){
    if (recaptchaVerifier) return;
    recaptchaVerifier = new RecaptchaVerifier(auth, 'recaptcha-container', {
      size: 'normal'
    });
  }

  sendOtpBtn?.addEventListener('click', async () => {
    showArtistError("");
    const raw = phoneInput.value.trim();
    const phone = normalizePhone(raw);
    if (!phone && !testingBypass) {
      showArtistError('Enter a valid phone. Use +<country><number> or a 10-digit Indian mobile.');
      return;
    }
    try{
      if (!testingBypass) {
        ensureRecaptcha();
        confirmationResult = await signInWithPhoneNumber(auth, phone, recaptchaVerifier);
      }
      otpSection.style.display = 'block';
    } catch(err){
      showArtistError(err?.message || 'Failed to send OTP.');
    }
  });

  // Toggle between login and signup (user)
  showSignupBtn?.addEventListener('click', () => {
    clearSignupErrors();
    form.style.display = 'none';
    signupForm.style.display = 'grid';
  });
  showLoginBtn?.addEventListener('click', () => {
    clearSignupErrors();
    signupForm.style.display = 'none';
    form.style.display = 'grid';
  });

  function clearSignupErrors(){
    errorTextSignup.textContent = '';
    errorTextSignup.hidden = true;
  }

  // Handle user signup
  signupForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearSignupErrors();
    const fullName = (fullNameInput.value || '').trim();
    const phone = (phoneUserInput.value || '').trim();
    const gender = genderSelect.value || '';
    const email = (emailSignupInput.value || '').trim();
    const pass1 = password1Input.value;
    const pass2 = password2Input.value;

    if (!fullName) { return showSignupError('Please enter your full name.'); }
    if (!/\S+@\S+\.\S+/.test(email)) { return showSignupError('Please enter a valid email.'); }
    if (pass1.length < 6) { return showSignupError('Password must be at least 6 characters.'); }
    if (pass1 !== pass2) { return showSignupError('Passwords do not match.'); }

    try{
      const cred = await createUserWithEmailAndPassword(auth, email, pass1);
      if (fullName) {
        await updateProfile(cred.user, { displayName: fullName });
      }
      // Sign out and return to login form
      await auth.signOut?.();
      alert('Account created. Please log in.');
      signupForm.style.display = 'none';
      form.style.display = 'grid';
      emailInput.value = email;
    } catch(err){
      showSignupError(err?.message || 'Sign up failed.');
    }
  });

  function showSignupError(msg){
    errorTextSignup.textContent = msg || '';
    errorTextSignup.hidden = !msg;
  }

  verifyOtpBtn?.addEventListener('click', async () => {
    showArtistError("");
    const code = otpInput.value.trim();
    if (!code && !testingBypass) {
      showArtistError('Please enter the OTP.');
      return;
    }
    try{
      if (!testingBypass) {
        await confirmationResult.confirm(code);
      }
      // Redirect to Artist feed
      window.location.href = '../Clyst-FrontEnd/ArtistmainPages/feed.html';
    } catch(err){
      showArtistError(err?.message || 'Invalid OTP.');
    }
  });

  function normalizePhone(input){
    if (!input) return '';
    const trimmed = input.replace(/\s+/g, '').replace(/[-()]/g, '');
    const e164 = /^\+[1-9]\d{7,14}$/;
    if (e164.test(trimmed)) return trimmed;
    // Assume India if 10 digits without country code
    const digits = trimmed.replace(/\D/g, '');
    if (digits.length === 10) return `+91${digits}`;
    // Handle leading 0 then 10 digits
    if (digits.length === 11 && digits.startsWith('0')) return `+91${digits.slice(1)}`;
    return '';
  }

  // Toggle artist login/signup
  showArtistSignupBtn?.addEventListener('click', () => {
    artistForm.style.display = 'none';
    artistSignupForm.style.display = 'grid';
  });
  showArtistLoginBtn?.addEventListener('click', () => {
    artistSignupForm.style.display = 'none';
    artistForm.style.display = 'grid';
  });

  function showArtistSignupError(msg){
    errorTextArtistSignup.textContent = msg || '';
    errorTextArtistSignup.hidden = !msg;
  }

  // Artisan signup OTP flow (with testing bypass)
  artistSendOtpBtn?.addEventListener('click', async () => {
    showArtistSignupError('');
    const raw = (phoneArtistSignupInput.value || '').trim();
    const phone = normalizePhone(raw);
    if (!phone && !testingBypass) {
      showArtistSignupError('Enter a valid phone.');
      return;
    }
    try{
      if (!testingBypass) {
        ensureRecaptcha();
        confirmationResult = await signInWithPhoneNumber(auth, phone, recaptchaVerifier);
      }
      artistOtpSection.style.display = 'block';
    } catch(err){
      showArtistSignupError(err?.message || 'Failed to send OTP.');
    }
  });

  artistVerifyOtpBtn?.addEventListener('click', async () => {
    showArtistSignupError('');
    const code = (artistOtpInput.value || '').trim();
    if (!code && !testingBypass) {
      showArtistSignupError('Please enter the OTP.');
      return;
    }
    try{
      if (!testingBypass) {
        await confirmationResult.confirm(code);
      }
      // Set display name if provided
      const currentUser = auth.currentUser;
      const fullName = (fullNameArtistInput.value || '').trim();
      if (currentUser && fullName) {
        await updateProfile(currentUser, { displayName: fullName });
      }
      // Sign out and return to artist login
      await auth.signOut?.();
      alert('Account created. Please log in.');
      artistSignupForm.style.display = 'none';
      artistForm.style.display = 'grid';
      phoneInput.value = phoneArtistSignupInput.value;
    } catch(err){
      showArtistSignupError(err?.message || 'Invalid OTP.');
    }
  });