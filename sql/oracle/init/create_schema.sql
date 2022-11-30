create user user_etl identified by <enter password>;

grant dba to user_etl;

grant connect to user_etl;

create user courts_info;

alter user courts_info quota unlimited on USERS;
