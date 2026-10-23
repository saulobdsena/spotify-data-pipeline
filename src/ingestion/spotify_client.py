
import os
import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

TOKEN_URL = "https://accounts.spotify.com/api/token"
API_URL = "https://api.spotify.com/v1"


def obter_token():
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError(
            "Confira SPOTIFY_CLIENT_ID e SPOTIFY_CLIENT_SECRET no .env"
        )

    resposta = requests.post(
        TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=30,
    )

    resposta.raise_for_status()
    return resposta.json()["access_token"]


def obter_artista(artist_id, token):
    resposta = requests.get(
        f"{API_URL}/artists/{artist_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )

    resposta.raise_for_status()
    return resposta.json()


def salvar_json(dados, nome_arquivo):
    pasta = PROJECT_ROOT / "data" / "raw"
    pasta.mkdir(parents=True, exist_ok=True)

    caminho = pasta / nome_arquivo

    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)

    print(f"Dados salvos em: {caminho}")


def main():
    # ID de exemplo do artista Radiohead
    artist_id = "4Z8W4fKeB5YxbusRsdQVPb"

    try:
        token = obter_token()
        dados = obter_artista(artist_id, token)

        registro = {
            "extraido_em": datetime.now(timezone.utc).isoformat(),
            "tipo_entidade": "artista",
            "dados": dados,
        }

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        salvar_json(
            registro,
            f"artista_{artist_id}_{timestamp}.json",
        )

        print(f"Artista: {dados.get('name', 'Nome indisponível')}")
        print(f"Seguidores: {dados.get('followers', {}).get('total')}")
        print(f"Popularidade: {dados.get('popularity')}")

    except requests.HTTPError as erro:
        print(f"Erro HTTP: {erro}")
        if erro.response is not None:
            print(erro.response.text[:1000])

    except requests.RequestException as erro:
        print(f"Erro de conexão: {erro}")

    except (ValueError, KeyError) as erro:
        print(f"Erro de configuração ou resposta: {erro}")


if __name__ == "__main__":
    main()
