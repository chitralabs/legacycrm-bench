-- Excerpt of legacy_schema.sql (Meridian CRM 4.2): the four tables in scope for RIN-03.
-- Legacy conventions: NO declarative FKs (integrity enforced by application code and the
-- nightly integrity_check.crms); soft delete via DEL_FLG; dates VARCHAR2(8) YYYYMMDD.

CREATE TABLE ACCT_MASTER (
  ACCT_ID     VARCHAR2(10) NOT NULL,      -- PK, format A########
  ACCT_NM     VARCHAR2(80) NOT NULL,
  ACCT_TYP    CHAR(1),
  REGION_CD   VARCHAR2(3),
  ANN_REV     NUMBER(15,2),
  CURR_CD     VARCHAR2(3),
  CRED_LIMIT  NUMBER(12,2),
  CRED_HOLD   CHAR(1),
  CREATE_DT   VARCHAR2(8),
  DEL_FLG     CHAR(1) DEFAULT 'N',
  PRIMARY KEY (ACCT_ID)
);

CREATE TABLE CONT_MASTER (
  CONT_ID     VARCHAR2(10) NOT NULL,      -- PK, format K########
  ACCT_ID     VARCHAR2(10),               -- app-enforced ref -> ACCT_MASTER
  FRST_NM     VARCHAR2(40),
  LAST_NM     VARCHAR2(40) NOT NULL,
  EMAIL_TX    VARCHAR2(120),
  PREF_CH     CHAR(1),
  OPTOUT_FLG  CHAR(1),
  DEL_FLG     CHAR(1) DEFAULT 'N',
  PRIMARY KEY (CONT_ID)
);

CREATE TABLE ORD_HEADER (
  ORD_ID      VARCHAR2(10) NOT NULL,      -- PK, format D########
  ACCT_ID     VARCHAR2(10),               -- app-enforced ref -> ACCT_MASTER
  ORD_DT      VARCHAR2(8),
  STAT_CD     CHAR(1),                    -- E,A,S,I,X
  DISC_PCT    NUMBER(5,2),
  TOT_AMT     NUMBER(15,2),
  DEL_FLG     CHAR(1) DEFAULT 'N',
  PRIMARY KEY (ORD_ID)
);

CREATE TABLE ORD_LINE (
  ORD_ID      VARCHAR2(10) NOT NULL,      -- app-enforced ref -> ORD_HEADER
  LINE_NO     NUMBER(4) NOT NULL,
  PROD_ID     VARCHAR2(10),
  QTY         NUMBER(9),
  UNIT_PRC    NUMBER(12,2),
  EXT_AMT     NUMBER(15,2),
  DEL_FLG     CHAR(1) DEFAULT 'N',
  PRIMARY KEY (ORD_ID, LINE_NO)
);
