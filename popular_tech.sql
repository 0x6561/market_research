CREATE TABLE POPULAR_TECH(
   ID             INT PRIMARY KEY  ,
   TERM           TEXT             NOT NULL,
   CATEGORY       TEXT             NOT NULL,
   CITY           TEXT             NOT NULL,
   STATE          TEXT             NOT NULL,
   COUNTRY        TEXT             NOT NULL,
   DATE           TEXT             NOT NULL,
   NUM_JOBS       INTEGER          NOT NULL
);
