-- Excerpt of legacy_schema.sql (Meridian CRM 4.2): the ORD_LINE table.
-- Legacy conventions: no declarative FKs; soft delete via DEL_FLG.
CREATE TABLE ORD_LINE (
  ORD_ID      VARCHAR2(10) NOT NULL,
  LINE_NO     NUMBER(4) NOT NULL,         -- starts at 1, contiguous
  PROD_ID     VARCHAR2(10),
  QTY         NUMBER(9),
  UNIT_PRC    NUMBER(12,2),
  EXT_AMT     NUMBER(15,2),               -- QTY * UNIT_PRC, line-level, before header discount
  DEL_FLG     CHAR(1) DEFAULT 'N',
  PRIMARY KEY (ORD_ID, LINE_NO)
);
