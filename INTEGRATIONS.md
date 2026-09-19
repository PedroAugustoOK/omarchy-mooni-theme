# Integrações Mooni

O Omarchy já gera e reaplica, a cada troca de tema, configurações para
Alacritty, Foot, Ghostty, Kitty, btop, Chromium/Chrome/Brave/Edge, Helix,
Neovim, VS Code, VSCodium, Cursor, Obsidian, teclado e superfícies do próprio
Omarchy. O Mooni usa essa rota oficial por meio de `colors.toml` e não duplica
essas configurações.

Os complementos em `integrations/` atendem softwares que não são configurados
automaticamente. Eles são deliberadamente opcionais: copie ou mescle apenas o
arquivo da ferramenta que usa, preservando suas escolhas locais.

Esses arquivos são gerados a partir de `colors.toml`; não os edite
diretamente. Após mudar a paleta, execute:

~~~bash
python3 scripts/generate-integrations.py
~~~

Para verificar se o repositório está sincronizado sem alterar arquivos, use
`python3 scripts/generate-integrations.py --check`.

| Ferramenta | Arquivo | Como aplicar |
| --- | --- | --- |
| bat | `bat.conf` | Mescle em `~/.config/bat/config`. |
| Cava | `cava-theme` | Copie para o diretório de temas do Cava e selecione-o em `config`. |
| git-delta | `delta.gitconfig` | Adicione um `include.path` ao seu `~/.gitconfig`. |
| Fastfetch | `fastfetch.jsonc` | Teste com `fastfetch --config /caminho/fastfetch.jsonc`; depois copie ou mescle em `~/.config/fastfetch/config.jsonc`. |
| fzf no Fish | `fzf.fish` | Faça `source` para testar e acrescente-o ao `config.fish` se gostar do resultado. |
| Lazygit | `lazygit.yml` | Mescle somente `gui.theme` em `~/.config/lazygit/config.yml`. |
| Steam | `steam.css` | Aplique pelo seu carregador de CSS de Steam; o Mooni não instala modificadores de cliente. |
| Superfile | `superfile.toml` | Mescle-o no arquivo de tema do Superfile. |
| Vencord/Discord | `vencord.theme.css` | Copie para a pasta de temas do Vencord e habilite-o em Settings → Themes. |
| Yazi | `yazi-theme.toml` | Mescle em `~/.config/yazi/theme.toml`; não altera atalhos nem layout. |
| Zed | `zed.json` | Copie para `~/.config/zed/themes/mooni.json` e selecione “Omarchy Mooni”. |

Nenhum dos arquivos em `integrations/` é instalado automaticamente por
`omarchy theme install`; isso evita que um tema altere configurações de apps
fora do seu escopo.
