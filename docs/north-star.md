# CLAIMLEDGER — North star

Versión corta. El documento completo es [documento-rector.md](documento-rector.md).

Leer esto **antes** de implementar cualquier componente. Si una decisión no suma a este texto, distrae del producto.

## Qué es

CLAIMLEDGER es un **libro de afirmaciones financieras verificadas**.

No es solo “claims”. Es una colección estructurada y trazable: cada cifra tiene identidad, valor, evidencia y un estado (verificada o no). El nombre encaja con eso: *claim* + *ledger*.

Regla del producto:

> **Si no hay una afirmación verificada, no hay respuesta.**

## El problema

En el estado de resultados de BYMA, en la **misma página**, hay dos cifras casi iguales:

- Resultado neto del período: **21.262.335**
- Resultado atribuible a la controlante: **21.259.769**

Un buscador puede recuperar la página correcta y **equivocarse de fila**. Se parecen, están juntas, y recuperar texto no es lo mismo que entender contabilidad.

Ese caso BYMA es el **test canónico**. Demuestra la tesis:

> El retrieval encuentra evidencia. CLAIMLEDGER convierte esa evidencia en una afirmación financiera verificable.

Recuperar la página correcta **no** equivale a identificar el dato correcto.

## Qué es una afirmación

No es un párrafo del PDF. Es esto:

> BYMA, al 31 de marzo de 2026, consolidado, resultado neto = 21.262.335.  
> Lo vi en tal documento, página 4, en la fila que dice RESULTADO NETO DEL PERÍODO.

Tres cosas distintas, que no se mezclan:

| Qué | Responde | Ejemplo |
|-----|----------|---------|
| Identidad | ¿Qué claim es? | `BYMA\|2026-03-31\|income_statement\|consolidated\|net_income` |
| Valor | ¿Cuánto? | 21262335 ARS (el número no identifica) |
| Evidencia | ¿De dónde salió? | documento, página, texto, recuadro |

`FinancialIdentity` es entidad. `MonetaryAmount` (valor + moneda + unidad) es componente: se deduplica por contenido, no forma parte del ID.

Dos evidencias distintas pueden ser el **mismo** claim. La evidencia demuestra origen. La identidad dice qué es. La provenance puede cambiar o acumularse sin crear otra entidad.

## Cómo se apilan las capas

No son alternativas. Cada una responde una sola pregunta.

```
                    PDF / XBRL
                        │
                        ▼
                    Docling
                        │
                DoclingDocument
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
    Docling Graph                LlamaIndex
    entity identity              retrieval
    merge / ledger               candidates
          │                           │
          └─────────────┬─────────────┘
                        ▼
                 CLAIMLEDGER
                 deterministic
                 financial kernel
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
           VERIFIED            ABSTAIN
                        │
                        ▼
                   Open WebUI
```

| Capa | Pregunta que responde |
|------|------------------------|
| Docling | ¿Qué hay en el documento? |
| Docling Graph | ¿Qué entidades y relaciones hay? |
| LlamaIndex | ¿Dónde están los candidatos relevantes? |
| CLAIMLEDGER | ¿Qué afirmación financiera representa esto y puedo demostrar que es correcta? |
| Open WebUI | ¿Cómo se lo muestro al usuario? |

Runtime: `DoclingDocument`. Persistencia o intercambio, si hace falta: JSON de Docling o DocLang. DocLang **no** es una etapa de cada request.

Retrieval **nunca** pasa por Markdown:

```
DoclingReader(export_type="json") → DoclingNodeParser → LlamaIndex
```

No: PDF → Docling → Markdown → LlamaIndex. Eso aplana la tabla y vuelve a matar consolidado vs controlante.

## Precisión sobre Docling Graph

Docling Graph es la **capa de identidad de entidades y relaciones**.

Puede persistir o exportar un grafo. Eso no es su función arquitectónica. **No es el extractor del P&L.** En CLAIMLEDGER su trabajo es acotado:

```
issuer + period + statement + scope + metric
        ↓
identity / nodo
        ↓
ID estable
```

Nos da contexto e identidad de entidades. **No** interpreta el claim contable.

CLAIMLEDGER resuelve: ¿esta evidencia es el resultado neto **consolidado** de BYMA en 1T26, y puedo demostrarlo?

## Las cuatro capas propias

Solo estas son el producto:

1. Identidad financiera
2. Afirmación financiera (claim)
3. Verificación
4. Abstención

Alrededor, infraestructura:

| Pieza | Rol |
|-------|-----|
| Docling | inteligencia de documento |
| Docling Graph | identidad de entidades, grafo, merge |
| LlamaIndex | búsqueda de candidatos |
| Open WebUI | presentación |
| DocLang | intercambio, no runtime |

## Regla inviolable: el kernel no se toca

CLAIMLEDGER **no tiene una etapa LLM para crear** `identity_v1` / `identity_v2`.

```
              LLM
               │
         retrieval / NLP
               │
               ▼
         CANDIDATES
               │
               ▼
    ┌────────────────────┐
    │   CLAIMLEDGER      │
    │                    │
    │ deterministic      │
    │ identity           │
    │ verification       │
    │ abstention         │
    └────────────────────┘
```

El LLM no crea la verdad. Puede ayudar **antes** (pregunta → candidatos). No puede: pregunta → el modelo inventa la identidad.

Si el parse no iguala el gold: no se cambia el expected, no se inventa la identidad con un modelo, no se trae MinerU. Se investiga conversión, schema, template, serialización o mapeo al grafo.

Un VLM puede **releer** una página difícil. Sigue diferido hasta que haya GPU. No puede decidir qué cifra es. La fase 11 exporta Cypher y lee los períodos de ese script; una base Neo4j, si algún día corre, consulta el libro y no verifica. El recorte de la página ya acompaña la ficha. Un gráfico en Open WebUI dibuja una **serie ya verificada** y no calcula el número.

El plan de los últimos cuatro trimestres es código alrededor del kernel: una verificación por trimestre. Identidad y verificación son servicios. **Ningún agente se saltea el kernel.**

El Core no inventa claims al parsear. El ledger se alimenta de evidencia; el claim aparece cuando se cumple el contrato. Ingest (libro) y Query (pregunta) son dos operaciones. El JSON de Docling se guarda inmutable.

## Qué hace CLAIMLEDGER y qué no

Hace:

- dar identidad financiera a una cifra;
- verificarla contra evidencia;
- abstenerse si no hay una sola respuesta demostrable;
- guardar esas afirmaciones como un libro trazable;
- evaluar si acertó el claim, no solo si recuperó texto parecido.

No hace:

- otro lector de PDF (usa Docling; **nunca MinerU**);
- otro buscador genérico;
- otro chat;
- inventar página, recuadro o número;
- responder con una IA como fuente de verdad de la cifra.

La interfaz no contiene la lógica financiera. El buscador no decide el claim. El lector de documentos no interpreta consolidado vs controlante. Open WebUI **dibuja** (ficha, recorte, gráfico); CLAIMLEDGER **verifica**. No copiamos el truco de otra plataforma.

## Test que tiene que pasar

Pregunta: *¿Cuál fue el resultado neto consolidado de BYMA en el 1T26?*

- Verificado: **21.262.335**, consolidado, 31 de marzo de 2026, página 4, fila “RESULTADO NETO DEL PERÍODO”.
- Si preguntan el atribuible a la controlante: **21.259.769**.
- Si la pregunta es ambigua, falta evidencia o hay dos candidatos incompatibles: **abstenerse**.

Si una implementación recupera bien y responde el vecino, falló el producto.

Los gold de Claimprint (`identity_v1` 45 casos, `identity_v2` 26 casos) son **contrato de regresión**, no ejemplos. Son lo que CLAIMLEDGER tiene que seguir entendiendo después de cambiar toda la infraestructura documental. Los tests del kernel corren **sin** Docling.

## Filtro para cada decisión

Antes de agregar un componente, una librería o un atajo, preguntar:

1. ¿Suma a convertir evidencia en una afirmación financiera demostrable?
2. ¿O está reimplementando “qué hay en el documento”, “qué entidades hay”, “dónde buscar” o “cómo mostrar”?
3. **Architecture Gate:** ¿qué problema concreto resuelve que lo actual no puede? “Porque los sistemas modernos usan multi-agent / Graph / MCP” **no alcanza**.

Si es lo segundo, usar el ecosistema. No reconstruirlo.

MVP = demostrar `21.262.335 ≠ 21.259.769` con identidad, evidencia, verified y abstención. Todo lo demás es secundario hasta que eso exista.

```
USAR EL ECOSISTEMA
        ↓
NO REIMPLEMENTAR EL ECOSISTEMA
        ↓
CONSTRUIR LA VERTICAL FINANCIERA
```
