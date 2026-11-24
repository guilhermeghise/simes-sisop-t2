# Relatório — SimES: simulador de E/S e de sistema de arquivos

**Integrantes:** Eduardo Ferrari, Guilherme Ghise Rossoni

**Repositório:** https://github.com/guilhermeghise/simes-sisop-t2

## 0. Resumo

Implementamos o núcleo N1–N4 e o módulo M3 do SimES, com SSTF, SCAN, polling, interrupção, operações de arquivos, DMA e buffering. Executamos X1–X5 e X8 com as cargas e os parâmetros oficiais. Em X1, SSTF reduziu a resposta média da carga aleatória em cerca de 58% frente a FCFS, mas SCAN não teve a menor espera máxima nessa carga. Em X4, cada diretório adicional acrescentou uma leitura ao open. Em X8, DMA teve custo fixo por requisição, e o buffering duplo atingiu o mesmo tempo total do circular nas taxas constantes avaliadas. Os testes do escopo e a validação automática passaram.

## 1. Escopo realizado

| Parte | Situação | Observação |
|---|---|---|
| N1 · Dispositivo (fornecido) | usado | HDD e dispositivo rápido, parâmetros oficiais |
| N2 · Subsistema de E/S (SSTF, SCAN, polling, interrupção) | completo | Desempate pela ordem da fila; SCAN visita a borda |
| N3 · Sistema de arquivos | completo | Caminhos, criação, tabelas, acesso, fechamento e remoção |
| N4 · Experimentos X1–X5 e relatório | completo | Hipóteses registradas antes das respectivas execuções |
| M3 · DMA e buffering | completo | DMA; buffers simples, duplo e circular; X8 |
| Integração (grupos de 4) | não se aplica | Dupla; integração desativada |
| Bônus flash | não feito | Fora do escopo |

Resultado dos testes automáticos (`python3 executar.py testes`): `Ran 43 tests — OK (skipped=8)`. São 35 testes aprovados e oito pulados, todos de módulos ou integração fora do escopo.

## 2. Implementação

### N2 — Subsistema de E/S

**Onde:** `simes/es/escalonadores.py`, classes `SSTF` e `SCAN`; `simes/es/cpu.py`, função `custo_cpu`.

**Decisões:** SSTF seleciona a menor distância e preserva a ordem de chegada nos empates. SCAN inclui pedidos no mesmo cilindro como à frente e visita a borda antes de inverter. Polling custa toda a duração do atendimento; interrupção custa 0,017 ms por bloco. Mantivemos FCFS e o simulador de eventos fornecidos.

**Dificuldades:** A ida do SCAN até a borda precisa entrar no custo, mesmo sem pedido ali; os testes com a fila do livro conferem o deslocamento. CPU e duração do dispositivo são indicadores separados no modelo.

### N3 — Sistema de arquivos

**Onde:** `simes/arquivos/sistema.py`, métodos `resolver`, `mkdir`, `create`, `open`, `read`, `write`, `seek`, `close` e `unlink`.

**Decisões:** Cada diretório visitado custa uma leitura. Os handles guardam modo e posição por abertura; a tabela global tem uma entrada por FCB e soma as aberturas. A leitura para no EOF, e seek além do EOF não aloca blocos. A escrita estende a alocação e aplica os acessos extras de realocação antes dos blocos escritos. Append consulta o tamanho atual a cada escrita. Escritas vazias não alteram metadados. O close grava o pai quando o FCB está sujo, limpa a marca e decrementa a contagem. O unlink remove o nome imediatamente, mas um arquivo aberto conserva seus blocos até o último close. Foram mantidos os ganchos de permissão e trava previstos no esqueleto.

**Dificuldades:** A posição pode estar além do EOF sem justificar leitura ou alocação. Outra abertura pode aumentar o arquivo antes de um append. Há testes adicionais para esses casos, custos de realocação, ENOSPC, modos inválidos e remoção com múltiplas aberturas. Nenhum conteúdo de bytes é armazenado: as operações simulam quantidades, metadados e acessos.

### M3 — DMA e buffering

**Onde:** `simes/es/cpu.py`, função `custo_cpu`; `simes/es/buffering.py`, função `simular_buffering`.

**Decisões:** DMA cobra as constantes de programação e de uma interrupção final, somando 0,018 ms por requisição. No buffering, um vetor circular registra quando cada buffer fica livre. O produtor aguarda o término de sua produção anterior e a liberação do buffer; o dispositivo aguarda os dados prontos e sua gravação anterior. O buffer fica ocupado até o fim da gravação. Retornamos duração, espera do produtor e utilização do dispositivo; carga vazia retorna zeros.

**Dificuldades:** Liberar um buffer no início da gravação permitiria sobreposição indevida. Os testes verificam bloqueio com consumidor lento, produtor lento, taxas iguais, zero blocos e tempos nulos. Dois buffers já sobrepõem produção e consumo no cenário determinístico, portanto o terceiro pode reduzir bloqueio sem reduzir o tempo total.

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

## 4. Relação com sistemas reais

**Escalonamento e conclusão de E/S.** O X1 isola uma fila de um HDD. O Linux usa a infraestrutura [blk-mq](https://docs.kernel.org/block/blk-mq.html), com filas de software e de hardware; isso limita a transposição das médias do simulador para máquinas atuais. No Windows, o [Storport](https://learn.microsoft.com/en-us/windows-hardware/drivers/storage/storport-i-o-model) trabalha com pedidos assíncronos. O macOS oferece interfaces de drivers de blocos no [BlockStorageDeviceDriverKit](https://developer.apple.com/documentation/blockstoragedevicedriverkit). As interfaces reais não equivalem diretamente aos três algoritmos didáticos. X2 mostra como o custo relativo de polling e interrupção muda com a velocidade do dispositivo; seus valores fixos não modelam todas as estratégias reais.

**Arquivos, caminhos e aberturas.** X3 evidencia localidade e custos de metadados; X4 cobra uma leitura por diretório em todas as aberturas. O Linux mantém a [dcache](https://docs.kernel.org/filesystems/path-lookup.html), permitindo resolver componentes já conhecidos sem repetir todo o acesso ao armazenamento. Portanto, a reta observada no X4 não prevê uma leitura física por componente em todo open real. X5 distingue arquivos distintos de aberturas: vários handles podem referenciar o mesmo arquivo. No Linux, referências permitem continuar usando um arquivo removido; no macOS, o manual de [unlink](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/unlink.2.html) também descreve a liberação após o fechamento das últimas referências. No Windows, a [exclusão e o fechamento](https://learn.microsoft.com/en-us/windows/win32/fileio/closing-and-deleting-files) dependem dos handles e das regras de compartilhamento. O comportamento do simulador aproxima a remoção Unix; ele não reproduz toda a semântica de compartilhamento do Windows.

**DMA e buffers.** O Linux usa sua [API de DMA](https://docs.kernel.org/core-api/dma-api-howto.html) para mapear memória acessível ao dispositivo. O Windows oferece [técnicas de programação DMA](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/dma-programming-techniques), e o macOS fornece [IODMACommand](https://developer.apple.com/documentation/kernel/iodmacommand) para converter referências de memória em endereços de E/S. Essas interfaces exigem gerenciamento que não aparece no custo fixo de X8. Buffers permitem sobreposição, mas não aumentam a taxa do estágio mais lento. O buffering do experimento é uma fila finita entre produtor e dispositivo, diferente da cache de arquivos; o [buffering de arquivos do Windows](https://learn.microsoft.com/windows/win32/fileio/file-buffering) tem regras próprias para operações com e sem cache.

## 5. Limitações do simulador

- Os tempos são simulados por fórmulas fixas; não são medições de desempenho deste computador. As sementes são fixas e não foram calculados intervalos de confiança para uma população de cargas.
- O HDD não representa todos os detalhes de firmware, paralelismo, reordenação interna, setores ou falhas. O dispositivo rápido é apenas o modelo sem busca e rotação, não um SSD completo.
- O sistema de arquivos usa diretórios de um bloco, FCBs em memória e alocação contígua. Não implementamos ext4, NTFS ou APFS, journaling, recuperação após queda, cache de dados ou de caminhos.
- A camada de arquivos agrupa blocos consecutivos e soma tempos de disco sem fila de E/S. Não habilitamos a integração X12: os tempos de X3–X5 não incluem os escalonadores de X1.
- X3 compara cargas com tamanhos, operações e frequências diferentes. Seek não acessa disco no modelo, e sua presença afeta a média agregada. Assim, a diferença entre cargas não é um efeito isolado do método de acesso.
- A contagem global de X5 é por FCB; a posição é independente por abertura. Não simulamos duplicação de descritores, fork, limites do kernel ou concorrência real.
- DMA só altera a contabilidade de CPU. Não há contenção de barramento, IOMMU, custo de mapeamento, coerência de cache ou agrupamento de interrupções. CPU não é somada ao tempo do disco.
- O buffering usa blocos idênticos e tempos constantes, sem jitter, cópia adicional ou processamento paralelo dentro de um estágio. A igualdade entre dois e três buffers vale para essa configuração e não elimina o valor de buffers extras em cargas variáveis.

## 6. Conclusões

1. SSTF reduziu deslocamento e resposta média frente a FCFS na carga aleatória de X1. A menor espera máxima do SCAN prevista nessa carga não se confirmou.
2. No modelo de X2, interrupções reduzem CPU no HDD, mas o polling custa menos no dispositivo rápido com os parâmetros fornecidos.
3. A localidade das leituras influencia o custo de X3, e a composição da carga impede interpretar a média geral como uma comparação controlada entre métodos de acesso.
4. Resolver mais diretórios aumenta os acessos do open em X4; separar tabelas globais e por processo evita confundir arquivos distintos com suas aberturas em X5.
5. DMA amortiza a programação por requisição, sendo vantajoso frente à interrupção por bloco a partir dos tamanhos maiores avaliados. Com um bloco, 0,018 ms de DMA supera ligeiramente 0,017 ms de interrupção.
6. Dois buffers permitem a sobreposição necessária nas taxas constantes de X8. O terceiro não reduz a duração total observada, embora possa diminuir o bloqueio do produtor.

## 7. Referências

- SILBERSCHATZ, A.; GALVIN, P. B.; GAGNE, G. *Operating System Concepts*. 9. ed. Wiley, 2013. Capítulos 10–13, conforme as referências e regras do esqueleto.
- NOVO MÓR, Filipo. [Esqueleto e README do SimES, 2026/II](https://github.com/ProfessorFilipo/Aulas_SisOp/tree/main/Trabalho_IO_2026II). Regras de custos, parâmetros e configurações oficiais.
- LINUX KERNEL. [Multi-Queue Block IO Queueing Mechanism](https://docs.kernel.org/block/blk-mq.html); [Pathname lookup](https://docs.kernel.org/filesystems/path-lookup.html); [Dynamic DMA mapping Guide](https://docs.kernel.org/core-api/dma-api-howto.html).
- MICROSOFT. [Storport I/O model](https://learn.microsoft.com/en-us/windows-hardware/drivers/storage/storport-i-o-model); [Closing and Deleting Files](https://learn.microsoft.com/en-us/windows/win32/fileio/closing-and-deleting-files); [DMA programming techniques](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/dma-programming-techniques); [File Buffering](https://learn.microsoft.com/windows/win32/fileio/file-buffering).
- APPLE. [BlockStorageDeviceDriverKit](https://developer.apple.com/documentation/blockstoragedevicedriverkit); [unlink(2), manual arquivado do macOS](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/unlink.2.html); [IODMACommand](https://developer.apple.com/documentation/kernel/iodmacommand).

Documentação on-line consultada em 24/11/2026. As interpretações foram limitadas às interfaces documentadas, sem medições em sistemas operacionais reais.

## 8. Declaração de autoria e uso de IA

**Quem fez o quê:** Guilherme Ghise Rossoni ficou responsável por SSTF, SCAN, polling, interrupção, resolução de caminhos, criação e abertura de arquivos e pelos experimentos X1 e X2. Eduardo Ferrari ficou responsável pelas demais operações de arquivos, por DMA e buffering, pelos testes adicionais, pelos experimentos X3, X4, X5 e X8 e pela consolidação do relatório. O professor forneceu o esqueleto, as cargas, as configurações dos experimentos e o validador.

**Uso de ferramentas de IA:** Nós discutimos os requisitos do simulador, pesquisamos os conceitos de sistemas operacionais e definimos a divisão das tarefas. Usamos o OpenAI Codex em etapas do desenvolvimento. Na implementação, a ferramenta ajudou a traduzir as regras do simulador em código Python, linguagem com a qual tínhamos pouca familiaridade. Também recorremos a ela nos testes, na execução dos experimentos e na redação das análises. A tabela detalha os usos na parte de cada integrante.

| Ferramenta | Finalidade | Onde foi usada (arquivos ou seções) |
|---|---|---|
| OpenAI Codex (etapa do Guilherme) | Implementação em Python, execução de testes e experimentos, análise e redação | `simes/es/escalonadores.py` (SSTF e SCAN), `simes/es/cpu.py` (polling e interrupção), `simes/arquivos/sistema.py` (resolver, mkdir, create e open), seções X1 e X2 de `RELATORIO.md` |
| OpenAI Codex (etapa do Eduardo) | Implementação em Python, criação e execução de testes, execução e análise dos experimentos, redação e exportação | `simes/arquivos/sistema.py` (read, write, seek, close e unlink), `simes/es/cpu.py` (DMA), `simes/es/buffering.py`, testes adicionais, `graficos.py` (rótulos de X5), `grupo.json`, seções X3–X5 e X8 e consolidação de `RELATORIO.md`, `ferramentas/exportar_relatorio.py` e PDF |
