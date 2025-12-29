PRÊMIO GOIÁS ABERTO PARA A INTELIGÊNCIA ARTIFICIAL – GO.IA

LIFE IA – REGULAÇÃO AUTÔNOMA

1. Proponente: 
Lívia Moreira Rocha
Desenvolvedora Junior – Ortodontista – Experiência em IA Generativa e Saúde Pública
2. IES / Empresa / Startup / ICTI:
A Nine Health é uma startup brasileira em desenvolvimento dedicada a soluções tecnológicas para a Saúde. A empresa tem como missão promover a transformação digital na saúde pública através de ferramentas baseadas em Inteligência Artificial, com ênfase em equidade, transparência e eficiência operacional.
Responsável pela implementação da LIFE IA
3. Título do Projeto:
LIFE IA – Regulação Autônoma: Sistema Inteligente para a Automatização de Leitos de Hospitais Estaduais do Sistema Único de Saúde – Goiás por via IA Aberta.

4 – Descreva a solução inovadora e o problema a ser resolvido
A Lei Orgânica da Saúde, 8080, de 19 de setembro de 1990, garante a regulamentação de ações e serviços de saúde em todo território nacional, estabelecendo que a saúde é um direito fundamental do ser humano (BRASIL, 1990). Apesar da garantia constitucional, a realidade operacional dos hospitais brasileiros, especialmente aqueles com abrangência de atendimentos de alta complexidade, revela desafios significativos relacionados à organização e regulação do acesso aos serviços de saúde.

Nos hospitais que atendem casos de maior complexidade, é comum observar, na ausência de uma devida organização e regulação eficiente, a ocorrência de superlotação. Este fenômeno gera sobrecarga nas equipes assistenciais e resulta na frequente dificuldade de acolher, no tempo clinicamente oportuno, pacientes que apresentam quadros de gravidade elevada (CARVALHO et al.,2024). Um dos principais fatores que contribuem para esta situação consiste no fato de que os serviços hospitalares com unidades de Urgência e Emergência apresentam uma procura crescente de pacientes portadores de condições de saúde de menor urgência. Esta demanda é originada, em grande medida, pela demanda reprimida de outros níveis de atenção, o que impõe um volume de atendimento que excede a capacidade instalada das unidades (SANTOS; LIMA; OLIVEIRA,2020).

Segundo Santos, Lima e Oliveira (2020), hospitais de média complexidade na Rede de Atenção às Urgências enfrentam desafios significativos relacionados à gestão de leitos e ao tempo de permanência dos pacientes, fatores que impactam diretamente a qualidade do atendimento e a eficiência do sistema como um todo. Além disso, a falta de interoperabilidade entre diferentes sistemas de saúde constitui um obstáculo significativo para a adoção em larga escala da Saúde Digital (ROTZSCH et al.,2024)

Diante deste cenário, propõe-se a integração e implantação do LIFE IA, que utiliza Inteligência Artificial aberta para automatizar e otimizar o gerenciamento de leitos hospitalares no Sistema Único de Saúde de Goiás. A proposta visa integrar diferentes especialidades médicas, desde a regulação de leitos de Unidade de Terapia Intensiva até cirurgias eletivas, criando uma ponte inteligente e eficiente entre as redes municipais de saúde e o Estado.

O sistema foi desenvolvido com uma arquitetura moderna de microserviços, garantindo escalabilidade, manutenibilidade e resiliência operacional. O frontend foi construído utilizando React Native versão, Expo SDK e TypeScript, garantindo a responsividade da aplicação. O diferencial inovador consiste em:

4.1 Triagem Automatizada
O LIFE IA utiliza o BioBert para leitura de pronturários.  O BioBert é uma Inteligência Artificial de código aberto (Open Source) especializada em dados médicos, será responsável por analisar prontuários e outros dados para determinar a prioridade clínica de cada paciente.

4.2 Logística Preditiva
O LIFE IA fornece informações em tempo real para familiares e equipes de saúde, incluindo previsão de vaga baseada em taxa de ocupação e histórico de internações, tempo médio de regulação desde a solicitação até a autorização, e tempo de transferência. 

4.3 Pilotagem em Shadow Mode
Na fase inicial de implantação, o LIFE IA operará em modo paralelo, denominado Shadow Mode. Neste modelo, a Inteligência Artificial fornece a recomendação, mas a decisão final permanece com o regulador humano. Este modelo garante segurança clínica ao preservar a autonomia hospitalar, permite o aprendizado contínuo através da coleta de dados de desempenho comparando decisões da Inteligência Artificial com decisões humanas, e possibilita o refinamento do modelo baseado em desfechos clínicos reais observados ao longo do tempo.

5 – Impacto social, econômico e/ou ambiental esperado
5.1 Contextualização
Em uma era onde é tecnicamente possível realizar cirurgias com uso de robótica avançada, à saúde pública brasileira ainda enfrenta desafios fundamentais relacionados à
distribuição equitativa de vagas para leitos em cirurgias eletivas e casos complexos que necessitam de Unidade de Terapia Intensiva. A regulação do Sistema Único de Saúde foi instituída em dois mil e oito através da Portaria número 1.559 (BRASIL, 2008), e a Rede Nacional de Dados em Saúde foi estabelecida em dois mil e vinte com o objetivo de promover a interoperabilidade e a integração de dados em Saúde no Brasil (FERRÉ et al.,
2024).

Dados do Portal da Transparência de Goiás, consultados em vinte um de dezembro de dois mil e vinte e cinco, revelam que existem atualmente mais de oitocentos pacientes em fila de espera para regulação em diferentes especialidades, incluindo Unidade de Terapia Intensiva, Psiquiatria, Neurologia e Cardiologia. Conforme estabelece a Constituição Federal Brasileira, a saúde é um direito de todos e um dever do Estado (BRASIL,1988). 

O Sistema Único de Saúde deve garantir acesso universal e gratuito a serviços de saúde, porém a realidade operacional evidencia uma lacuna significativa entre o direito constitucional e a prática cotidiana.

A utilização de aprendizado de máquina e inteligência artificial garante a indiscriminação e equidade no acesso aos serviços de saúde, priorizando exclusivamente a urgência clínica e eliminando vieses humanos que possam comprometer a justiça distributiva dos recursos de saúde. Esta abordagem tecnológica representa um avanço significativo na materialização dos princípios constitucionais de universalidade e equidade que fundamentam o Sistema Único de Saúde.

5.2 Impacto Social (Segurança e Humanização)
A LIFE IA prevê a redução de vieses na priorização de vagas, visto que a IA utiliza critérios exclusivamente clínicos e logísticos de forma indiscriminatória. Adicionalmente, estima-se a redução da mortalidade ao parear pacientes críticos com unidades de expertise adequada de forma ágil (GASPAR et al., 2025). 

5.3 Impacto Econômico: Otimização
A LIFE IA reduz o custo por regulação e o tempo de trabalho burocrático, pois é verificado que equipes multiprofissionais apontam que a lentidão na realização de exames regulados pelo Sistema de Regulação (SISREG) e a demora no agendamento de pareceres de outras especialidades (cruciais para a discussão clínica e definição de condutas) são os fatores que mais contribuem para o prolongamento do tempo de internação hospitalar. Esta percepção corrobora a literatura, que também associa a longa permanência de pacientes à necessidade de exames complementares e especializados durante a internação (CUNHA et al., 2023). 

5.4 Impacto Ambiental
A LIFE IA propõe a redução de deslocamentos desnecessários é alcançada através do pareamento inteligente que considera a proximidade geográfica como um dos critérios, com peso de quinze por cento. Esta otimização resulta em redução de emissões de dióxido de carbono provenientes de ambulâncias em trajetos desnecessários, diminuição do consumo de combustível do sistema de transporte de saúde, e redução do tempo de deslocamento de equipes médicas, permitindo que estes profissionais dediquem mais tempo ao atendimento direto aos pacientes.

A digitalização de processos contribui para a sustentabilidade ambiental através da substituição de formulários físicos por digitais, reduzindo significativamente o consumo de papel e a geração de resíduos administrativos. Estima-se que cada solicitação de regulação gere, no processo manual tradicional, aproximadamente dez páginas de documentos impressos. Com a digitalização completa do processo, esta geração de resíduos é completamente eliminada.

6 – Nível de maturidade da solução e potencial de sustentabilidade
6.1 Nível de Maturidade Tecnológica
A solução enquadra-se no Nível de Prontidão Tecnológica seis a sete, correspondente a Produto Mínimo Viável. Esta classificação é justificada por diversos fatores que demonstram o estágio avançado de desenvolvimento do projeto. A tecnologia foi validada através de testes extensivos em ambiente de desenvolvimento, onde a arquitetura de microserviços e o modelo de Inteligência Artificial BioBert foram submetidos a cenários realistas de uso.

A prototipagem avançada está concluída, com interface completa para Hospital, Regulador e módulo de Transporte implementados e funcionais. As interfaces foram desenvolvidas seguindo princípios de usabilidade e acessibilidade, garantindo que profissionais de saúde possam utilizar o sistema com mínima curva de aprendizado. Entretanto, a pilotagem em ambiente de produção com dados reais em tempo real, denominada Shadow Mode, ainda está pendente, sendo esta a principal etapa a ser executada com os recursos da premiação.

6.2 Sustentabilidade Pós-Premiação
A sustentabilidade do sistema da LIFE IA é garantida por múltiplos pilares que asseguram sua viabilidade operacional e financeira no longo prazo. 
O primeiro pilar consiste na arquitetura cem por cento Open Source, onde toda a stack tecnológica utiliza ferramentas de código aberto, eliminando completamente custos de licença e dependência de fornecedores proprietários. 
O custo total de licenças de software é, portanto, zero reais, representando uma economia significativa em comparação com soluções proprietárias.

7 – Capacidade da Equipe
Lívia Moreira Rocha (Proponente): Desenvolvedora Júnior, Odontóloga, Expertise clínica em Saúde Pública e competências em desenvolvimento de IA aplicada à saúde.

Sebastião Relson Reis da Luz: Bacharel em Ciências da Computação. Desenvolvedor Sênior, Expertise em Retrieval Augmented Generation (RAG) e arquitetura de sistemas de Inteligência Artificial.

8 – Conformidade Ética e Lei Geral de Proteção de Dados
8.1 Adequação à Lei Geral de Proteção de dados
O tratamento de dados de saúde, classificados como dados sensíveis, exige um nível elevado de diligência e conformidade regulatória. Em estrito cumprimento à Lei Federal nº 13.709/2018 (LGPD), o sistema LIFE IA implementa uma abordagem de Privacy by Design, integrando a proteção de dados em todas as fases de seu ciclo de vida. As seguintes salvaguardas foram implementadas:
Minimização e Finalidade do Tratamento: O tratamento de dados é restrito ao estritamente necessário para a otimização da fila de regulação de leitos do SUS em Goiás. Conforme preconiza a LGPD, não haverá desvio de finalidade ou uso secundário das informações coletadas.
Técnicas de Anonimização e Pseudonimização: A base de dados para treinamento e operação será submetida a rigorosos processos de desidentificação. Os algoritmos não terão acesso a informações de identificação direta (como nome ou CPF), garantindo a privacidade absoluta do cidadão.
Segurança da Informação e Controle de Acesso: Os dados serão processados em ambiente computacional seguro sob a governança da Secretaria de Estado da Saúde de Goiás (SES-GO). Serão aplicadas medidas de criptografia, controle de acesso baseado em função (RBAC - Controle de Acesso Baseado em Função) e logs de auditoria constantes.
Base Legal e Transparência: O tratamento encontra amparo nas bases legais de tutela da saúde (Art. 7º, VIII) e execução de políticas públicas (Art. 7º, III). A formalização do acesso será realizada via Acordo de Cooperação Técnica e Termo de Confidencialidade com a SES-GO.
Esta estrutura de proteção não apenas cumpre os requisitos legais, mas alinha-se aos pilares contemporâneos de Governança em Saúde Digital, assegurando que a inovação tecnológica caminhe em conjunto com a integridade institucional e a responsabilidade ética no tratamento de ativos de dados públicos (MOURA JUNIOR et al., 2025).


8.2.Princípios Éticos: Transparência e Auditabilidade
O código-fonte do sistema está publicado em repositório público GitHub, sob licença permissiva MIT. Esta abertura permite que pesquisadores, auditores e a sociedade civil possam revisar o código-fonte e identificar possíveis vieses algorítmicos, propor melhorias e correções através de mecanismos de contribuição colaborativa, e replicar a solução em outros contextos geográficos ou institucionais, ampliando o impacto social da inovação.
O pareamento clínico utiliza critérios transparentes e objetivos, mitigando vieses por fatores socioeconômicos ou regionais. A decisão é baseada exclusivamente em urgência clínica, determinada pela prioridade atribuída, tempo em fila e gravidade do código da Classificação Internacional de Doenças, especialidade necessária, estabelecida através de mapeamento técnico entre procedimentos e recursos hospitalares, e disponibilidade de leitos, baseada em dados em tempo real fornecidos pelos hospitais da rede.
A explicabilidade, conceito fundamental em Inteligência Artificial do LIFE IAl, é garantida através de múltiplos mecanismos. Toda decisão da Inteligência Artificial é acompanhada de justificativa clínica detalhada, apresentada em linguagem natural que permite aos profissionais de saúde compreenderem o raciocínio por trás da recomendação. O score de gravidade é apresentado como valor numérico transparente em escala de zero a cem pontos, permitindo comparações objetivas entre diferentes solicitações. O motivo da escolha do hospital é explicado detalhadamente, descrevendo como os critérios de urgência, especialidade e disponibilidade foram ponderados na decisão final.
O LIFE IA será apresentado ao Comitê de Ética em Saúde para supervisionar a operação do sistema.
9 – Utilização de IA 100% aberta e Metodologia
9.1 Software, Modelo e Arquitetura Aberta
O LIFE IA garante a reprodutibilidade total por meio de uma arquitetura de microserviços construída integralmente com tecnologias de código aberto. O backend é desenvolvido em Python utilizando o framework FastAPI, que atua como uma API unificada para orquestrar os serviços de inteligência e integração de dados. O frontend  é construído em React Native com Expo SDK, proporcionando interfaces intuitivas e responsivas para hospitais e reguladores.
A inteligência clínica da plataforma opera através de um pipeline multimodal híbrido:
BioBERT v1.1 (Peso 60%): Utilizado para o reconhecimento de entidades médicas e análise técnica de textos em prontuários, com licença Apache 2.0.
Llama 3 (Peso 10%): Responsável pela interpretação contextual e geração de resumos clínicos, executado localmente via Ollama.
OCR Tesseract (Peso 30%): Engine de extração de texto para documentos digitalizados, garantindo a ingestão de dados de fontes físicas.
O armazenamento utiliza PostgreSQL para dados estruturados e auditoria, enquanto a orquestração de todo o ecossistema é gerenciada por Docker Desktop e Docker Compose, garantindo um ambiente estável e replicável. Todo o código-fonte será disponibilizado no GitHub sob licença MIT, cumprindo o critério de transparência total exigido pelo edital.
9.2 Metodologia Empregada: O Pipeline de Regulação
A metodologia do LIFE IA baseia-se em um ciclo de processamento inteligente dividido em cinco camadas funcionais:
Ingestão e OCR: O hospital solicitante realiza o upload de documentos que são processados pelo serviço de OCR para converter imagens em texto processável.
Análise Clínica (NLP): O serviço biobert_service.py extrai CIDs, sintomas e gravidade. Simultaneamente, o Llama 3 realiza a interpretação contextual para gerar uma justificativa clínica explicável (xai_explicabilidade.py).
Matchmaking Logístico: Através do matchmaker_logistico.py, o sistema cruza as necessidades do paciente com o mapa de hospitais de Goiás, calculando o melhor desfecho baseado em distância (via APIs de mapas) e disponibilidade real de leitos.
Validação em Shadow Mode: As sugestões da IA são apresentadas ao regulador humano para autorização ou ajuste, permitindo que o modelo aprenda com as decisões dos especialistas antes de uma automação plena.
Monitoramento de Desfecho: O sistema acompanha a transferência e o tempo de regulação, retroalimentando o banco de dados para o retreinamento contínuo dos modelos preditivos.
9.3 Ciclo de Aprendizado Contínuo e Auditoria
Para assegurar a confiabilidade, o LIFE IA implementa métricas de desempenho rigorosas, como a Acurácia de Pareamento (objetivo > 85%) e o Tempo de Resposta (análise completa em menos de 10 segundos). A metodologia prevê retreinamentos periódicos utilizando dados anonimizados do Portal da Transparência de Goiás, adaptando a IA à sazonalidade de doenças e mudanças na rede hospitalar estadual.

10 – Comprovação de Participação de ICTI em Goiás
Aberta a propostas de parcerias.

11 – Cronograma de Execução Pós-Premiação (12 Meses)
O cronograma de implantação do  LIFE IA, está estruturado em seis fases sequenciais e parcialmente sobrepostas, distribuídas ao longo de doze meses, com entregáveis claros e mensuráveis. A organização temporal foi definida de modo a mitigar riscos técnicos, garantir conformidade regulatória e permitir validação progressiva da solução em ambiente real.
Fase 1 – Infraestrutura e Preparação Técnica (Meses 1–2)
Nesta fase será realizado o provisionamento completo do ambiente computacional de produção, incluindo a configuração da arquitetura de microserviços em nuvem ou infraestrutura pública estadual. Serão implementados os serviços de banco de dados, monitoramento e segurança básica da informação.
Principais atividades: Setup de ambiente Docker e Kubernetes; Configuração de banco de dados PostgreSQL com replicação e backup; Implementação de monitoramento (Prometheus e Grafana); Documentação técnica da arquitetura.


Entregáveis: Ambiente de produção operacional; Documentação de arquitetura e fluxos de dados.


Fase 2 – Integração Institucional e Conformidade LGPD (Meses 2–3)
Esta fase compreende a formalização de acordos institucionais e a preparação dos dados necessários para treinamento e validação da Inteligência Artificial.
Principais atividades: Formalização de Acordo de Cooperação Técnica com a SES-GO; Adequação jurídica e técnica à Lei Geral de Proteção de Dados; Integração com bases públicas e sistemas de regulação existentes; Engenharia de features a partir dos dados históricos.


Entregáveis:Termos de confidencialidade e responsabilidade assinados; Pipeline ETL funcional; Dataset de treinamento anonimizado e validado.


Fase 3 – Modelagem, Treinamento e Validação (Meses 3–8)
Fase central do projeto, dedicada ao treinamento e validação dos modelos preditivos e de linguagem utilizados na regulação automatizada.
Principais atividades: Fine-tuning dos modelos BioBERT e Llama 3 com dados de regulação; Treinamento dos módulos de score de urgência e pareamento logístico; Validação offline com dados históricos; Auditoria técnica externa independente.


Entregáveis: Modelos treinados com acurácia ≥ 85%; Relatório técnico de validação e análise de vieses; Código-fonte publicado em repositório público (licença MIT).


Fase 4 – APIs e Integração Operacional (Meses 6–7)
Nesta fase ocorre a consolidação da comunicação entre backend, frontend e serviços externos.
Principais atividades: Implantação da API RESTful em FastAPI; Integração com sistemas hospitalares e regulatórios; Integração com APIs de logística (OpenStreetMap ou similar); Testes de carga e performance.


Entregáveis: API em produção com SLA ≥ 99,5%; Documentação OpenAPI/Swagger; Relatórios de testes de performance.


Fase 5 – Pilotagem em Shadow Mode e Capacitação (Meses 8–10)
O sistema será operado em paralelo ao processo manual, garantindo segurança clínica e aprendizado supervisionado.
Principais atividades: Operação do sistema em Shadow Mode; Coleta de métricas de concordância IA × reguladores;  Refinamento dos modelos; Treinamento de aproximadamente 50 reguladores.


Entregáveis: Relatório de pilotagem; Modelo refinado (versão estável); Equipes treinadas e certificadas.


Fase 6 – Automação Parcial e Entrega Final (Meses 11–12)
Etapa de consolidação da solução e disseminação dos resultados.
Principais atividades: Ativação da sugestão automática da IA; Implantação do módulo de comunicação com familiares; Finalização da documentação técnica e científica; Apresentação institucional dos resultados.


Entregáveis: Sistema em produção com automação parcial; Módulo de comunicação funcional; Artigo científico submetido;Relatório final para órgãos parceiros.

12 – Plano de Aplicação dos Recursos (R$ 500.000,00)
O plano de aplicação dos recursos pós-premiação para o projeto LIFE IA foi estruturado com foco na transformação do atual Produto Mínimo Viável (MVP) em um ecossistema de missão crítica capaz de operar em toda a rede hospitalar de Goiás. Considerando a alta criticidade do setor de saúde, a alocação de R$ 500.000,00 prioriza a robustez técnica, a segurança cibernética e a alta disponibilidade da infraestrutura.


Categoria FAPEG
Valor (R$)
Justificativa Técnica Baseada na Solução
Desenvolvimento e Aprimoramento
R$ 200.000
Refatoração da arquitetura atual para microsserviços distribuídos e implementação produtiva dos modelos Llama 3.2 e BioBERT.
Infraestrutura Tecnológica
R$ 160.000
Provisionamento de Cluster Kubernetes (K8s) em nuvem nacional com redundância e GPUs para inferência 24/7.
Segurança e Conformidade
R$ 60.000
Auditoria especializada de segurança, PenTests e implementação de camadas de anonimização de dados sensíveis.
Engenharia e Integração de Dados
R$ 50.000
Desenvolvimento e manutenção de scrapers resilientes para o Portal de Saúde GO e conectores oficiais do CNES.
Capacitação e Implantação
R$ 30.000
Treinamento técnico-clínico para reguladores médicos e suporte à transição do fluxo manual para o autônomo.
TOTAL
R$ 500.000




12.2 – Detalhamento da Execução e Justificativa dos Gastos
A aplicação do recurso é fundamentada na necessidade de elevar o nível tecnológico da solução para padrões governamentais. No campo do Desenvolvimento Especializado, o montante de R$ 200.000,00 destina-se à contratação de consultoria técnica para desacoplar o motor de inteligência artificial da API principal. Essa arquitetura garante que o treinamento e a recalibragem dos modelos não impactem a estabilidade do site de regulação. Inclui-se, ainda, o desenvolvimento de um painel de UX/UI profissional que substituirá as interfaces prototipais, facilitando a tomada de decisão clínica.
Para a Infraestrutura de Missão Crítica (R$ 160.000,00), o projeto opta pelo uso de infraestrutura elástica (Kubernetes) na nuvem brasileira Magalu Cloud. Esta escolha estratégica visa cumprir os requisitos de soberania de dados e garantir escalabilidade automática durante picos de demanda hospitalar. A base de dados PostgreSQL será configurada com redundância geográfica e backups periódicos (Point-in-Time Recovery), assegurando que não haja perda de registros vitais.
A Segurança da Informação e LGPD (R$ 60.000,00) é tratada como pilar central. O orçamento financiará auditorias externas e a contratação de testes de invasão (Pentests) para blindar a API de regulação contra acessos indevidos. Toda a lógica de anonimização será validada juridicamente para garantir a conformidade absoluta com a Lei nº 13.709/2018.
12.3 – Metodologia de Gestão do Recurso
A equipe proponente atuará como o Núcleo Estratégico e Técnico, gerenciando a execução dos serviços de terceiros sem violar vedações relativas a pagamentos de pessoal interno. A Livia Moreira Rocha liderará a visão de produto e validação de acurácia clínica, enquanto o Sebastião Relson atuará como gestor de contratos e revisor técnico (Code Review), garantindo que todos os entregáveis mantenham a fidelidade à IA 100% Aberta sob licença MIT e os padrões de reprodutibilidade total exigidos por este edital.

13 – Apresente eventual portfólio ou demonstrativo da solução (link vídeo, link para MVP,
link apresentações).
Link para o Repositório Público. https://github.com/LiviaMor/regulacao-ms
Link Público para Demonstração  -  https://youtu.be/TlBRzvru-eY?si=TqqLUTBzVrucetyN































