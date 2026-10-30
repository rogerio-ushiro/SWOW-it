# Guia de tradução SWOW-EN → italiano

Regras fixas para todos os lotes do Epic `traducao-swow-en-para-italiano`. Qualquer dúvida de caso novo vira linha neste guia antes de continuar.

## Tabelas

| Arquivo | Conteúdo |
|---|---|
| `cues.tsv` | todos os cues (inclusive os que também aparecem como resposta) |
| `respostas.tsv` | só as respostas que **não** são cue |
| `marcadores.tsv` | os marcadores do `complete` ("Unknown word", "No more responses") |

Colunas (TSV, UTF-8, sem aspas): `en`, `it`, `status`, `nota`.

- **Chave = a string inglesa exata** (maiúsculas e minúsculas contam). Uma string aparece em uma só tabela, uma só vez.
- Uma palavra que é cue e resposta vive só em `cues.tsv`; a tradução vale nos dois usos (é isso que mantém o `coverage` consistente).
- **Uma tradução por palavra**, independente do cue em que apareceu (decisão de 2026-10-30). Se o sentido varia, escolher o sentido que **mais aparece nas respostas do SWOW** (conferir no `strength.R123` as respostas mais frequentes do cue), e não o sentido de dicionário; marcar `ambiguo` conforme o critério abaixo.

## Status

| status | quando |
|---|---|
| `ok` | equivalente direto e natural |
| `ambiguo` | mais de um sentido relevante **e o italiano não cobre os mesmos sentidos** que a palavra inglesa; `it` traz o dominante nas respostas e `nota` traz a alternativa (ex.: `bat` → `pipistrello`; alt.: mazza). Se a polissemia é a mesma nas duas línguas (*earth*/*terra*, *delta*/*delta*), o status é `ok` |
| `sem_equivalente` | sem palavra italiana natural, inclusive preposições e palavras gramaticais (*at*) e conceitos culturais (*gravy*); `it` traz a aproximação ou perífrase mais curta, e se não houver, repete `en` |
| `nome_proprio` | pessoa, lugar, marca, obra: forma italiana se existir (Germany → Germania), senão a mesma |
| `erro_digitacao` | `en` é erro de digitação ou forma inexistente; `it` traduz a forma corrigida e `nota` traz a correção |

**A coluna `it` nunca fica vazia.**

## Regras de tradução

1. **Flexões:** cada forma é traduzida por si, mantendo número, tempo e grau (*elections* → *elezioni*, *elect* → *eleggere*). Não normalizar para o lema.
2. **Caixa (decidido):** a saída preserva o padrão da string inglesa exata: `aa` → minúscula, `Aa` → inicial maiúscula, `AA` → tudo maiúsculo. Nunca fundir variantes de caixa. (O validador avisa quando o padrão não bate; nomes próprios que em italiano pedem outra caixa são exceção e vão com nota.)
3. **Várias palavras** (*a lot*, *cream cheese*): traduzir como unidade, com a expressão italiana natural.
4. **Siglas e marcas** (*DNA*, *NASA*, *Google*): usar a forma italiana corrente (DNA, NASA, Google).
5. **Falsos amigos:** o italiano não pode ser a palavra de aparência parecida com sentido outro (*pretend* ≠ *pretendere*; *ma* é "mamma", não "ma").
6. **Registro:** manter o registro (gíria → gíria italiana equivalente, se existir; senão `sem_equivalente`).
7. **Coerência:** a mesma palavra inglesa recebe sempre a mesma tradução, em qualquer lote.
8. **Palavra que um italiano realmente diria:** preferir a forma corrente e coloquial à dicionarizada ou literária (*secco* e não *essiccato*; *cuore spezzato* e não *crepacuore*; *ahia* e não *ahi*).
9. **Falso amigo em italiano:** a palavra italiana escolhida não pode ter um segundo sentido forte que desvie a associação (*provato* = esausto, *quanto* = how much, *metro* = unidade de medida).
10. **Colisões previsíveis:** quando a tradução é a mesma de outro cue ou resposta (*spiaggia* para *beach* e *seaside*), registrar na `nota`; elas são medidas na Task 6.0.

## Colisões (duas palavras inglesas que viram a mesma italiana)

Regra fiel ao original, aplicada na Story 6:

- contagens e `N` do `strength` somam; `unknown` soma;
- `Types` do `responseStats` é o **conjunto** de cues distintos (não soma);
- repetição criada pela tradução (duas respostas do mesmo participante viram a mesma palavra) é **mantida**, sem reaplicar deduplicação;
- as colisões são medidas na Task 6.0 e documentadas.

## Marcadores

Forma fixa em `marcadores.tsv`; valem só no `complete` italiano. No `R100` continuam `NA`, como no original.

## Fluxo de um lote

1. O lote de entrada é uma lista de `en` (extraída de `vocab_cues.tsv` / `vocab_respostas.tsv`), **cada palavra acompanhada das ~10 respostas mais frequentes dela no `strength.R123`**; o sentido é escolhido por essas associações, não pelo dicionário (confirmado no piloto, 2026-10-30).
2. A tradução grava as linhas em `cues.tsv` ou `respostas.tsv`.
3. `python3 -I scripts/check_table.py <tabela>` valida: colunas, `it` não vazio, status válido, chave única, padrão de caixa.
4. Só com o validador sem erro o lote conta como concluído.

## Decisões deste guia

- 2026-10-30: uma tradução por palavra (não por cue); sentido variável → status `ambiguo`. Refinar com exceções por cue só se o piloto mostrar muitas ambíguas.
