import pandas as pd
from sqlalchemy import create_engine
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path

engine = create_engine(
    "mssql+pyodbc://USER:PASSWORD@HOST/DB?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
)

# Filtro por conceptos que mencionaste, ajusta la tabla y columnas a tus nombres reales
SQL = """
SELECT 
  t470.f470_ts          AS fecha_doc,
  t470.f470_id_cia      AS compania,
  t470.f470_rowid       AS id_docto,
  t450.f450_rowid_docto AS id_doc_row,
  t470.f470_id_concepto AS concepto,
  t470.f470_rowid_item_ext AS cod_ref,
  t120.f120_referencia  AS codigo_item,
  t120.f120_descripcion AS item,
  t470.f470_id_unidad_medida AS unidad,
  t470.f470_cant_base   AS cantidad,
  t470.f470_costo_prom_uni AS costo_unitario,
  t470.f470_costo_prom_tot AS costo_total,
  t150.f150_descripcion AS bodega,
  t150.f150_id          AS codigo_bodega
FROM t470_cm_movto_invent t470
LEFT JOIN t450_cm_docto_invent t450 ON t450.f450_rowid_docto = t470.f470_rowid_docto
LEFT JOIN t150_mc_bodegas      t150 ON t150.f150_rowid       = t470.f470_rowid_bodega
LEFT JOIN t120_mc_items        t120 ON t120.f120_id          = t470.f470_rowid_item_ext
WHERE t470.f470_id_concepto IN (701, 511, 512, 602)
"""

out_dir = Path("data/mov_inventario_parquet")
out_dir.mkdir(parents=True, exist_ok=True)

chunks = pd.read_sql(SQL, engine, chunksize=100_000, parse_dates=["fecha_doc"])

for i, df in enumerate(chunks):
    # Partición simple por año/mes (mejora consultas temporales)
    df["anio"] = df["fecha_doc"].dt.year
    df["mes"]  = df["fecha_doc"].dt.month

    table = pa.Table.from_pandas(df)
    pq.write_to_dataset(
        table,
        root_path=str(out_dir),
        partition_cols=["anio","mes"]  # crea carpetas anio=YYYY/mes=MM
    )
    print(f"chunk {i} listo")


