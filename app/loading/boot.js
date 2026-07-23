// Externalisé (audit M1) : la CSP script-src 'self' bloque l'inline — ce fichier même-origine passe.
window.__irmFail = function (msg) {
  document.getElementById("status").textContent = "Le démarrage a échoué.";
  var e = document.getElementById("err");
  e.style.display = "block";
  e.textContent = msg + "\n\nConsulte les logs : %APPDATA%/com.nylenia.irminsul/logs/next-server.log";
  var s = document.querySelector(".spin");
  if (s) s.style.display = "none";
};
