# Revisão técnica — 2026-09-19

## Comparação com o Omarchy oficial

Referências consultadas no GitHub: [contrato de temas](https://github.com/omacom/omarchy/blob/quattro/docs/theming.md),
[Flexoki Light](https://github.com/omacom/omarchy/blob/quattro/themes/flexoki-light/colors.toml)
e [Everforest](https://github.com/omacom/omarchy/blob/quattro/themes/everforest/colors.toml).

Mantivemos a estrutura oficial: paleta canônica, superfícies do shell, ícones,
wallpapers e overrides somente de cores. Não copiamos as paletas oficiais:
preservamos a identidade de cada tema e os papéis semânticos para código.
Assim como no fluxo oficial, arquivos existentes na raiz têm precedência sobre
templates. Por isso VS Code e Helix agora recebem os arquivos gerados na raiz,
além das cópias opcionais em integrations/. Não distribuímos Lua ou vscode.json
para contornar as restrições de temas instalados por Git.

## Correções

- Zed: o gerador não gravava sua saída e usava propriedades syntax.* inválidas.
  Agora usa o objeto syntax e estilos por token do [schema oficial](https://zed.dev/schema/themes/v0.2.0.json).
- Helix: os escopos usavam ANSI genérico em vez do contrato de código; o fundo
  estava vazio. Agora sintaxe e diagnósticos usam os papéis declarados.
- VS Code: constantes, pontuação, seleções, menus, sugestões, abas, painéis e
  cores ANSI explícitas; removido o escopo amplo meta.function-call, que podia
  colorir argumentos como funções. Referência: [cores da interface](https://code.visualstudio.com/api/references/theme-color).
- Nome do tema independente do nome da pasta do clone, usando theme.toml.
- Verificação --check sem escrita, validação de contraste e regressões dos
  arquivos gerados. A pontuação do Ankh claro passou a usar seu neutro legível.
- Mooni: Zed tem um único gerador; FZF preserva opções com aspas e não escreve
  variáveis universais; Delta evita fundos saturados; Yazi usa as seções atuais
  [documentadas](https://yazi-rs.github.io/docs/configuration/theme/).

## Limites e decisões

Os testes são estáticos e de geração; não comprovam a aparência de todos os apps
abertos nem a atualização em tempo real do VS Code. O hook existente permanece
inalterado, sem instalação ou execução nesta revisão. Ele é um workaround,
depende de detalhes internos do editor e não elimina todas as condições de cache.
Nenhum arquivo em /usr/share/omarchy foi modificado.

Neovim continua usando os templates do sistema, portanto não prometemos
equivalência exata de tokens com os outros editores. Transparência, parser,
extensões e opções locais podem mudar o resultado visual.

As referências Flexoki Light e Everforest acima foram usadas somente para
comparar estrutura e contrato do Omarchy; nenhuma captura ou paleta foi
reutilizada. As prévias atuais são capturas reais deste tema, conforme
[PREVIEWS.md](PREVIEWS.md). A tela de bloqueio da sessão continua distinta do
desbloqueio de disco do Plymouth.
