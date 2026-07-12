/* ════════════════════════════════════════════════════════════════
   captura.js — Formulario de registro de Mal Mercado (un solo origen).
   Se inyecta en cada <div data-mm-captura> de cualquier página.
   Envía a un Google Form (POST no-cors a formResponse): los registros
   caen a la hoja de cálculo del dueño. AQUÍ NO HAY NINGÚN SECRETO:
   el ID del formulario es público por diseño (es un form público).
   ════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var FORM = "https://docs.google.com/forms/d/e/1FAIpQLSfktiqMqs-3pUNtNnVHeBXMKAcE1HUD4AxMvEwyUnsLXeY0XQ/formResponse";
  var E = { nombre: "entry.339523399", email: "entry.647095335", tel: "entry.172294119",
            pais: "entry.34816064", edad: "entry.1668220949",
            interes: "entry.429510721", fuente: "entry.1428730459" };
  var EDADES = ["18–24", "25–34", "35–44", "45–54", "55+"];
  var INTERESES = ["Acciones", "Cripto", "Tecnología e IA", "Macroeconomía",
                   "Inversión a largo plazo", "Trading"];
  var FUENTES = ["TikTok", "Instagram", "YouTube", "X", "Facebook", "Threads", "Google", "Amigo"];
  // La lista DEBE coincidir letra por letra con las opciones del Google Form.
  var PAISES = ["México", "Estados Unidos", "Colombia", "Chile", "Perú", "España",
    "Afganistán","Albania","Alemania","Andorra","Angola","Antigua y Barbuda","Arabia Saudita","Argelia","Armenia","Australia","Austria","Azerbaiyán","Bahamas","Bangladés","Barbados","Baréin","Bélgica","Belice","Benín","Bielorrusia","Birmania (Myanmar)","Bolivia","Bosnia y Herzegovina","Botsuana","Brasil","Brunéi","Bulgaria","Burkina Faso","Burundi","Bután","Cabo Verde","Camboya","Camerún","Canadá","Catar","Chad","China","Chipre","Ciudad del Vaticano","Comoras","Corea del Norte","Corea del Sur","Costa de Marfil","Costa Rica","Croacia","Cuba","Dinamarca","Dominica","Ecuador","Egipto","El Salvador","Emiratos Árabes Unidos","Eritrea","Eslovaquia","Eslovenia","Estonia","Etiopía","Filipinas","Finlandia","Fiyi","Gabón","Gambia","Georgia","Ghana","Granada","Grecia","Guatemala","Guinea","Guinea Ecuatorial","Guinea-Bisáu","Guyana","Haití","Honduras","Hungría","India","Indonesia","Irak","Irán","Irlanda","Islandia","Islas Marshall","Islas Salomón","Israel","Italia","Jamaica","Japón","Jordania","Kazajistán","Kenia","Kirguistán","Kiribati","Kuwait","Laos","Lesoto","Letonia","Líbano","Liberia","Libia","Liechtenstein","Lituania","Luxemburgo","Macedonia del Norte","Madagascar","Malasia","Malaui","Maldivas","Malí","Malta","Marruecos","Mauricio","Mauritania","Micronesia","Moldavia","Mónaco","Mongolia","Montenegro","Mozambique","Namibia","Nauru","Nepal","Nicaragua","Níger","Nigeria","Noruega","Nueva Zelanda","Omán","Países Bajos","Pakistán","Palaos","Palestina","Panamá","Papúa Nueva Guinea","Paraguay","Polonia","Portugal","Reino Unido","República Centroafricana","República Checa","República del Congo","República Democrática del Congo","República Dominicana","Ruanda","Rumania","Rusia","Samoa","San Cristóbal y Nieves","San Marino","San Vicente y las Granadinas","Santa Lucía","Santo Tomé y Príncipe","Senegal","Serbia","Seychelles","Sierra Leona","Singapur","Siria","Somalia","Sri Lanka","Suazilandia (Eswatini)","Sudáfrica","Sudán","Sudán del Sur","Suecia","Suiza","Surinam","Tailandia","Taiwán","Tanzania","Tayikistán","Timor Oriental","Togo","Tonga","Trinidad y Tobago","Túnez","Turkmenistán","Turquía","Tuvalu","Ucrania","Uganda","Uruguay","Uzbekistán","Vanuatu","Venezuela","Vietnam","Yemen","Yibuti","Zambia","Zimbabue"];

  var CSS = "" +
    ".mmc{background:rgba(255,255,255,.04);border:1px solid rgba(62,240,140,.3);border-radius:16px;" +
    "padding:1.6rem;max-width:560px;margin:0 auto;position:relative;z-index:1}" +
    ".mmc h3{font-family:'Space Grotesk',sans-serif;font-size:1.35rem;margin:0 0 .3rem;color:#eef2f6}" +
    ".mmc h3 .g{color:#3ef08c}" +
    ".mmc p.s{color:#8b95a3;font-size:.88rem;margin:0 0 1.1rem;line-height:1.55}" +
    ".mmc .fila{display:grid;grid-template-columns:1fr 1fr;gap:.7rem}" +
    ".mmc label{display:block;font-family:'JetBrains Mono',monospace;font-size:.62rem;" +
    "letter-spacing:.13em;text-transform:uppercase;color:#8b95a3;margin:.8rem 0 .3rem}" +
    ".mmc input,.mmc select{width:100%;box-sizing:border-box;background:#0d1117;color:#eef2f6;" +
    "border:1px solid rgba(255,255,255,.15);border-radius:9px;padding:.65rem .8rem;" +
    "font-family:Inter,sans-serif;font-size:.92rem}" +
    ".mmc input:focus,.mmc select:focus{outline:none;border-color:#3ef08c}" +
    ".mmc button{width:100%;margin-top:1.2rem;background:#3ef08c;color:#07090d;border:none;" +
    "border-radius:10px;padding:.85rem;font-weight:700;font-size:1rem;cursor:pointer;font-family:Inter,sans-serif}" +
    ".mmc button:disabled{opacity:.6;cursor:wait}" +
    ".mmc .ok{text-align:center;padding:2rem 1rem}" +
    ".mmc .ok b{color:#3ef08c;font-size:1.15rem;display:block;margin-bottom:.4rem}" +
    ".mmc .leg{font-size:.7rem;color:#67707c;margin-top:.8rem;line-height:1.5}";

  function opts(arr, ph) {
    var h = '<option value="" disabled selected>' + ph + "</option>";
    for (var i = 0; i < arr.length; i++) h += "<option>" + arr[i] + "</option>";
    return h;
  }

  function render(div) {
    div.innerHTML =
      '<form class="mmc" novalidate>' +
      "<h3>Recibe <span class='g'>El Lunes de Mal Mercado</span></h3>" +
      '<p class="s">Cada lunes antes de que abra el mercado: lo que reportaron las noticias de la semana, gratis y en 5 minutos. Sin spam, date de baja cuando quieras.</p>' +
      '<label>Nombre</label><input name="nombre" required autocomplete="name">' +
      '<div class="fila"><div><label>Email</label><input name="email" type="email" required autocomplete="email"></div>' +
      '<div><label>Teléfono (WhatsApp)</label><input name="tel" type="tel" required autocomplete="tel"></div></div>' +
      '<div class="fila"><div><label>País</label><select name="pais" required>' + opts(PAISES, "Elige tu país") + "</select></div>" +
      '<div><label>Edad</label><select name="edad" required>' + opts(EDADES, "Rango de edad") + "</select></div></div>" +
      '<div class="fila"><div><label>Qué te interesa más</label><select name="interes" required>' + opts(INTERESES, "Elige un tema") + "</select></div>" +
      '<div><label>Cómo nos conociste</label><select name="fuente" required>' + opts(FUENTES, "Elige una opción") + "</select></div></div>" +
      "<button type='submit'>Quiero el correo del lunes</button>" +
      '<p class="leg">Al registrarte aceptas recibir el correo semanal gratuito de Mal Mercado. Usamos tus datos solo para enviarte contenido y entender a nuestra audiencia; no los vendemos ni compartimos.</p>' +
      "</form>";

    var form = div.querySelector("form");
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      if (!form.reportValidity()) return;
      var btn = form.querySelector("button");
      btn.disabled = true; btn.textContent = "Enviando…";
      var fd = new FormData();
      fd.append(E.nombre, form.nombre.value.trim());
      fd.append(E.email, form.email.value.trim());
      fd.append(E.tel, form.tel.value.trim());
      fd.append(E.pais, form.pais.value);
      fd.append(E.edad, form.edad.value);
      fd.append(E.interes, form.interes.value);
      fd.append(E.fuente, form.fuente.value);
      fetch(FORM, { method: "POST", mode: "no-cors", body: fd }).finally(function () {
        div.querySelector(".mmc").innerHTML =
          '<div class="ok"><b>Listo. Ya estás dentro.</b>' +
          "El primer correo llega el próximo lunes antes de que abra el mercado. " +
          'Mientras tanto: <a href="track.html" style="color:#3ef08c">mira nuestro historial público</a>.</div>';
        if (window.gtag) gtag("event", "lead_captura", { fuente_pagina: location.pathname });
      });
    });
  }

  var style = document.createElement("style");
  style.textContent = CSS;
  document.head.appendChild(style);
  var zonas = document.querySelectorAll("[data-mm-captura]");
  for (var i = 0; i < zonas.length; i++) render(zonas[i]);
})();
