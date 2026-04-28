# Projeto PLN


# Etapa para criação do ambiente virtual e ativar ele
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

# Instale as dependências
```powershell

python -m pip install -r requirements.txt
python -m pip install -e .

```
# Comando para executar a extração dos dados
```powershell

python -m src.data_preparation

```


