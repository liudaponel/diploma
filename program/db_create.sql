CREATE TABLE data (
    id serial primary key,
    station text,
    year_ int not null,
    month_ int not null,
    day_ int not null,
    hour_ int not null,
    foEs float,
    fmin float,
    hhEs float,
    fbEs float
);

create table solar_activity (
    year_ int not null,
    month_ int not null,
    day_ int not null,
    f30 float
);