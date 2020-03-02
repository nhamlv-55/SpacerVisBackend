#!/bin/sh
sqlite3 exp_db "create table exp(name varchar(100), done bool, result varchar(5), time int, aux varchar(200));"
