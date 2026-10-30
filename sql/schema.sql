CREATE TABLE categories (
    category_id    VARCHAR(50) PRIMARY KEY,
    category_name  VARCHAR(100) NOT NULL
);

CREATE TABLE competitions (
    competition_id    VARCHAR(50) PRIMARY KEY,
    competition_name  VARCHAR(150) NOT NULL,
    parent_id         VARCHAR(50),
    type              VARCHAR(30),
    gender            VARCHAR(20),
    level             VARCHAR(50),
    category_id       VARCHAR(50) REFERENCES categories(category_id)
);

CREATE TABLE complexes (
    complex_id    VARCHAR(50) PRIMARY KEY,
    complex_name  VARCHAR(150) NOT NULL
);

CREATE TABLE venues (
    venue_id      VARCHAR(50) PRIMARY KEY,
    venue_name    VARCHAR(150) NOT NULL,
    city_name     VARCHAR(100),
    country_name  VARCHAR(100),
    country_code  VARCHAR(10),
    timezone      VARCHAR(100),
    complex_id    VARCHAR(50) REFERENCES complexes(complex_id)
);

CREATE TABLE competitors (
    competitor_id  VARCHAR(50) PRIMARY KEY,
    name           VARCHAR(150) NOT NULL,
    country        VARCHAR(100),
    country_code   VARCHAR(10),
    abbreviation   VARCHAR(20)
);

CREATE TABLE competitor_rankings (
    rank_id              SERIAL PRIMARY KEY,
    rank                 INTEGER,
    movement             INTEGER,
    points               INTEGER,
    competitions_played  INTEGER,
    competitor_id        VARCHAR(50) REFERENCES competitors(competitor_id)
);