drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  'text' text not null
);

DROP TABLE IF EXISTS users;
CREATE TABLE users(
  username text PRIMARY KEY ,
  password text not NULL
)