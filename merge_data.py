"""
Hannah McGoran
02/25/2023
1. Substitutes incorrect concentration standard deviation data in 02/23/2023
with correct data through indexing by sample ID
2. Calculates potential density using GSW and adds it on to the isotope dataframe
3. Merges updated 02/23/2023 isotope+density data with master sheet data (331 samples to 329 samples)
4. Merges all of the aforementioned data with water mass percentages (329 samples to 272 samples)
"""
import pandas as pd
import numpy as np
import gsw as gsw


def convert_column(dataframe, column_name):  # Converts a column in a dataframe to a 1-D array
    prelim_list = list(dataframe[column_name])
    variable_array = [float(i) for i in prelim_list]
    return variable_array


def main():
    isotope = pd.read_csv("Updated GP16 Regression - New N2O Data.csv")
    new_conc = pd.read_csv("Updated GP16 Regression - New Concentrations.csv")
    mastersheet = pd.read_csv("Updated GP16 Regression - Other Variables from Main Sheet.csv")
    water_mass = pd.read_csv("Updated GP16 Regression - Water Mass Data (Pre-merge).csv")

    # Switch out old N2O concentrations with new N2O concentrations
    for i in range(len(new_conc["conc"])):
        samp_id = new_conc.at[i, "samp_num"]  # Identifies the sample ID to be replaced
        index = np.where(isotope["geotraces_numer"] == samp_id)[0][0]  # Identifies the index of the sample that needs to be replaced
        isotope.at[index, "N2O_nM"] = new_conc.at[i, "conc"]  # Replaces the conc at the index of interest with the updated conc
        isotope.at[index, "N2O_stdev_nM"] = new_conc.at[i, "stdev"]

    # Merge metadata with isotope data
    isotope_merge = pd.merge(mastersheet, isotope, on='geotraces_numer')  # Merges the new isotope data with the metadata

    # Calculate Potential Density
    salinity = convert_column(isotope_merge, "SALNTY")
    pressure = convert_column(isotope_merge, "CTDPRS")
    longitude = convert_column(isotope_merge, "LONGITUDE")
    latitude = convert_column(isotope_merge, "LATITUDE")
    temperature = convert_column(isotope_merge, "CTDTMP")
    abs_salinity = gsw.conversions.SA_from_SP(salinity, pressure, longitude, latitude)
    cons_temp = gsw.conversions.CT_from_t(abs_salinity, temperature, pressure)
    density = list(gsw.density.sigma0(abs_salinity, cons_temp))
    isotope_merge["Potdens"] = density  # Adds density as a column to the isotope dataframe

    # Merge isotope data + metadata with water mass data
    water_mass_merge = pd.merge(isotope_merge, water_mass, on='geotraces_numer')

    isotope_merge.to_csv(
           r'/Users/hannahmcgoran/Documents/Research/Second GP16 Linear Regression/merge_isotope.csv', index=False)
    water_mass_merge.to_csv(
          r'/Users/hannahmcgoran/Documents/Research/Second GP16 Linear Regression/merge_water_mass.csv', index=False)


if __name__ == "__main__":
    main()