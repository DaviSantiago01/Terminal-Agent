import uvicorn


def main() -> None:
    """Executa a API localmente via comando instalado."""

    uvicorn.run("apps.api.main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
