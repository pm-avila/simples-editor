import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { SUPABASE_URL, SUPABASE_ANON_KEY } from "./config.js";


const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const loginForm = document.getElementById("login-form");
const loginScreen = document.getElementById("login-screen");
const ideShell = document.getElementById("ide-shell");
const message = document.getElementById("login-message");


function showIdeShell() {
  loginScreen.hidden = true;
  ideShell.hidden = false;
}


function showLoginScreen() {
  loginScreen.hidden = false;
  ideShell.hidden = true;
}


async function restoreSession() {
  const { data } = await supabase.auth.getSession();
  if (data.session) {
    showIdeShell();
    return;
  }
  showLoginScreen();
}


loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(loginForm);
  const { error } = await supabase.auth.signInWithPassword({
    email: formData.get("email"),
    password: formData.get("password"),
  });

  if (error) {
    message.textContent = error.message;
    showLoginScreen();
    return;
  }

  message.textContent = "";
  showIdeShell();
});


restoreSession();
