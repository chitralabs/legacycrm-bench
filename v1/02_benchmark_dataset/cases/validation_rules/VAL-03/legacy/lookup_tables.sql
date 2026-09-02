-- Excerpt of legacy_schema.sql: the tables referenced by ORD-002/ORD-005 LOOKUPs.
-- Soft delete via DEL_FLG ('Y' rows are invisible to LOOKUP, which sees live rows only).

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
