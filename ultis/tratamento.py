import pandas as pd
import os
import glob


# =============================================================================
# Tabelas de domínio CNES — fixas, não dependem de ano/mês/estado
# =============================================================================

MASK_TP_LEITO = {
    "1": "Cirúrgico",
    "2": "Clínico",
    "3": "Complementar",
    "4": "Obstétrico",
    "5": "Pediátrico",
    "6": "Outras Especialidades",
    "7": "Hospital Dia",
}

# Chave = (TP_LEITO, CODLEITO), pois o mesmo CODLEITO pode se repetir
# em mais de um TP_LEITO com descrições diferentes.
MASK_SUBTIPO_LEITO = {
    ("1", "01"): "Buco Maxilo Facial",
    ("1", "02"): "Cardiologia",
    ("1", "03"): "Cirurgia Geral",
    ("1", "04"): "Endocrinologia",
    ("1", "05"): "Gastroenterologia",
    ("1", "06"): "Ginecologia",
    ("1", "08"): "Nefrologia/Urologia",
    ("1", "09"): "Neurocirurgia",
    ("1", "11"): "Oftalmologia",
    ("1", "12"): "Oncologia",
    ("1", "13"): "Ortopedia/Traumatologia",
    ("1", "14"): "Otorrinolaringologia",
    ("1", "15"): "Plástica",
    ("1", "16"): "Torácica",
    ("1", "67"): "Transplante",
    ("1", "90"): "Queimado Adulto",
    ("1", "91"): "Queimado Pediátrico",
    ("2", "01"): "Buco Maxilo Facial",
    ("2", "02"): "Cardiologia",
    ("2", "03"): "Cirurgia Geral",
    ("2", "31"): "AIDS",
    ("2", "32"): "Cardiologia",
    ("2", "33"): "Clínica Geral",
    ("2", "35"): "Dermatologia",
    ("2", "36"): "Geriatria",
    ("2", "37"): "Hansenologia",
    ("2", "38"): "Hematologia",
    ("2", "39"): "Leito/Dia",
    ("2", "40"): "Nefrourologia",
    ("2", "41"): "Neonatologia",
    ("2", "42"): "Neurologia",
    ("2", "44"): "Oncologia",
    ("2", "46"): "Pneumologia",
    ("2", "62"): "UTI Infantil",
    ("2", "87"): "Saúde Mental",
    ("2", "88"): "Queimado Adulto",
    ("2", "89"): "Queimado Pediátrico",
    ("3", "32"): "Cardiologia",
    ("3", "33"): "Clínica Geral",
    ("3", "51"): "UTI II Adulto - SRAG COVID-19",
    ("3", "52"): "UTI II Pediátrica - SRAG COVID-19",
    ("3", "61"): "UTI Adulto",
    ("3", "62"): "UTI Infantil",
    ("3", "63"): "UTI Neonatal",
    ("3", "64"): "Unidade Intermediária",
    ("3", "65"): "Unidade Intermediária Neonatal",
    ("3", "66"): "Unidade de Isolamento",
    ("3", "74"): "UTI Adulto - Tipo I",
    ("3", "75"): "UTI Adulto - Tipo II",
    ("3", "76"): "UTI Adulto - Tipo III",
    ("3", "77"): "UTI Pediátrica - Tipo I",
    ("3", "78"): "UTI Pediátrica - Tipo II",
    ("3", "79"): "UTI Pediátrica - Tipo III",
    ("3", "80"): "UTI Neonatal - Tipo I",
    ("3", "81"): "UTI Neonatal - Tipo II",
    ("3", "82"): "UTI Neonatal - Tipo III",
    ("3", "83"): "UTI de Queimados",
    ("3", "85"): "UTI Coronariana Tipo II - UCO Tipo II",
    ("3", "86"): "UTI Coronariana Tipo III - UCO Tipo III",
    ("3", "92"): "Unidade de Cuidados Intermediários Neonatal Convencional",
    ("3", "93"): "Unidade de Cuidados Intermediários Neonatal Canguru",
    ("3", "94"): "Unidade de Cuidados Intermediários Pediátrico",
    ("3", "95"): "Unidade de Cuidados Intermediários Adulto",
    ("3", "96"): "Suporte Ventilatório Pulmonar - COVID-19",
    ("4", "10"): "Obstetrícia Cirúrgica",
    ("4", "43"): "Obstetrícia Clínica",
    ("5", "45"): "Pediatria Clínica",
    ("5", "68"): "Pediatria Cirúrgica",
    ("6", "34"): "Crônicos",
    ("6", "47"): "Psiquiatria",
    ("6", "48"): "Reabilitação",
    ("6", "49"): "Pneumologia Sanitária",
    ("6", "84"): "Acolhimento Noturno",
    ("7", "07"): "Cirúrgico/Diagnóstico/Terapêutico",
    ("7", "69"): "AIDS",
    ("7", "70"): "Fibrose Cística",
    ("7", "71"): "Intercorrência Pós-Transplante",
    ("7", "72"): "Geriatria",
    ("7", "73"): "Saúde Mental",
}

COLUNAS_IMPORTANTES = [
    "CNES",
    "CODUFMUN",
    "REGSAUDE",
    "TPGESTAO",
    "TP_LEITO",
    "CODLEITO",
    "QT_EXIST",
    "QT_SUS",
    "QT_NSUS",
]


# =============================================================================
# Tratamento — Leitos (CNES-LT)
# =============================================================================

def tratar_leitos(
    df_lt: pd.DataFrame,
    year: int,
    month: int,
    state: str = None,
    salvar: bool = True,
    pasta_saida: str = "data/processed",
) -> pd.DataFrame:
    """
    Trata o DataFrame bruto de leitos (CNES-LT) para qualquer estado/ano/mês:
    descreve tipo e subtipo de leito, padroniza tipos de coluna, remove
    leitos inexistentes (QT_EXIST = 0) e opcionalmente salva em parquet.

    Parâmetros:
        df_lt: DataFrame bruto retornado pelo PySUS (grupo LT do CNES)
        year: ano de referência dos dados, ex: 2026
        month: mês de referência dos dados, ex: 1
        state: sigla do estado (opcional, usada só para nomear o arquivo de saída)
        salvar: se True, exporta o resultado para parquet
        pasta_saida: pasta onde o parquet será salvo

    Retorna:
        DataFrame tratado, com colunas descritivas de tipo/subtipo de leito.
    """
    df = df_lt[COLUNAS_IMPORTANTES].copy()

    # --- Descrição do tipo de leito (macro) ---------------------------------
    df["TP_LEITO"] = df["TP_LEITO"].astype(str).str.strip()
    df["DS_TP_LEITO"] = df["TP_LEITO"].map(MASK_TP_LEITO)

    # --- Padronização: quantidades -> inteiro, com alerta -------------------
    colunas_numericas = ["QT_EXIST", "QT_SUS", "QT_NSUS"]
    for col in colunas_numericas:
        convertida = pd.to_numeric(df[col], errors="coerce")
        n_invalidos = convertida.isna().sum()
        if n_invalidos > 0:
            print(f"[ALERTA] {n_invalidos} valor(es) inválido(s) em '{col}' -> "
                  f"substituídos por 0. Revise antes de seguir.")
        df[col] = convertida.fillna(0).astype(int)

    # --- Padronização: códigos mantidos como texto ---------------------------
    colunas_codigo = ["TP_LEITO", "CODLEITO", "REGSAUDE", "CODUFMUN", "CNES"]
    for col in colunas_codigo:
        df[col] = df[col].astype(str).str.strip()

    df["DS_TP_LEITO"] = df["DS_TP_LEITO"].astype(str).str.strip()

    # --- Descrição do subtipo de leito, com alerta de código não mapeado ----
    chave_subtipo = list(zip(df["TP_LEITO"], df["CODLEITO"]))
    df["DS_SUBTIPO_LEITO"] = [MASK_SUBTIPO_LEITO.get(k) for k in chave_subtipo]

    n_subtipo_nao_mapeado = df["DS_SUBTIPO_LEITO"].isna().sum()
    if n_subtipo_nao_mapeado > 0:
        combinacoes_faltantes = sorted(set(
            k for k, desc in zip(chave_subtipo, df["DS_SUBTIPO_LEITO"]) if desc is None
        ))
        print(f"[ALERTA] {n_subtipo_nao_mapeado} linha(s) com combinação (TP_LEITO, CODLEITO) "
              f"fora da tabela de domínio conhecida -> DS_SUBTIPO_LEITO ficou nulo. "
              f"Combinações não mapeadas: {combinacoes_faltantes}. "
              f"Revise/atualize MASK_SUBTIPO_LEITO antes de seguir.")

    # --- Remove linhas sem leitos reais ---------------------------------------
    df = df[df["QT_EXIST"] != 0]

    df.info()

    # --- Exportação -----------------------------------------------------------
    if salvar:
        os.makedirs(pasta_saida, exist_ok=True)
        prefixo_uf = f"{state}_" if state else ""
        nome_arquivo = f"LT_{prefixo_uf}{year}{month:02d}.parquet"
        caminho = os.path.join(pasta_saida, nome_arquivo)
        df.to_parquet(caminho, index=False)
        print(f"Salvo em: {caminho}")

    return df


# =============================================================================
# Tratamento — SIH (internações, grupo RD)
# =============================================================================

COLUNAS_BASE_SIH = [
    "MUNIC_MOV", "CNES", "DT_INTER", "DT_SAIDA", "DIAS_PERM",
    "VAL_TOT", "MORTE", "SEXO", "IDADE", "COD_IDADE", "ESPEC",
]


def tratar_sih(
    df_bruto: pd.DataFrame,
    year: int,
    month: int,
    state: str = None,
    colunas_extra: list = None,
    salvar: bool = True,
    pasta_saida: str = "data/processed",
) -> pd.DataFrame:
    """
    Trata o DataFrame bruto de internações (SIH) para qualquer estado/ano/mês:
    seleciona colunas, converte tipos, recalcula dias_permanencia e
    opcionalmente salva em parquet.
    """
    colunas_extra = [c for c in (colunas_extra or []) if c not in COLUNAS_BASE_SIH]
    colunas_uteis = COLUNAS_BASE_SIH + colunas_extra

    faltantes = [c for c in colunas_uteis if c not in df_bruto.columns]
    if faltantes:
        raise KeyError(f"Colunas ausentes no DataFrame bruto do SIH: {faltantes}")

    df = df_bruto[colunas_uteis].copy()

    df = df.rename(columns={
        "MUNIC_MOV": "municipio_cod",
        "CNES": "hospital_cod",
        "DT_INTER": "data_internacao",
        "DT_SAIDA": "data_saida",
        "DIAS_PERM": "dias_permanencia",
        "ESPEC": "tp_leito",
        "VAL_TOT": "valor_total",
        "MORTE": "morte",
        "SEXO": "sexo",
        "IDADE": "idade",
        "COD_IDADE": "cod_idade",
    })

    df["data_internacao"] = pd.to_datetime(df["data_internacao"], format="%Y%m%d", errors="coerce")
    df["data_saida"] = pd.to_datetime(df["data_saida"], format="%Y%m%d", errors="coerce")
    df["valor_total"] = pd.to_numeric(df["valor_total"], errors="coerce")
    df["idade"] = pd.to_numeric(df["idade"], errors="coerce")
    # TODO: se quiser idade sempre em anos, normalize aqui usando cod_idade
    # (SIH: 2=dias, 3=meses, 4=anos — confira a tabela de domínio da versão que está usando)

    df["morte"] = pd.to_numeric(df["morte"], errors="coerce").map({0: False, 1: True})
    df["sexo"] = pd.to_numeric(df["sexo"], errors="coerce").map({1: "Masculino", 3: "Feminino"})

    n_antes = len(df)
    df["dias_permanencia"] = (df["data_saida"] - df["data_internacao"]).dt.days
    df = df[df["dias_permanencia"] >= 0]
    n_descartadas = n_antes - len(df)
    if n_descartadas:
        print(f"[tratar_sih] {n_descartadas} registros descartados "
              f"(datas inválidas ou dias_permanencia negativo) de {n_antes}.")

    if salvar:
        os.makedirs(pasta_saida, exist_ok=True)
        prefixo_uf = f"{state}_" if state else ""
        nome_arquivo = f"SIH_{prefixo_uf}{year}{month:02d}.parquet"
        caminho = os.path.join(pasta_saida, nome_arquivo)
        df.to_parquet(caminho, index=False)
        print(f"Salvo em: {caminho}")

    return df


# =============================================================================
# Tratamento — Hospitais por tipo de leito (cruza LT tratado + ST bruto)
# =============================================================================

def _detectar_coluna(df: pd.DataFrame, candidatos: list, obrigatoria: bool = True) -> str:
    """
    Encontra a primeira coluna de df que exista entre os nomes candidatos
    (tenta match exato, depois por substring). Levanta erro se obrigatória
    e nada for encontrado; senão retorna None.
    """
    for nome in candidatos:
        if nome in df.columns:
            return nome
    for nome in candidatos:
        achados = [c for c in df.columns if nome.upper() in c.upper()]
        if achados:
            return achados[0]
    if obrigatoria:
        raise KeyError(
            f"Nenhuma coluna encontrada entre os candidatos {candidatos}. "
            f"Colunas disponíveis: {df.columns.tolist()}"
        )
    return None


def _localizar_parquet_estabelecimentos(state: str, year: int, month: int,
                                          pasta: str = "data/raw/downloads/ducklake/st") -> str:
    """
    Localiza o parquet bruto de estabelecimentos já baixado (ex: STSP2605.parquet)
    dentro de data/raw/downloads/ducklake/st/, sem baixar nada.
    """
    padrao = os.path.join(pasta, f"ST{state}{str(year)[2:]}{month:02d}.parquet")
    candidatos = glob.glob(padrao)
    if not candidatos:
        raise FileNotFoundError(
            f"Nenhum arquivo de estabelecimentos encontrado em {padrao}. "
            "Rode a extração (get_dados_estabelecimentos) antes."
        )
    return candidatos[0]


def tratar_hospitais_por_tipo_leito(
    year: int,
    month: int,
    state: str,
    caminho_leitos_tratados: str = None,
    salvar: bool = True,
    pasta_saida: str = "data/processed",
) -> pd.DataFrame:
    """
    Lê o parquet de leitos já tratado (data/processed) e o parquet bruto de
    estabelecimentos já baixado (data/raw/downloads/ducklake/st), cruza os
    dois e gera um resumo por hospital: total de leitos existentes/SUS/não-SUS
    e leitos por tipo (macro), com nome do hospital. Não baixa nada.

    Parâmetros:
        year, month: usados para localizar o parquet de leitos tratado e o
            de estabelecimentos, e para nomear o arquivo de saída
        state: sigla do estado, ex: "SP"
        caminho_leitos_tratados: caminho do parquet de leitos já tratado.
            Se None, usa o padrão gerado por tratar_leitos:
            data/processed/LT_{state}_{ano}{mes:02d}.parquet
        salvar: se True, exporta o resultado para parquet
        pasta_saida: pasta onde o parquet será salvo
    """
    # --- 1. Ler o parquet de leitos já tratado ---------------------------------
    if caminho_leitos_tratados is None:
        caminho_leitos_tratados = f"data/processed/LT_{state}_{year}{month:02d}.parquet"

    if not os.path.exists(caminho_leitos_tratados):
        raise FileNotFoundError(
            f"Arquivo de leitos tratados não encontrado em {caminho_leitos_tratados}. "
            "Rode tratar_leitos() antes, ou informe caminho_leitos_tratados manualmente."
        )

    df_leito = pd.read_parquet(caminho_leitos_tratados)

    colunas_esperadas = {"CNES", "CODUFMUN", "TPGESTAO", "TP_LEITO", "DS_TP_LEITO",
                          "QT_EXIST", "QT_SUS", "QT_NSUS"}
    faltantes = colunas_esperadas - set(df_leito.columns)
    if faltantes:
        raise KeyError(
            f"{caminho_leitos_tratados} não tem as colunas esperadas {faltantes}. "
            "Confirme que o arquivo é saída de tratar_leitos()."
        )

    # --- 2. Ler o parquet bruto de estabelecimentos já baixado ------------------
    caminho_st = _localizar_parquet_estabelecimentos(state, year, month)
    df_nomes = pd.read_parquet(caminho_st)

    print("Colunas recebidas em estabelecimentos:", df_nomes.columns.tolist())

    col_cnes_st = _detectar_coluna(df_nomes, ["CO_CNES", "CNES"])
    col_fantasia = _detectar_coluna(df_nomes, ["NO_FANTASIA", "FANTASIA"], obrigatoria=False)
    col_razao = _detectar_coluna(df_nomes, ["NO_RAZAO_SOCIAL", "RAZAOSOCIAL", "RAZAO_SOCIAL"], obrigatoria=False)

    df_nomes[col_cnes_st] = df_nomes[col_cnes_st].astype(str).str.strip()

    n_dup_cnes = df_nomes[col_cnes_st].duplicated().sum()
    if n_dup_cnes > 0:
        print(f"[ALERTA] {n_dup_cnes} CNES duplicados no cadastro de estabelecimentos — "
              "mantendo apenas o primeiro registro de cada para não duplicar leitos no merge.")
        df_nomes = df_nomes.drop_duplicates(subset=col_cnes_st, keep="first")

    colunas_nome = [c for c in [col_fantasia, col_razao] if c]

    # --- 3. Cruzar leitos + nomes ---------------------------------------------
    df_completo = df_leito.merge(
        df_nomes[[col_cnes_st] + colunas_nome],
        left_on="CNES", right_on=col_cnes_st, how="left"
    )

    if col_fantasia:
        n_sem_nome = df_completo[col_fantasia].isna().sum()
        if n_sem_nome > 0:
            print(f"[ALERTA] {n_sem_nome} linha(s) de leito sem nome de estabelecimento "
                  "encontrado no cadastro CNES.")

    # --- 4. Total geral por hospital -------------------------------------------
    chaves_hospital = ["CNES", "CODUFMUN", "TPGESTAO"]

    resumo_hospital = (
        df_completo.groupby(chaves_hospital, dropna=False)
        .agg(
            TOTAL_EXISTENTES=("QT_EXIST", "sum"),
            TOTAL_SUS=("QT_SUS", "sum"),
            TOTAL_NSUS=("QT_NSUS", "sum"),
        )
        .reset_index()
        .sort_values("TOTAL_EXISTENTES", ascending=False)
    )

    # --- 5. Leitos por tipo (macro, TP_LEITO), em colunas, por hospital -------
    leitos_por_tipo = df_completo.pivot_table(
        index=chaves_hospital,
        columns="DS_TP_LEITO",
        values="QT_EXIST",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    # --- 6. Junta tudo e reincorpora o nome do hospital -------------------------
    nomes_por_cnes = (
        df_completo.drop_duplicates(subset="CNES")
        [["CNES"] + colunas_nome]
    )

    df_final = (
        resumo_hospital
        .merge(leitos_por_tipo, on=chaves_hospital)
        .merge(nomes_por_cnes, on="CNES", how="left")
    )

    print(df_final.shape)

    # --- 7. Exportação -----------------------------------------------------------
    if salvar:
        os.makedirs(pasta_saida, exist_ok=True)
        nome_arquivo = f"HP_P_TP_LT_{state}_{year}{month:02d}.parquet"
        caminho = os.path.join(pasta_saida, nome_arquivo)
        df_final.to_parquet(caminho, index=False)
        print(f"Salvo em: {caminho}")

    return df_final


if __name__ == "__main__":
    from extracao import get_dados_leitos, get_dados_sih
    df_lt_raw = get_dados_leitos(state="SP", year=2026, month=1)
    if df_lt_raw is not None:
       tratar_leitos(df_lt_raw, year=2026, month=1, state="SP")

    df_sih_raw = get_dados_sih(state="SP", year=2026, month=1)
    if df_sih_raw is not None:
        tratar_sih(df_sih_raw, year=2026, month=1, state="SP")

    df_hospitais = tratar_hospitais_por_tipo_leito(year=2026, month=1, state="SP")