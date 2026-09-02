-- Excerpt of legacy_schema.sql (Meridian CRM 4.2, synthetic legacy artifact).
-- Legacy conventions: dates as VARCHAR2(8) YYYYMMDD ('00000000' = null);
-- booleans as CHAR(1) Y/N (blank = N); soft delete via DEL_FLG.

CREATE TABLE CONT_MASTER (
  CONT_ID     VARCHAR2(10) NOT NULL,      -- PK, format K########
  ACCT_ID     VARCHAR2(10),               -- app-enforced ref -> ACCT_MASTER
  FRST_NM     VARCHAR2(40),
  LAST_NM     VARCHAR2(40) NOT NULL,
  EMAIL_TX    VARCHAR2(120),
  PHONE_TX    VARCHAR2(24),
  PREF_CH     CHAR(1),                    -- E=email, P=phone, M=mail, blank=E
  OPTOUT_FLG  CHAR(1),                    -- Y = no marketing contact
  OWNER_UID   VARCHAR2(8),
  TEAM_CD     VARCHAR2(4),
  CREATE_DT   VARCHAR2(8),
  DEL_FLG     CHAR(1) DEFAULT 'N',
  PRIMARY KEY (CONT_ID)
);
