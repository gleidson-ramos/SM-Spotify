# 🎵 SM-Spotify
Gerador de playlists que cria uma lista de 25 músicas a partir de um artista e uma faixa informados, usando as recomendações da Spotify Web API.

## ✨ Funcionalidades
- Busca uma faixa e artista na Spotify Web API
- Usa o gênero, artista e faixa como sementes (*seeds*) para gerar recomendações
- Gera uma playlist de 25 músicas relacionadas
- Oferece opção de salvar a playlist diretamente na conta do Spotify do usuário (`-s`)
- Cache local de token de acesso para evitar autenticações repetidas

## 🛠️ Tecnologias
- Python
- Spotipy: client Python para a Spotify Web API
- Spotify Web API (endpoints de busca, recomendações e playlists)

## 📋 Pré-requisitos
- Python 3.8+
- Uma conta de desenvolvedor no [Spotify for Developers](https://developer.spotify.com/) com um app registrado (para obter `Client ID`, `Client Secret` e `Redirect URI`)

## 🚀 Instalação
```bash
git clone https://github.com/gleidson-ramos/SM-Spotify.git
cd SM-Spotify
pip install -r requirements.txt
```

### Configuração das credenciais

Antes de usar, defina suas credenciais do Spotify usando variáveis de ambiente:

```bash
SPOTIFY_CLIENT_ID="seu_client_id"
SPOTIFY_CLIENT_SECRET="seu_client_secret"
SPOTIFY_REDIRECT_URI="sua_redirect_uri"
```

## ▶️ Uso
```bash
python spotify.py [-h] --artist ARTIST --track TRACK [-s]
```

**Argumentos:**

| Argumento | Descrição |
|---|---|
| `--artist` | Nome do artista |
| `--track` | Nome da faixa |
| `-s` (opcional) | Salva a playlist gerada na conta do Spotify |

### Exemplos

Gerar e exibir a playlist no terminal:
```bash
python spotify.py --artist "SZA" --track "Kill Bill"
```

Gerar e salvar a playlist na conta do Spotify:
```bash
python spotify.py --artist "SZA" --track "Kill Bill" -s
```

## 📄 Sobre o Projeto
Projeto desenvolvido como atividade para a disciplina de Sistemas Multimidias.