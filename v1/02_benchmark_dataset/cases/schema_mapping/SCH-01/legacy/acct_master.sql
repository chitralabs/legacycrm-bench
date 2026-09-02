-- Excerpt of legacy_schema.sql (Meridian CRM 4.2, synthetic legacy artifact).
-- Legacy conventions: no declarative FKs; dates as VARCHAR2(8) YYYYMMDD ('00000000' = null);
-- booleans as CHAR(1) Y/N; soft delete via DEL_FLG.

CREATE TABLE ACCT_MASTER (
  ACCT_ID     VARCHAR2(10) NOT NULL,      -- PK, format A########
  ACCT_NM     VARCHAR2(80) NOT NULL,
  ACCT_TYP    CHAR(1),                    -- C=Customer, P=Prospect, R=Partner, X=Inactive
  SIC_CD      VARCHAR2(4),
  REGION_CD   VARCHAR2(3),                -- e.g. NAM, EMA, APA, LAT
  ANN_REV     NUMBER(15,2),
  CURR_CD     VARCHAR2(3),                -- blank = USD
  OWNER_UID   VARCHAR2(8),
  TEAM_CD     VARCHAR2(4),
  CRED_LIMIT  NUMBER(12,2),
  CRED_HOLD   CHAR(1),                    -- Y/N
  CREATE_DT   VARCHAR2(8),
  UPD_DT      VARCHAR2(8),
  DEL_FLG     CHAR(1) DEFAULT 'N',
  PRIMARY KEY (ACCT_ID)
);
