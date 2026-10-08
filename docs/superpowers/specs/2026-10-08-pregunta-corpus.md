# Pregunta, corpus, verificación, pantalla

Acuerdo de esta conversación. El plan de implementación está en `docs/superpowers/plans/2026-10-08-pregunta-corpus.md`.

## Circuito

1. El usuario pregunta.
2. Se buscan las filas en los JSON ya parseados (las tablas del estado de resultados).
3. Cada cifra se verifica contra el libro y se valida la identidad: empresa, trimestre, grupo o controlante, renglón.
4. La pantalla muestra una sola respuesta.
5. El modelo escribe una frase con esos datos. Si no puede, la pantalla igual muestra la ficha verificada, con una frase fija armada con esos mismos datos.

DocLang no se abre al preguntar. Es una copia de intercambio del mismo documento.

## Prueba manual que tiene que pasar

Pregunta: «armá una tabla con todos los trimestres de BYMA».

La pantalla muestra el resultado neto consolidado de 1T26 (`21262335`) y de 2T26 (`81956525`), cada uno con su identidad. No muestra `21259769`. No dice «me abstengo» debajo de «verificado». No dibuja el gráfico.

## Lo que no cambia

- El oro sigue siendo `21262335` contra `21259769`.
- `query` sigue callando con `ambiguous_period` cuando piden un resultado neto sin decir el trimestre y sin pedir la tabla de todos.
- El modelo no elige el número ni inventa la identidad.
- Una fila de la controlante y una del grupo, aunque estén en la misma tabla, siguen siendo dos cosas distintas.

## Fuera de este corte

No se responde cualquier pregunta del PDF. Este corte deja lista la prueba de la tabla de trimestres del resultado neto, que es la que falló en la captura.
