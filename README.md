# Projeto PLN

## Ambiente

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
```

Se precisar gerar uma lista completa do ambiente sem incluir o proprio projeto
editavel, use:

```powershell
python -m pip freeze --exclude-editable
```

## Executar

```powershell
python -m src.data_preparation
```
