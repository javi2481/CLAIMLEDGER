"""Browser page for manual questions. The product app stays POST /claims/query."""

from __future__ import annotations

_PAGE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Claimledger</title>
<style>
  body { font-family: Georgia, serif; max-width: 40rem; margin: 3rem auto; padding: 0 1rem; color: #1a1a1a; }
  h1 { font-size: 1.4rem; font-weight: normal; }
  p { color: #444; }
  form { display: flex; gap: 0.5rem; }
  input { flex: 1; font: inherit; padding: 0.6rem; }
  button { font: inherit; padding: 0.6rem 1rem; cursor: pointer; }
  #answer { font-size: 1.25rem; line-height: 1.4; white-space: pre-wrap; }
  .hints { padding: 0; list-style: none; }
  .hints button { background: none; border: 0; padding: 0.2rem 0; text-decoration: underline; cursor: pointer; }
</style>
</head>
<body>
<h1>Claimledger</h1>
<p>Preguntá por el resultado de BYMA en el 1T26 o el 2T26.</p>
<form id="ask">
  <input id="question" name="question" autocomplete="off" autofocus placeholder="resultado neto consolidado del 1T26">
  <button type="submit">Preguntar</button>
</form>
<ul class="hints">
  <li><button type="button" data-q="resultado neto consolidado del 1T26">resultado neto consolidado del 1T26</button></li>
  <li><button type="button" data-q="resultado atribuible a la controlante 1T26">resultado atribuible a la controlante 1T26</button></li>
  <li><button type="button" data-q="Comparar resultado neto consolidado 1T26 vs 2T26">comparar 1T26 vs 2T26</button></li>
</ul>
<p id="answer"></p>
<script>
const PERIOD = {"2026-03-31": "1T26", "2026-06-30": "2T26"};
const SCOPE = {consolidated: "consolidado", parent_attributable: "controlante"};
const METRIC = {
  net_income: "Resultado neto",
  gross_profit: "Resultado bruto",
  operating_income: "Resultado operativo",
  income_before_tax: "Resultado antes de impuesto",
  income_tax: "Impuesto a las ganancias",
  nci_income: "Resultado no controlante"
};
const REASON = {
  unresolved_identity: "No identifiqué un importe en la pregunta.",
  off_corpus: "Eso está fuera del libro.",
  recipe_no_extract: "Esa pregunta no pide un importe verificable.",
  no_matching_claim: "No hay un importe que coincida.",
  incomplete_comparison: "La comparación está incompleta.",
  ambiguous_period: "El período es ambiguo."
};
function line(claim) {
  const metric = METRIC[claim.metric] || claim.metric;
  const scope = SCOPE[claim.scope] || claim.scope;
  const period = PERIOD[claim.period] || claim.period;
  return metric + " " + scope + " " + period + ": " + claim.value + " " + claim.currency;
}
function show(data) {
  const out = document.getElementById("answer");
  if (data.status === "verified" && data.claim) {
    out.textContent = "Verificado. " + line(data.claim);
    return;
  }
  if (data.status === "verified" && data.claims) {
    out.textContent = "Verificado.\\n" + data.claims.map(line).join("\\n");
    return;
  }
  if (data.status === "abstained") {
    out.textContent = "Me abstengo. " + (REASON[data.reason] || data.reason || "");
    return;
  }
  out.textContent = "No pude leer la respuesta.";
}
async function ask(question) {
  const out = document.getElementById("answer");
  out.textContent = "Consultando…";
  const response = await fetch("/claims/query", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({question})
  });
  show(await response.json());
}
document.getElementById("ask").addEventListener("submit", (event) => {
  event.preventDefault();
  ask(document.getElementById("question").value);
});
document.querySelectorAll("[data-q]").forEach((button) => {
  button.addEventListener("click", () => {
    document.getElementById("question").value = button.dataset.q;
    ask(button.dataset.q);
  });
});
</script>
</body>
</html>
"""


def build_manual_app():
    from starlette.applications import Starlette
    from starlette.responses import HTMLResponse
    from starlette.routing import Mount, Route

    from claimledger.http.app import build_app

    async def home(_request) -> HTMLResponse:
        return HTMLResponse(_PAGE)

    return Starlette(
        routes=[
            Route("/", home, methods=["GET"]),
            Mount("/", app=build_app()),
        ]
    )
