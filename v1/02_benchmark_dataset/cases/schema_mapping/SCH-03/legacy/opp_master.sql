-- Excerpt of legacy_schema.sql (Meridian CRM 4.2, synthetic legacy artifact).
-- Legacy conventions: dates as VARCHAR2(8) YYYYMMDD ('00000000' = null);
-- amounts NUMBER(15,2) in the account currency (CURR_CD blank = USD); soft delete via DEL_FLG.

CREATE TABLE OPP_MASTER (
  OPP_ID      VARCHAR2(10) NOT NULL,      -- PK, format O########
  ACCT_ID     VARCHAR2(10),
  OPP_NM      VARCHAR2(120),
  STAT_CD     CHAR(1),                    -- P,Q,N,W,L (see data dictionary)
  STAGE_PCT   NUMBER(3),                  -- legacy duplicate of STAT_CD, 10/25/60/100/0
  AMT         NUMBER(15,2),
  CURR_CD     VARCHAR2(3),
  CLOSE_DT    VARCHAR2(8),
  OWNER_UID   VARCHAR2(8),
  TEAM_CD     VARCHAR2(4),
  LOST_RSN    VARCHAR2(2),                -- required when STAT_CD='L'
  CREATE_DT   VARCHAR2(8),
  UPD_DT      VARCHAR2(8),
  DEL_FLG     CHAR(1) DEFAULT 'N',
  PRIMARY KEY (OPP_ID)
);
