-- Meridian CRM 4.2 core schema (synthetic legacy artifact; fictional system).
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

CREATE TABLE CASE_MASTER (
  CASE_ID     VARCHAR2(10) NOT NULL,      -- PK, format C########
  ACCT_ID     VARCHAR2(10),
  CONT_ID     VARCHAR2(10),
  SEV_CD      CHAR(1),                    -- 1=Critical 2=High 3=Normal 4=Low
  STAT_CD     CHAR(1),                    -- N=New, A=Assigned, P=Pending-Customer, R=Resolved, X=Closed
  SUBJ_TX     VARCHAR2(200),
  OPEN_DT     VARCHAR2(8),
  RES_DT      VARCHAR2(8),
  OWNER_UID   VARCHAR2(8),
  TEAM_CD     VARCHAR2(4),
  ESC_FLG     CHAR(1),
  DEL_FLG     CHAR(1) DEFAULT 'N',
  PRIMARY KEY (CASE_ID)
);

CREATE TABLE PROD_MASTER (
  PROD_ID     VARCHAR2(10) NOT NULL,      -- PK, format P########
  PROD_NM     VARCHAR2(80),
  FAMILY_CD   VARCHAR2(4),
  LIST_PRC    NUMBER(12,2),
  ACTIVE_FLG  CHAR(1),
  EOL_DT      VARCHAR2(8),                -- end-of-life date
  DEL_FLG     CHAR(1) DEFAULT 'N',
  PRIMARY KEY (PROD_ID)
);

CREATE TABLE ORD_HEADER (
  ORD_ID      VARCHAR2(10) NOT NULL,      -- PK, format D########
  ACCT_ID     VARCHAR2(10),
  ORD_DT      VARCHAR2(8),
  STAT_CD     CHAR(1),                    -- E=Entered, A=Approved, S=Shipped, I=Invoiced, X=Cancelled
  CURR_CD     VARCHAR2(3),
  DISC_PCT    NUMBER(5,2),                -- header discount percent, 0..100
  TOT_AMT     NUMBER(15,2),               -- denormalized: sum of line EXT_AMT after header discount
  OWNER_UID   VARCHAR2(8),
  DEL_FLG     CHAR(1) DEFAULT 'N',
  PRIMARY KEY (ORD_ID)
);

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

CREATE TABLE ACT_LOG (
  ACT_ID      VARCHAR2(10) NOT NULL,      -- PK, format T########
  ENT_NAME    VARCHAR2(12),               -- parent entity table name
  ENT_ID      VARCHAR2(10),
  ACT_TYP     CHAR(1),                    -- C=Call, E=Email, M=Meeting, K=Task
  ACT_DT      VARCHAR2(8),
  DONE_FLG    CHAR(1),
  NOTES_TX    VARCHAR2(500),
  OWNER_UID   VARCHAR2(8),
  DEL_FLG     CHAR(1) DEFAULT 'N',
  PRIMARY KEY (ACT_ID)
);

CREATE TABLE USR_MASTER (
  USR_ID      VARCHAR2(8) NOT NULL,       -- PK
  USR_NM      VARCHAR2(60),
  ROLE_ID     VARCHAR2(8),
  TEAM_CD     VARCHAR2(4),
  MGR_UID     VARCHAR2(8),
  ACTIVE_FLG  CHAR(1),
  DEL_FLG     CHAR(1) DEFAULT 'N',
  PRIMARY KEY (USR_ID)
);

CREATE TABLE ROLE_DEF (
  ROLE_ID     VARCHAR2(8) NOT NULL,
  ROLE_NM     VARCHAR2(40),
  PRIMARY KEY (ROLE_ID)
);

CREATE TABLE INT_ENDPOINT (
  EP_NAME     VARCHAR2(20) NOT NULL,
  EP_URL      VARCHAR2(200),
  AUTH_TYP    VARCHAR2(10),
  ACTIVE_FLG  CHAR(1),
  PRIMARY KEY (EP_NAME)
);

CREATE TABLE AUD_EVENT (
  EVT_ID      NUMBER(12) NOT NULL,
  EVT_TS      VARCHAR2(14),               -- YYYYMMDDHH24MISS
  EVT_CD      VARCHAR2(12),
  USR_ID      VARCHAR2(8),
  ENT_NAME    VARCHAR2(12),
  ENT_ID      VARCHAR2(10),
  OLD_VAL     VARCHAR2(500),
  NEW_VAL     VARCHAR2(500),
  PRIMARY KEY (EVT_ID)
);
