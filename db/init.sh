#!/bin/bash
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE extension address_standardizer;
	INSERT INTO tiger.loader_platform(os, declare_sect, pgbin, wget, unzip_command, psql, path_sep,
			   loader, environ_set_command, county_process_command)
	SELECT 'debbie', declare_sect, pgbin, wget, unzip_command, psql, path_sep,
		   loader, environ_set_command, county_process_command
	  FROM tiger.loader_platform
	  WHERE os = 'sh';
	UPDATE tiger.loader_platform
		SET declare_sect = '
			TMPDIR="\${staging_fold}/temp/"
			UNZIPTOOL=unzip
			WGET="/usr/bin/wget -nc"
			export PGBIN=/usr/lib/postgresql/16/bin
			export PGUSER=postgres
			export PGPASSWORD=password
			export PGDATABASE=postgres
			PSQL=\${PGBIN}/psql
			SHP2PGSQL=shp2pgsql
			cd \${staging_fold}
		'
	WHERE os = 'debbie';
	UPDATE tiger.loader_lookuptables SET load = true WHERE table_name = 'zcta520';
	UPDATE tiger.loader_variables
		SET tiger_year = '2022',
			website_root = 'https://www2.census.gov/geo/tiger/TIGER2022',
			staging_fold = '/gisdata'
EOSQL

psql -c "SELECT Loader_Generate_Nation_Script('debbie')" -d postgres --no-psqlrc -tA > /gisdata/nation_script_load.sh
cd /gisdata
sh nation_script_load.sh

psql -c "SELECT Loader_Generate_Script(ARRAY['CA'], 'debbie')" -d postgres --no-psqlrc -tA > /gisdata/ca_script_load.sh
sh ca_script_load.sh

psql -c "SELECT tiger.install_missing_indexes()"
psql -c "ANALYZE"