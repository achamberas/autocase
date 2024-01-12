CREATE OR REPLACE EXTERNAL TABLE simulation_poc.idf_runs
  OPTIONS (
  format = 'CSV',
  uris = [
    'gs://carbonsight_eplus/idf_run1/2009_5A_RetailStripmall_V2_S1_R1/per_idf_energy_csv/*.csv',
    'gs://carbonsight_eplus/idf_run1/2009_5B_RetailStripmall_V2_S1_R1/per_idf_energy_csv/*.csv',
    'gs://carbonsight_eplus/idf_run1/2009_5C_RetailStripmall_V2_S1_R1/per_idf_energy_csv/*.csv',
    'gs://carbonsight_eplus/idf_run1/2009_6A_RetailStripmall_V2_S1_R1/per_idf_energy_csv/*.csv',
    'gs://carbonsight_eplus/idf_run1/2009_6B_RetailStripmall_V2_S1_R1/per_idf_energy_csv/*.csv',
    'gs://carbonsight_eplus/idf_run1/2010_5A_RetailStripmall_V2_S2_R1/per_idf_energy_csv/*.csv',
    'gs://carbonsight_eplus/idf_run1/2009_1A_RetailStripmall_V1_S1_R1/per_idf_energy_csv/*.csv'
  ],
  skip_leading_rows = 1);

SELECT split(_FILE_NAME, "/")[4] as sim_hash, * 
FROM `autocase-201317.simulation_poc.idf_runs`;