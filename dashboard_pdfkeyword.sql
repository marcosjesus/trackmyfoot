BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "dashboard_pdfkeyword" (
	"id"	integer NOT NULL,
	"pattern"	text,
	"description"	varchar(255) NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "dashboard_pdfkeyword" ("id","pattern","description") VALUES (37,'','Leg Use (%) R');
INSERT INTO "dashboard_pdfkeyword" ("id","pattern","description") VALUES (38,'','Leg Use (%) L');
INSERT INTO "dashboard_pdfkeyword" ("id","pattern","description") VALUES (39,'(\d+\.\d+|\d+)\s+Total Touches\s*\(#\)\s+(\d+\.\d+|\d+)','Total Touches (#)');
INSERT INTO "dashboard_pdfkeyword" ("id","pattern","description") VALUES (40,'(\d+\.\d+|\d+)\s+Work Rate \(yd/min\)\s+(\d+\.\d+|\d+)','Work Rate (yd/min)');
INSERT INTO "dashboard_pdfkeyword" ("id","pattern","description") VALUES (41,'(\d+\.\d+|\d+)\s+Accl/Decl \(#\)\s+(\d+\.\d+|\d+)','Accl/Decl (#)');
INSERT INTO "dashboard_pdfkeyword" ("id","pattern","description") VALUES (42,'(\d+\.\d+|\d+)\s+Sprint Distance \(y\)\s+(\d+\.\d+|\d+)','Sprint Distance (y)');
INSERT INTO "dashboard_pdfkeyword" ("id","pattern","description") VALUES (43,'(\d+\.\d+|\d+)\s+Distance Covered \(mi\)\s+(\d+\.\d+|\d+)','Distance Covered (mi)');
INSERT INTO "dashboard_pdfkeyword" ("id","pattern","description") VALUES (44,'(\d+\.\d+|\d+)\s+Total Releases \(#\)\s+(\d+\.\d+|\d+)','Total Releases (#)');
INSERT INTO "dashboard_pdfkeyword" ("id","pattern","description") VALUES (45,'(\d+\.\d+|\d+)\s+Long Possessions \(#\)\s+(\d+\.\d+|\d+)','Long Possessions (#)');
INSERT INTO "dashboard_pdfkeyword" ("id","pattern","description") VALUES (46,'(\d+\.\d+|\d+)\s+Short Possessions\s*\(#\)\s+(\d+\.\d+|\d+)','Short Possessions (#)');
INSERT INTO "dashboard_pdfkeyword" ("id","pattern","description") VALUES (47,'(\d+\.\d+|\d+)\s+One-Touch \(#\)\s+(\d+\.\d+|\d+)','One-Touch (#)');
INSERT INTO "dashboard_pdfkeyword" ("id","pattern","description") VALUES (48,'(\d+\.\d+|\d+)\s+Ball Possessions\s*\(#\)\s+(\d+\.\d+|\d+)','Ball Possessions');
COMMIT;
