# Arquivos originais e recuperação manual

O download usa exclusivamente os três IDs fornecidos pelo professor.

| Fonte | Link | Copiar o conteúdo original para |
|---|---|---|
| PIB | https://drive.google.com/file/d/1GQVxYHY9ouZvh_Jkbzt3sjnWHslxGqnX/view | `data/raw/pib_original` |
| População | https://drive.google.com/file/d/1OLg85S7vAr4MQomc_wcaQhRo6SLciSu0/view | `data/raw/populacao_original` |
| DTB | https://drive.google.com/file/d/1G3Ll5LsIhsvpodjnKg6JE0KXbc_D-BSP/view | `data/raw/dtb_original` |

1. Baixe o mesmo arquivo pelo navegador. Se o Drive negar acesso, solicite ao professor
   permissão ou uma cópia desse arquivo; não use outra base sem documentar a mudança.
2. Coloque o arquivo original, **sem descompactar nem editar**, no caminho da tabela.
   Você pode manter seu nome original e alterar somente `fontes.<fonte>.arquivo` em
   `config.json` para o caminho relativo correspondente.
3. Ative o ambiente, defina `PYTHONPATH=src` e execute `python -m sudeste.pipeline`.
   Não é preciso repetir o download nem ter conexão com a internet nessa etapa.

`downloads.jsonl` mantém o histórico de tentativas, erros, URLs, metadados e hashes.
O download não sobrescreve originais já existentes. Arquivos `.part` indicam tentativas
incompletas e não são lidos pelo pipeline. Os nomes locais sem extensão não alteram
o conteúdo: a compressão é reconhecida pela assinatura XZ.

Se o hash diferir, **não remova a verificação só para prosseguir**. Inspecione o arquivo,
confirme fonte, esquema, unidades e referência temporal, registre a justificativa e
atualize o hash e os metadados em `config.json`. Sem evidência de ano, o pipeline não
pode atribuir uma data ao arquivo. As datas econômicas verificadas nos arquivos atuais
são 2020; a edição da DTB continua não informada.
