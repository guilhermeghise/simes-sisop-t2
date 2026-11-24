# Relatório — SimES: simulador de E/S e de sistema de arquivos

**Integrantes:** [nome completo de TODOS os integrantes, separados por vírgula]

**Repositório:** [https://github.com/usuario/repositorio — o repositório público do grupo]

<!--
INSTRUÇÕES DO MODELO (apaguem este bloco antes de entregar)
- Este relatório é a entrega: exportem-no para PDF e CADA integrante envia o PDF no Moodle.
- Nomes completos de todos os integrantes e o link do repositório público são obrigatórios
  (linhas acima). Não coloquem matrícula, e-mail, telefone ou outro dado pessoal.
- Mantenham EXATAMENTE os títulos numerados (## 0. ... ## 8.) e os campos em negrito.
- Na seção 3, mantenham X1 a X5 e só as seções dos experimentos do escopo do grupo
  (M1 = X6, M2 = X7, M3 = X8, M4 = X9, M5 = X10, M6 = X11, integração = X12, bônus = X13).
  Apaguem as seções dos experimentos que o grupo não fez.
- Substituam todo texto entre colchetes [ ... ] pelo conteúdo do grupo.
- O campo **Veredito:** aceita só: CONFIRMADA, PARCIALMENTE CONFIRMADA ou REFUTADA.
- Em **Evidências:**, citem arquivos que existam no repositório (resultados/..., graficos/...).
- Antes de entregar, rodem:  python3 ferramentas/validar_entrega.py
-->

## 0. Resumo

[Até 10 linhas: o que o grupo implementou, quais módulos escolheu e os 3 resultados mais importantes.]

## 1. Escopo realizado

| Parte | Situação | Observação |
|---|---|---|
| N1 · Dispositivo (fornecido) | usado | — |
| N2 · Subsistema de E/S (SSTF, SCAN, polling, interrupção) | [completo / parcial] | [ ] |
| N3 · Sistema de arquivos | [completo / parcial] | [ ] |
| N4 · Experimentos X1–X5 e relatório | [completo / parcial] | [ ] |
| [M? · nome do módulo] | [completo / parcial] | [ ] |
| [Integração (grupos de 4)] | [completo / parcial] | [ ] |
| [Bônus flash] | [completo / parcial / não feito] | [ ] |

Resultado dos testes automáticos (`python3 executar.py testes`): [cole a última linha, ex.: "Ran 26 tests ... OK (skipped=6)"]

## 2. Implementação

### N2 — Subsistema de E/S

**Onde:** [arquivos e funções]

**Decisões:** [como implementaram SSTF, SCAN, polling e interrupção; casos especiais]

**Dificuldades:** [o que deu trabalho e como resolveram]

### N3 — Sistema de arquivos

**Onde:** [arquivos e funções]

**Decisões:** [resolução de caminhos, tabelas de arquivos abertos, leitura e escrita, unlink com arquivo aberto]

**Dificuldades:** [ ]

### [M? — nome do módulo]

**Onde:** [ ]

**Decisões:** [ ]

**Dificuldades:** [ ]

## 3. Experimentos

### X1 — Escalonadores sob quatro padrões de carga

**Hipótese:** Na carga aleatória, esperamos que o SSTF percorra menos cilindros e tenha uma resposta média menor que o FCFS. Também esperamos que o SCAN tenha uma espera máxima menor que o SSTF nessa carga.

**Fundamentação:** O SSTF escolhe a requisição mais próxima da cabeça, o que tende a reduzir o custo de busca em relação à ordem de chegada do FCFS. Se pedidos próximos continuarem chegando, os mais distantes podem ficar esperando. O SCAN percorre o disco em uma direção antes de inverter, o que tende a reduzir esse problema (Silberschatz, 9ª ed., §10.4).

**Configuração:** Disco rígido simulado de 5.000 cilindros, interrupção e cache desativada. Cada escalonador (FCFS, SSTF e SCAN) atende as mesmas 2.000 requisições de cada carga padronizada (sequencial, aleatória, concentrada e em rajadas), totalizando 12 execuções.

**Resultados:** O p95 é o percentil 95 do tempo entre a chegada e a conclusão da requisição. A espera máxima mede o maior tempo entre a chegada e o início do atendimento.

| Carga | Escalonador | Deslocamento (cilindros) | Resposta média (ms) | Resposta p95 (ms) | Espera máxima (ms) | Vazão (req/s) |
|---|---|---:|---:|---:|---:|---:|
| Sequencial | FCFS | 7.184.093 | 10.241,05 | 19.565,45 | 20.598,06 | 61,48 |
| Sequencial | SSTF | 2.336.365 | 17,39 | 32,79 | 37,44 | 167,49 |
| Sequencial | SCAN | 2.469.069 | 23,21 | 43,65 | 48,59 | 167,41 |
| Aleatória | FCFS | 3.316.472 | 50,10 | 145,09 | 193,52 | 82,45 |
| Aleatória | SSTF | 2.631.714 | 20,99 | 48,61 | 116,65 | 82,45 |
| Aleatória | SCAN | 3.372.680 | 31,53 | 65,06 | 116,73 | 82,36 |
| Concentrada | FCFS | 1.864.164 | 19,80 | 48,57 | 96,02 | 83,81 |
| Concentrada | SSTF | 1.613.030 | 15,02 | 37,20 | 130,52 | 83,81 |
| Concentrada | SCAN | 3.338.708 | 33,20 | 68,33 | 118,75 | 83,70 |
| Rajadas | FCFS | 3.341.490 | 266,97 | 505,32 | 597,29 | 83,46 |
| Rajadas | SSTF | 209.811 | 147,49 | 277,72 | 296,99 | 84,42 |
| Rajadas | SCAN | 199.955 | 148,62 | 278,70 | 285,44 | 84,43 |

**Evidências:** `resultados/es.csv` (linhas de X1), `graficos/X1_resposta_media_ms.png`, `graficos/X1_espera_max_ms.png` e `graficos/X1_deslocamento_total.png`.

**Análise:** Na carga aleatória, o SSTF percorreu cerca de 21% menos cilindros que o FCFS e reduziu em 58% a resposta média. A vazão ficou igual nos dois casos, pois as 2.000 requisições terminaram no mesmo instante simulado. A espera máxima do SCAN, de 116,727 ms, ficou 0,074 ms acima da do SSTF, contrariando a segunda parte da hipótese. Em rajadas, o SCAN teve a menor espera máxima (285,44 ms) e o menor deslocamento, com 50 pedidos disponíveis de uma vez em cada rajada.

A carga sequencial alterna dois processos que acessam regiões distantes do disco. O FCFS preserva essa alternância e acumula fila. O SSTF e o SCAN conseguem atender pedidos próximos sem cruzar o disco a cada chegada. Na carga concentrada, o SSTF teve a menor média e a maior espera máxima. Esse resultado é compatível com a preferência por pedidos próximos, mas uma espera máxima isolada não demonstra inanição. Nessa carga, a ida do SCAN à borda também ajuda a explicar o seu deslocamento maior, pois o modelo cobra o movimento mesmo quando não há pedidos naquele trecho.

O simulador atende uma requisição por vez, sem cache neste experimento. Isso ajuda a isolar o custo mecânico e a ordem de atendimento. Na prática, a camada de blocos do Linux pode mesclar pedidos adjacentes e usar várias filas. No Windows, o Storport encaminha pedidos de forma assíncrona ao driver. O macOS oferece drivers de blocos para protocolos de armazenamento específicos. Essas diferenças limitam a aplicação direta dos tempos simulados. [Linux blk-mq](https://docs.kernel.org/block/blk-mq.html), [Windows Storport](https://learn.microsoft.com/en-us/windows-hardware/drivers/storage/storport-i-o-model), [Apple BlockStorageDeviceDriverKit](https://developer.apple.com/documentation/blockstoragedevicedriverkit).

**Veredito:** PARCIALMENTE CONFIRMADA

### X2 — Polling × interrupção conforme o dispositivo

**Hipótese:** Nas cargas aleatória e sequencial, esperamos que a interrupção use uma fração menor de CPU que o polling no disco rígido. No dispositivo rápido, esperamos que a ordem se inverta e o polling use menos CPU.

**Fundamentação:** No polling, o modelo cobra CPU durante todo o atendimento. Por interrupção, cobra 0,017 ms por bloco pela interrupção e pela cópia. O disco rígido acrescenta busca e rotação ao tempo de transferência. Já o dispositivo rápido não tem esses dois custos e leva 0,008 ms por bloco, abaixo dos 0,017 ms cobrados por interrupção (Silberschatz, 9ª ed., §§13.2.1–13.2.2 e `simes/parametros.py`).

**Configuração:** FCFS, sem cache, com 2.000 requisições por execução. Foram cruzados dois dispositivos (HDD e rápido), duas cargas (aleatória e sequencial) e dois modos de CPU (polling e interrupção), totalizando oito execuções. O indicador é o tempo de CPU gasto com E/S como porcentagem do tempo total simulado.

**Resultados:**

| Dispositivo | Carga | CPU com polling (%) | CPU com interrupção (%) |
|---|---|---:|---:|
| HDD | Aleatória | 86,2832 | 1,1213 |
| HDD | Sequencial | 99,9977 | 0,8361 |
| Rápido | Aleatória | 0,5280 | 1,1219 |
| Rápido | Sequencial | 1,0739 | 2,2821 |

**Evidências:** `resultados/es.csv` (linhas de X2) e `graficos/X2_cpu.png`.

**Análise:** No HDD, o polling cobra da CPU a busca, a rotação e a transferência. Com a carga sequencial, o disco passou quase todo o tempo atendendo pedidos, e o polling consumiu 99,9977% do tempo simulado. A interrupção caiu para 0,8361% porque cobra um custo fixo por bloco. No dispositivo rápido, só há custo de transferência. Como 0,008 ms por bloco é menos que 0,017 ms, o polling usou menos CPU nas duas cargas. Para cada par de dispositivo e carga, o modo de CPU não alterou a vazão nem a resposta média, pois o simulador contabiliza o custo de CPU separadamente e não o soma ao tempo de atendimento do disco.

Na prática, o Linux permite polling de conclusões com `io_uring` em dispositivos compatíveis. O Storport do Windows e o DriverKit do macOS oferecem rotinas para tratar interrupções de hardware. O dispositivo rápido do X2 usa um tempo fixo por bloco e o experimento não inclui DMA nem interrupções agrupadas. A inversão observada depende desses parâmetros e não indica que o polling sempre usará menos CPU em um SSD real. [Linux io_uring](https://github.com/axboe/liburing/blob/master/man/io_uring_setup.2), [Windows Storport](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/storport/nc-storport-hw_interrupt), [Apple DriverKit](https://developer.apple.com/documentation/driverkit/iointerruptdispatchsource).

**Veredito:** CONFIRMADA

### X3 — Acesso sequencial × direto

**Hipótese:** Esperamos que o tempo médio de read seja menor na carga de compilador, com leituras sequenciais, do que no banco de dados, com posições aleatórias. Esperamos também que seek não gere acessos ao disco. A média de todas as operações depende da composição de cada carga e não deve ser tomada como uma comparação isolada dos métodos de acesso.

**Fundamentação:** Leituras consecutivas aproveitam a alocação contígua e evitam parte dos custos de busca e rotação do HDD. Acesso direto permite escolher a posição, mas o seek do sistema de arquivos só atualiza o handle; o custo físico aparece na leitura ou escrita seguinte. As cargas oficiais têm arquivos, tamanhos e operações diferentes (Silberschatz, 9ª ed., cap. 11; simes/disco.py e simes/arquivos/camada_bloco.py).

**Configuração:** Duas cargas oficiais, compilador e banco_dados, no HDD, com alocação contígua e sem cache. O compilador executa três builds, lendo fontes/cabeçalhos e criando objetos; o banco acessa uma tabela de 64 MiB em 3.000 transações com posições aleatórias e log de acréscimo. A hipótese foi registrada em 332de0e antes da execução de `python3 executar.py experimentos X1 X2 X3`.

**Resultados:** As duas execuções terminaram sem erros. As médias por operação são tempos de disco simulados.

| Indicador | Compilador | Banco de dados |
|---|---:|---:|
| Operações | 3.904 | 6.602 |
| Acessos totais | 5.400 | 3.610 |
| Acessos por operação | 1,3832 | 0,5468 |
| Tempo total (ms) | 11.986,6500 | 19.846,9600 |
| Tempo médio geral (ms) | 3,0704 | 3,0062 |
| Tempo médio de read (ms) | 1,4828 | 5,4918 |
| Tempo médio de write (ms) | 0,9068 | 5,5425 |
| Acessos médios por read/write | 1 / 1 | 1 / 1 |
| Tempo médio de open (ms) | 8,2049 | 4,2500 |
| Acessos médios por open | 3 | 2 |
| Operações seek / custo (ms) | 0 / não se aplica | 3.000 / 0 |

**Evidências:** `resultados/arquivos.csv` e `resultados/arquivos_por_operacao.csv` (X3), `resultados/experimentos.csv` e `graficos/X3_tempo_por_operacao.png`. Os gráficos foram gerados com `python3 graficos.py`.

**Análise:** O read do compilador custou cerca de 73% menos tempo que o do banco, apesar de ambos acessarem um bloco por leitura. A diferença aparece na localidade física: no modelo, blocos consecutivos evitam rotação adicional, enquanto posições aleatórias pagam busca e rotação com maior frequência. As escritas também foram mais baratas no compilador, mas incluem padrões e tamanhos diferentes, não uma comparação controlada do mesmo arquivo. O banco fez 3.000 seeks, todos sem acesso e sem tempo de disco: só a operação seguinte efetua a transferência.

A média geral do banco (3,0062 ms) ficou ligeiramente abaixo da do compilador (3,0704 ms), embora seus reads fossem mais lentos. Os seeks gratuitos são cerca de 45% de suas operações e diluem essa média. Já o compilador repete aberturas, criações, fechamentos e remoções; seus opens percorrem três diretórios, contra dois no banco. O tempo total maior do banco também depende do maior número de operações. Assim, o resultado confirma a previsão sobre leituras e seek, mas não permite atribuir toda diferença agregada somente ao método de acesso. Essa distinção segue a separação entre métodos de acesso e operações de arquivos do cap. 11 do livro. Não houve falha de alocação nem realocação nas duas cargas.

**Veredito:** CONFIRMADA

### X4 — Custo de resolver caminhos conforme a profundidade

**Hipótese:** Esperamos que open em um caminho com d diretórios abaixo da raiz faça exatamente d + 1 leituras de diretório, para d de 1 a 10. O tempo médio deve crescer com a profundidade nas cargas oficiais, sem custo de escrita no open.

**Fundamentação:** O modelo não tem cache de diretórios: resolver lê a raiz e cada diretório intermediário até localizar o arquivo. Cada diretório ocupa um bloco. Assim, acrescentar um componente de diretório acrescenta uma leitura, embora o tempo por leitura dependa da posição física e da continuidade no HDD (Silberschatz, 9ª ed., cap. 11; regras de simes/arquivos/sistema.py).

**Configuração:** Dez cadeias oficiais com profundidade de 1 a 10 diretórios abaixo da raiz, alocação contígua, HDD e sem cache. Em cada cadeia, um arquivo de 4.096 bytes é aberto, lido e fechado 20 vezes. A hipótese foi registrada em a7b6c26 antes de `python3 executar.py experimentos X1 X2 X3 X4`. As médias abaixo consideram apenas open, separando o custo de construção da árvore.

**Resultados:** As dez execuções terminaram sem erros; cada profundidade teve 20 opens.

| Diretórios abaixo da raiz | Leituras por open | Tempo médio por open (ms) |
|---|---:|---:|
| 1 | 2 | 4,2500 |
| 2 | 3 | 4,2900 |
| 3 | 4 | 4,3300 |
| 4 | 5 | 4,3700 |
| 5 | 6 | 4,4100 |
| 6 | 7 | 4,4500 |
| 7 | 8 | 4,4900 |
| 8 | 9 | 4,5300 |
| 9 | 10 | 4,5700 |
| 10 | 11 | 4,6100 |

**Evidências:** `resultados/arquivos_por_operacao.csv` (X4, open), `resultados/arquivos.csv` (X4), `resultados/experimentos.csv` e `graficos/X4_open_por_profundidade.png`, gerado por `python3 graficos.py`.

**Análise:** O número de leituras foi exatamente d + 1 em todas as profundidades: raiz mais d diretórios até o pai do arquivo. Open não grava e não transfere o conteúdo do arquivo; este é lido pela operação read seguinte. A construção com alocação contígua coloca os diretórios e o arquivo em blocos consecutivos, todos no mesmo cilindro neste experimento. Ao voltar ao bloco da raiz, o disco paga a latência rotacional, mas as leituras dos diretórios seguintes aproveitam a sequência. Por isso o tempo foi 4,17 + 0,04 × (d + 1) ms, de 4,25 a 4,61 ms, aumentando 0,04 ms por nível.

A linearidade dos acessos decorre da regra de resolução de caminhos do modelo, conforme o cap. 11 do livro. A inclinação do tempo depende desta disposição física: não significa pagar uma busca e uma rotação completas a cada nível. Repetir o open não reduziu o custo porque o simulador não mantém cache de diretórios. Em sistemas reais, caches de nomes e metadados podem evitar leituras físicas em aberturas repetidas, como discutido na seção 4.

**Veredito:** CONFIRMADA

### X5 — Tabelas de arquivos abertos com vários processos

**Hipótese:** Na carga de servidor web, esperamos um máximo de três handles por processo e 24 entradas somadas nos oito trabalhadores. A tabela global deve ter menos entradas que essa soma, no máximo 12 arquivos distintos, e algum arquivo deve apresentar contador de aberturas maior que um.

**Fundamentação:** Cada trabalhador abre três páginas antes das leituras e fechamentos. As páginas vêm de um conjunto de 12 arquivos, permitindo compartilhar FCBs entre processos. A tabela global representa arquivos distintos e soma suas aberturas, enquanto cada abertura tem modo e posição na tabela do processo (Silberschatz, 9ª ed., cap. 11; simes/cargas_arquivos.py e simes/arquivos/estruturas.py).

**Configuração:** Carga oficial servidor_web, oito trabalhadores, 12 páginas, 40 rodadas e três aberturas por trabalhador em cada rodada. Todos os trabalhadores abrem antes da fase de leitura e só fecham depois dela. HDD, alocação contígua e sem cache. A hipótese foi registrada em 6b723b4 antes de `python3 executar.py experimentos X1 X2 X3 X4 X5`.

**Resultados:** A carga executou 6.279 operações sem erros, incluindo 960 opens, 4.346 reads e 960 closes.

| Indicador | Máximo observado |
|---|---:|
| Entradas na tabela global | 12 |
| Handles de um processo | 3 |
| Soma das tabelas dos processos | 24 |
| Contador de aberturas de um arquivo | 6 |

Foram 17.824 acessos, média de 2,8387 por operação e 1,4897 ms por operação. Cada open fez duas leituras de diretório, com 4,2730 ms de média; close não fez acessos porque a carga só lê os arquivos abertos.

**Evidências:** `resultados/arquivos.csv` (X5 e indicadores max_tabela_global, max_tabela_processo, max_soma_tabelas_processo e max_contador_aberturas), `resultados/arquivos_por_operacao.csv`, `resultados/experimentos.csv` e `graficos/X5_tabelas.png`, gerado por `python3 graficos.py`.

**Análise:** A soma máxima de 24 handles resulta das três aberturas de cada um dos oito trabalhadores. A tabela global chegou a 12 entradas, uma por FCB distinto, e não a 24: várias aberturas compartilham o mesmo arquivo. O contador máximo de seis mostra um arquivo simultaneamente aberto por seis processos, sem exigir que os oito escolham a mesma página. O conjunto de páginas limita a tabela global a 12, e esta execução chegou a esse limite.

Os quatro indicadores são máximos coletados ao longo da carga e não precisam ocorrer no mesmo instante. Não é correto somar o contador máximo de um arquivo como se fosse o contador de todos os 12. O contador representa referências abertas, e não quantidade de leituras; cada close retira uma referência e a entrada global sai quando sua contagem chega a zero. As posições permanecem nos handles de cada processo, permitindo leituras independentes. A separação ilustra as tabelas global e por processo discutidas no cap. 11 do livro. O experimento mede tamanhos de tabelas, não bytes de memória do kernel nem concorrência de execução real.

**Veredito:** CONFIRMADA

### X6 — Cache de blocos (M1)

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### X7 — Escalonadores avançados e inanição (M2)

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### X8 — DMA e buffering (M3)

**Hipótese:** Esperamos que DMA use 0,018 ms de CPU por requisição, independente dos blocos. A interrupção deve custar menos para um bloco (0,017 ms), mas mais para 8, 64 e 256 blocos. No buffering, esperamos que dois e três buffers reduzam o tempo total frente a um buffer e empatem entre si nas taxas constantes escolhidas; o terceiro pode reduzir a espera do produtor quando o dispositivo é mais lento.

**Fundamentação:** DMA cobra uma programação de 0,003 ms e uma interrupção de 0,015 ms. Interrupção programada cobra 0,017 ms por bloco. Com um buffer, produção e gravação são serializadas; com dois, esses estágios podem se sobrepor, mas o gargalo continua sendo o estágio mais lento. O terceiro buffer amplia a fila sem aumentar essa taxa em um fluxo determinístico de blocos idênticos (Silberschatz, 9ª ed., §§13.2.3 e 13.4.2; simes/parametros.py).

**Configuração:** Hipótese registrada em 4e46129 antes de `python3 executar.py experimentos X1 X2 X3 X4 X5 X8`. Na parte de CPU: HDD, FCFS, sem cache, 1.000 requisições aleatórias por execução, semente 11, intervalo médio de 40 ms, requisições de 1, 8, 64 ou 256 blocos, nos modos polling, interrupção e DMA (12 execuções). No buffering: 500 blocos, produção de 2 ms/bloco, consumo de 0,5, 2 ou 8 ms/bloco, com 1, 2 ou 3 buffers (nove execuções).

**Resultados:** Todas as 21 execuções terminaram com status ok. Os percentuais de CPU abaixo usam o tempo total de cada execução como denominador.

| Blocos por requisição | Polling (%) | Interrupção (%) | DMA (%) | CPU de interrupção por req. (ms) | CPU DMA por req. (ms) |
|---|---:|---:|---:|---:|---:|
| 1 | 25,1715 | 0,0423 | 0,0448 | 0,017 | 0,018 |
| 8 | 25,8677 | 0,3383 | 0,0448 | 0,136 | 0,018 |
| 64 | 31,4371 | 2,7059 | 0,0448 | 1,088 | 0,018 |
| 256 | 50,5224 | 10,8204 | 0,0448 | 4,352 | 0,018 |

Os custos por requisição são os das constantes do modelo; os percentuais dos CSVs foram arredondados a quatro casas.

| Consumo (ms/bloco) | Buffers | Tempo total (ms) | Bloqueio do produtor (ms) | Utilização do dispositivo (%) |
|---|---|---:|---:|---:|
| 0,5 | 1 | 1.250,0 | 249,5 | 20,0000 |
| 0,5 | 2 | 1.000,5 | 0,0 | 24,9875 |
| 0,5 | 3 | 1.000,5 | 0,0 | 24,9875 |
| 2 | 1 | 2.000,0 | 998,0 | 50,0000 |
| 2 | 2 | 1.002,0 | 0,0 | 99,8004 |
| 2 | 3 | 1.002,0 | 0,0 | 99,8004 |
| 8 | 1 | 5.000,0 | 3.992,0 | 80,0000 |
| 8 | 2 | 4.002,0 | 2.988,0 | 99,9500 |
| 8 | 3 | 4.002,0 | 2.980,0 | 99,9500 |

**Evidências:** `resultados/es.csv` (X8), `resultados/buffering.csv`, `resultados/experimentos.csv`, `graficos/X8_cpu.png` e `graficos/X8_buffering.png`, gerados com `python3 graficos.py`.

**Análise:** DMA custa 0,003 + 0,015 = 0,018 ms por requisição, enquanto interrupção cobra 0,017 ms por bloco. Para um bloco, DMA custa cerca de 5,9% mais CPU que interrupção. Para 8, 64 e 256 blocos, a redução de CPU por requisição é de aproximadamente 86,8%, 98,3% e 99,6%. A vantagem decorre de amortizar a programação e a interrupção final sobre toda a transferência, conforme §13.2.3 do livro. O polling cresce com o tempo de atendimento do HDD. Para um mesmo tamanho de requisição, os três modos mantêm o mesmo tempo total: o simulador contabiliza CPU separadamente do dispositivo, e não demonstra uma aceleração da transferência por DMA.

Com um buffer, o tempo é 500 × (2 + consumo), pois gerar e gravar não se sobrepõem. Com dois ou três buffers, o tempo é 2 + consumo + 499 × max(2, consumo): há enchimento inicial e esvaziamento final, mas o regime permanente segue o estágio mais lento. Para consumo de 0,5 ms, o produtor limita a utilização do dispositivo a cerca de 25%; para 2 e 8 ms, a utilização chega perto de 100%. O terceiro buffer reduziu o bloqueio em apenas 8 ms no consumidor lento, de 2.988 para 2.980 ms, sem mudar os 4.002 ms totais. Isso confirma a distinção entre capacidade de fila e vazão: mais buffers não aceleram o gargalo. A igualdade entre duplo e circular vale para estes tempos constantes; não foi avaliada variabilidade de produção ou consumo (§13.4.2).

**Veredito:** CONFIRMADA

### X9 — Links e compartilhamento (M4)

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### X10 — Proteção e travas (M5)

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### X11 — Métodos de alocação (M6)

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### X12 — Integração ponta a ponta

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

### X13 — Armazenamento flash (bônus)

**Hipótese:** [ ]

**Fundamentação:** [ ]

**Configuração:** [ ]

**Resultados:** [ ]

**Evidências:** [ ]

**Análise:** [ ]

**Veredito:** [ ]

## 4. Relação com sistemas reais

[Para cada tema do escopo, relacionem o que o simulador mostrou com o que Windows, Linux e
macOS fazem de fato. Exemplos: escalonadores de E/S do Linux (mq-deadline, BFQ, none); cache
de páginas e gravação periódica; cache de diretórios (dentry cache); FAT/exFAT nos pendrives;
estruturas do ext4, do NTFS e do APFS; travas mandatórias do Windows × consultivas do Linux.]

## 5. Limitações do simulador

[O que o modelo simplifica e como isso pode ter afetado as conclusões.]

## 6. Conclusões

[3 a 6 conclusões objetivas.]

## 7. Referências

- SILBERSCHATZ, A.; GALVIN, P. B.; GAGNE, G. *Operating System Concepts*. 9. ed. Wiley, 2013.
- [Outras fontes consultadas, com link]

## 8. Declaração de autoria e uso de IA

**Quem fez o quê:** [divisão do trabalho entre os integrantes]

**Uso de ferramentas de IA:**

| Ferramenta | Finalidade | Onde foi usada (arquivos ou seções) |
|---|---|---|
| [ex.: nenhuma] | [ ] | [ ] |
