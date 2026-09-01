import os
import asyncio
import glob
import shutil
import pandas as pd

os.environ["PYSUS_CACHEPATH"] = os.path.abspath("data/raw")

from pysus.api.client import PySUS


# =============================================================================
# Extração — Leitos (CNES-LT)
# =============================================================================

async def get_leitos(state, year, month):
    async with PySUS() as pysus:
        files = await pysus.query(
            dataset="cnes",
            group="LT",
            state=state,
            year=year,
            month=month,
        )

        if not files:
            print(f"Nenhum arquivo encontrado para {state}/{year}/{month}.")
            return None

        local_paths = []
        for f in files:
            local = await pysus.download(f)
            print("Baixado em:", local.path)
            local_paths.append(local.path)

        df = pysus.read_parquet(local_paths, mode="union").df()
        return df


def get_dados_leitos(state, year, month):
    try:
        df = asyncio.run(get_leitos(state, year, month))
        return df
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None


# =============================================================================
# Extração — SIH (internações, grupo RD)
# =============================================================================

"""async def get_sih(state, year, month):
    async with PySUS() as pysus:
        files = await pysus.query(
            dataset="sih",
            group="RD",
            state=state,
            year=year,
            month=month,
        )

        if not files:
            print(f"Nenhum arquivo encontrado para {state}/{year}/{month}.")
            return None

        local_paths = []
        for f in files:
            local = await pysus.download(f)
            print("Baixado em:", local.path)
            local_paths.append(local.path)

        df = pysus.read_parquet(local_paths, mode="union").df()
        return df


def get_dados_sih(state, year, month):
    try:
        df = asyncio.run(get_sih(state, year, month))
        return df
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None"""




async def get_sih(state, year, month):
    async with PySUS() as pysus:
        files = await pysus.query(
            dataset="sih",
            group="RD",
            state=state,
            year=year,
            month=month,
        )

        if not files:
            print(f"Nenhum arquivo encontrado para {state}/{year}/{month}.")
            return None

        local_paths = []
        for f in files:
            local = await pysus.download(f)
            print("Baixado em:", local.path)
            local_paths.append(local.path)

        # Leitura dos arquivos baixados
        df = pysus.read_parquet(local_paths, mode="union").df()

        # Identifica a coluna de data (no SIH cru costuma ser DT_INTER, pós-tratamento data_internacao)
        col_data = next((col for col in ["data_internacao", "DT_INTER"] if col in df.columns), None)

        if col_data:
            # Converte para datetime (trata tanto formato YYYYMMDD quanto ISO)
            df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
            
            # Filtra apenas o ano e mês desejados
            df = df[
                (df[col_data].dt.year == int(year)) & 
                (df[col_data].dt.month == int(month))
            ]

        return df


def get_dados_sih(state, year, month):
    try:
        df = asyncio.run(get_sih(state, year, month))
        return df
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None



# =============================================================================
# Extração — Estabelecimentos (CNES-ST)
# =============================================================================


def _mover_st_para_pasta_propria(pasta_raiz: str = "data/raw/downloads/ducklake"):
    """
    O PySUS organiza o cache por 'dataset', não por 'group'. Como leitos (LT)
    e estabelecimentos (ST) compartilham dataset="cnes", os dois caem juntos
    em cnes/. Esta função move só os arquivos ST*.parquet para st/, deixando
    LT*.parquet intocado em cnes/.
    """
    pasta_origem = os.path.join(pasta_raiz, "cnes")
    pasta_destino = os.path.join(pasta_raiz, "st")
    os.makedirs(pasta_destino, exist_ok=True)

    for origem in glob.glob(os.path.join(pasta_origem, "ST*.parquet")):
        destino = os.path.join(pasta_destino, os.path.basename(origem))
        shutil.move(origem, destino)
        print(f"Movido: {origem} -> {destino}")


async def get_estabelecimentos(state, year, month):
    async with PySUS() as pysus:
        files = await pysus.query(
            dataset="cnes",
            group="ST",
            state=state,
            year=year,
            month=month,
        )

        if not files:
            print(f"Nenhum arquivo encontrado para {state}/{year}/{month}.")
            return None

        local_paths = []
        for f in files:
            local = await pysus.download(f)
            print("Baixado em:", local.path)
            local_paths.append(local.path)

        df = pysus.read_parquet(local_paths, mode="union").df()
        return df


def get_dados_estabelecimentos(state, year, month):
    try:
        df = asyncio.run(get_estabelecimentos(state, year, month))
        _mover_st_para_pasta_propria()
        return df
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    #df_lt_raw = get_dados_leitos(state="SP", year=2026, month=5)
    df_sih_raw = get_dados_sih(state="SP", year=2026, month=6)
    #df_st_raw = get_dados_estabelecimentos(state="SP", year=2026, month=5)