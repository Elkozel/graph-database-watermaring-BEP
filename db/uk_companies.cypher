CREATE CONSTRAINT FOR (c:Company) REQUIRE c.companyNumber IS UNIQUE;
//Constraint for a node key is a Neo4j Enterprise feature only - run on an instance with enterprise
//CREATE CONSTRAINT FOR (p:Person) REQUIRE (p.birthMonth, p.birthYear, p.name) IS NODE KEY
CREATE CONSTRAINT FOR (p:Property) REQUIRE p.titleNumber IS UNIQUE;

LOAD CSV WITH HEADERS FROM "https://guides.neo4j.com/ukcompanies/data/PSCAmericans.csv" AS row1
MERGE (c:Company {companyNumber: row1.company_number});

LOAD CSV WITH HEADERS FROM "https://guides.neo4j.com/ukcompanies/data/PSCAmericans.csv" AS row2
MERGE (p:Person {name: row2.`data.name`, birthYear: row2.`data.date_of_birth.year`, birthMonth: row2.`data.date_of_birth.month`})
ON CREATE SET p.nationality = row2.`data.nationality`,
              p.countryOfResidence = row2.`data.country_of_residence`;
              // TODO: Address;

LOAD CSV WITH HEADERS FROM "https://guides.neo4j.com/ukcompanies/data/PSCAmericans.csv" AS row3
MATCH (c:Company {companyNumber: row3.company_number})
MATCH (p:Person {name: row3.`data.name`, birthYear: row3.`data.date_of_birth.year`, birthMonth: row3.`data.date_of_birth.month`})
MERGE (p)-[r:HAS_CONTROL]->(c)
 SET r.nature = split(replace(replace(replace(row3.`data.natures_of_control`, "[",""),"]",""),  '"', ""), ",");

LOAD CSV WITH HEADERS FROM "https://guides.neo4j.com/ukcompanies/data/CompanyDataAmericans.csv" AS row4
MATCH (c:Company {companyNumber: row4.` CompanyNumber`})
SET c.name = row4.CompanyName,
    c.mortgagesOutstanding = toInteger(row4.`Mortgages.NumMortOutstanding`),
    c.incorporationDate = Date(Datetime({epochSeconds: apoc.date.parse(row4.IncorporationDate,'s','dd/MM/yyyy')})),
    c.SIC = row4.`SICCode.SicText_1`,
    c.countryOfOrigin = row4.CountryOfOrigin,
    c.status = row4.CompanyStatus,
    c.category = row4.CompanyCategory;

LOAD CSV WITH HEADERS FROM "https://guides.neo4j.com/ukcompanies/data/ElectionDonationsAmericans.csv" AS row5
MATCH (c:Company) WHERE c.companyNumber = row5.CompanyRegistrationNumber
MERGE (p:Recipient {name: row5.RegulatedEntityName})
SET p.entityType = row5.RegulatedEntityType
MERGE (c)-[r:DONATED {ref: row5.ECRef}]->(p)
SET r.date  = Date(Datetime({epochSeconds: apoc.date.parse(row5.ReceivedDate,'s','dd/MM/yyyy')})),
    r.value = toFloat(replace(replace(row5.Value, "??", ""), ",", ""));

LOAD CSV WITH HEADERS FROM "https://guides.neo4j.com/ukcompanies/data/LandOwnershipAmericans.csv" AS row6
MATCH (c:Company {companyNumber: row6.`Company Registration No. (1)`})
MERGE (p:Property {titleNumber: row6.`Title Number`})
SET p.address = row6.`Property Address`,
    p.county  = row6.County,
    p.price   = toInteger(row6.`Price Paid`),
    p.district = row6.District
MERGE (c)-[r:OWNS]->(p)
WITH row6, c,r,p WHERE row6.`Date Proprietor Added` IS NOT NULL
SET r.date = Date(Datetime({epochSeconds: apoc.date.parse(row6.`Date Proprietor Added`,'s','dd-MM-yyyy')}));
CREATE INDEX CompanyIndex FOR (n:Company) ON (n.incorporationDate);

CALL db.schema.visualization();