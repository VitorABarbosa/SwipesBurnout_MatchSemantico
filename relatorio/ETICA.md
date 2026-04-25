# CONNECT.AI — Considerações Éticas e LGPD

**Projeto:** CONNECT.AI — Sistema de Matchmaking Semântico (CP5 FIAP)
**Data:** 2026-04-22
**Versão:** 1.0

---

## 1. Dados Utilizados — Natureza Sintética

Todos os dados de perfis utilizados neste projeto são inteiramente sintéticos, gerados programaticamente pelo módulo `swipes_burnout/seed_data.py` com seed fixa (42). Nenhum dado real de pessoas físicas foi coletado, armazenado ou processado em qualquer etapa do desenvolvimento ou demonstração.

Os perfis sintéticos incluem nomes fictícios, idades geradas aleatoriamente dentro de faixas pré-definidas, cidades brasileiras reais (usadas apenas como categoria, sem dado de localização precisa), biografias textuais geradas a partir de templates e listas de interesses pré-definidas. O objetivo da síntese é demonstrar as capacidades técnicas do sistema sem nenhum risco à privacidade.

## 2. Consentimento e Base Legal (LGPD Art. 7º)

Em um sistema real em produção, a coleta de dados de perfis para fins de matchmaking se enquadraria no **consentimento explícito** como base legal (LGPD Art. 7º, I), exigindo: apresentação clara de quais dados serão coletados e com qual finalidade, termo de uso em linguagem acessível, opção de revogação do consentimento a qualquer momento, e registro de data/hora e versão do termo aceito.

Adicionalmente, o **legítimo interesse** (Art. 7º, IX) poderia fundamentar o processamento de dados comportamentais para melhoria do algoritmo de recomendação, desde que precedido de Relatório de Impacto à Proteção de Dados Pessoais (RIPD) e que os interesses do titular não prevaleçam sobre os do controlador.

## 3. Minimização de Dados (LGPD Art. 6º, III)

O modelo de dados `Perfil` coleta apenas os campos estritamente necessários para o funcionamento do algoritmo de matching: identificador único, nome (exibição), idade (filtro etário), cidade (filtro geográfico), gênero (filtro de preferência), gênero preferido (filtro hard), faixa etária preferida (filtro hard), objetivo (filtro hard + scoring), interesses (scoring), bio textual (embedding semântico) e o campo gerado `personalidade_ia` (mock da análise do Perfilador).

O sistema deliberadamente **não coleta**: foto real (dado biométrico — LGPD Art. 5º, II), número de telefone, e-mail, endereço preciso, renda, dados de saúde, orientação sexual explícita, dados de localização em tempo real ou qualquer dado de terceiro. Esta delimitação é uma decisão de design documentada e reflete o princípio de minimização da LGPD.

## 4. Justificativa para Uso de Mocks Textuais em Vez de Fotos Reais (ETH-02)

A decisão de usar mocks textuais determinísticos no Agente Perfilador, em vez de análise real de fotos via Gemini Vision, foi tomada por quatro razões convergentes:

**Privacidade:** Fotos de pessoas são dados biométricos (LGPD Art. 5º, II — dado sensível), exigindo consentimento específico e destacado para coleta e processamento. Utilizar fotos reais em um projeto acadêmico de demonstração introduziria riscos legais desproporcionais ao objetivo do trabalho.

**Custo zero:** Chamadas à API Gemini Vision têm custo por requisição. O mock textual elimina completamente este custo, tornando a demonstração gratuita e reproduzível sem dependência de créditos de API.

**Reprodutibilidade:** O mock determinístico garante que o mesmo perfil produz sempre o mesmo output do Perfilador, o que é essencial para testes automatizados e para a demonstração consistente do sistema.

**Escopo do CP5:** O objetivo do projeto é demonstrar a arquitetura multi-agente, o pipeline vetorial e o sistema de scoring — não avaliar a qualidade da análise multimodal. O mock cumpre o papel arquitetural do Agente Perfilador sem comprometer a integridade da demonstração técnica.

## 5. Riscos de Viés do Agente Perfilador (ETH-01)

O Agente Perfilador, em sua versão de produção com análise real de imagens, introduziria riscos de viés sistêmico que precisam ser gerenciados ativamente:

**Viés de aparência:** Modelos de análise de imagem são treinados em datasets que frequentemente super-representam determinados padrões de aparência. A inferência de personalidade a partir de foto pode perpetuar associações entre características físicas e traços psicológicos que não têm fundamento científico.

**Viés de câmara de eco:** Sistemas de matchmaking tendem a recomendar pessoas similares ao usuário em múltiplas dimensões. Sem diversidade intencional no pool e nos pesos do scoring, o sistema pode excluir sistematicamente grupos sub-representados.

**Viés de objetivo:** O filtro hard de objetivo (namoro/casual/amizade) elimina totalmente candidatos com objetivos diferentes. Em populações pequenas, isso pode resultar em ausência de matches para usuários com objetivos menos prevalentes.

Mitigações implementadas nesta versão: (1) mock textual eliminam viés de aparência por completo; (2) o pool sintético inclui 80 perfis de diversidade além dos 20 de alta compatibilidade; (3) os pesos do scoring são explícitos e auditáveis no código-fonte; (4) a justificativa do RAG usa apenas dados declarados pelo usuário, não inferências sobre aparência.

## 6. Aviso ao Usuário sobre Dados Sintéticos (ETH-03)

A interface Streamlit (`app/streamlit_app.py`) exibe um aviso explícito na página de Cadastro informando que todos os dados do sistema são sintéticos e que o aplicativo é uma demonstração técnica, não um serviço real de relacionamento. Este aviso garante transparência ao usuário sobre a natureza dos dados exibidos e previne confusão entre os perfis gerados e pessoas reais.

O mesmo aviso está presente na célula de conclusão do notebook `notebook/demo_cp5.ipynb`, reforçando que os resultados são demonstrativos e dependem da qualidade do embedding (real ou mock) utilizado na execução.

## 7. Direitos do Titular (LGPD Art. 18)

Em um sistema real em produção, os seguintes direitos do titular precisariam ser implementados: acesso aos próprios dados (exportação do perfil completo), retificação (edição de qualquer campo), exclusão (remoção do embedding do ChromaDB + dados de perfil), portabilidade (exportação em formato estruturado como JSON) e revogação de consentimento (desativação da conta + exclusão dentro de prazo legal).

O ChromaDB já suporta exclusão por ID (`collection.delete(ids=[id_perfil])`), o que provê a base técnica para implementar o direito ao esquecimento. A camada de aplicação precisaria complementar com exclusão de logs, caches e qualquer backup que contenha o perfil.

## 8. Recomendações para Produção

Antes de colocar um sistema deste tipo em produção com dados reais, as seguintes medidas seriam necessárias:

- Elaborar e publicar Política de Privacidade e Termos de Uso em linguagem clara
- Implementar fluxo de consentimento com registro de timestamp e versão do termo
- Designar um Encarregado de Proteção de Dados (DPO) conforme LGPD Art. 41
- Conduzir Relatório de Impacto à Proteção de Dados Pessoais (RIPD)
- Criptografar embeddings em repouso e em trânsito
- Implementar política de retenção de dados (ex: exclusão após 90 dias de inatividade)
- Realizar auditoria de viés semestral do algoritmo de scoring
- Monitorar drift de distribuição dos scores ao longo do tempo
