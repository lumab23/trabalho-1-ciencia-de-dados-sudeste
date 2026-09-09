# Relatório de qualidade — Luma / T326

Ano: 2020. Anos comuns: [2020].

## Registros por etapa

| Etapa | Registros |
|---|---:|
| pib_bruto | 5570 |
| populacao_bruta | 5570 |
| dtb_bruta | 5570 |
| pib_ano_selecionado | 5570 |
| populacao_ano_selecionado | 5570 |
| dtb_sudeste | 1668 |
| pib_sudeste | 1668 |
| populacao_sudeste | 1668 |
| apos_cruzar_pib | 1668 |
| apos_cruzar_populacao | 1668 |
| base_final | 1668 |

## Cobertura do Sudeste

| UF | DTB fornecida | Base final |
|---|---:|---:|
| ES | 78 | 78 |
| MG | 853 | 853 |
| RJ | 92 | 92 |
| SP | 645 | 645 |

## Perdas e recortes

Contagens abaixo podem se sobrepor (por exemplo, ausência simultânea de PIB e população). A exclusão final é contada uma única vez.

- pib_outros_anos: 0
- populacao_outros_anos: 0
- dtb_fora_sudeste: 3902
- pib_sem_dtb: 0
- pib_fora_sudeste_com_dtb: 3902
- populacao_sem_dtb: 0
- populacao_fora_sudeste_com_dtb: 3902
- dtb_sudeste_sem_pib: 0
- dtb_sudeste_sem_populacao: 0
- excluidos_calculo_invalido: 0

## Validações

Duplicatas município/ano: 0. Divergências de nomes: 0.
Releitura de CSV e Parquet aprovada; cálculo validado por comparação numérica. Valores econômicos em reais correntes, população em pessoas e PIB per capita em reais/pessoa.

Ausentes por coluna na base final:

- codigo_municipio: 0
- municipio: 0
- codigo_uf: 0
- uf: 0
- estado: 0
- regiao: 0
- ano: 0
- pib_total_reais: 0
- populacao: 0
- pib_per_capita_reais: 0
- impostos_reais: 0
- va_agropecuaria_reais: 0
- va_industria_reais: 0
- va_servicos_reais: 0
- va_administracao_publica_reais: 0

## Fontes e decisões

- pib: tabela5938_2020.csv.xz; 5570 linhas; csv; utf-8; compressão xz. SHA256: `992c5e3c2a237246fbf66832f5e962d54e4a891ee8bc4947a7ad7a9a2286c542`.
- populacao: tabela6579_2020.csv.xz; 5570 linhas; csv; utf-8; compressão xz. SHA256: `358a9388fe27679f0ce2829625e2c83a75ec0cbc6ced82a8ae5a1da8c8c6a05a`.
- dtb: RELATORIO_DTB_BRASIL_MUNICIPIO.csv; 5570 linhas; csv; utf-8; compressão None. SHA256: `92ee14276c0d69f1a8d16cde91b3aca9f4e506bbab98a28786935d032ba87857`.

- Ano dos arquivos originais identificado por Content-Disposition e título no Drive; não há coluna de ano nos CSVs fornecidos.
- Escolha automática do maior ano comum; config.ano permite selecionar outro ano comum, nunca anos distintos.
- DTB sem edição identificada: correspondência de códigos e nomes não comprova equivalência histórica de limites territoriais.
- Código municipal completo tem sete dígitos. Código local de cinco dígitos da DTB não é usado como chave.
- Região Sudeste derivada dos códigos de UF da DTB (31,32,33,35); regiões imediatas/intermediárias não são macrorregiões.
- Códigos ausentes e chaves duplicadas interrompem o pipeline após registrar as linhas; não há deduplicação arbitrária.
- PIB ausente, negativo ou não finito e população ausente, não positiva, não inteira ou não finita: exclusão auditada da base de consumo, sem imputação.
- VA e impostos: ausentes/não numéricos/não finitos ficam nulos; negativos são preservados e sinalizados para revisão.
- Nomes divergentes são relatados, sem cruzamento aproximado por nome; prevalece o nome da DTB.
- PIB per capita é PIB dividido pela estimativa populacional do mesmo ano; não representa renda individual nem distribuição de renda.
- VA dos serviços e VA da administração pública preservam os rótulos do arquivo; consultar os metadados SIDRA antes de agregar setores.
- Nenhuma quantidade de municípios foi imposta; cobertura final é reconciliada com a DTB fornecida.

Detalhes de esquema: inventario_fontes.json. Auditorias de chaves, cobertura, nomes e exclusões: CSVs nesta pasta. Os originais preservam os valores anteriores à conversão.
