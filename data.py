import requests
import json
import requests
import pandas as pd
import creds

# ALL COUNTRY'S STATUS
class DataFlow:
    def __init__(self):
        pass

    def get_all_country_data(self):
        url = "https://api.covid19api.com/summary"

        try:
            # Request API
            response = requests.get(url)
        except:
            pass

        try:
            # Each nations data
            data = eval(response.text)["Countries"]

            # Features
            countries = [x["Country"] for x in data]
            country_code = [x["CountryCode"] for x in data]
            total_confirmed = [x["TotalConfirmed"] for x in data]
            total_deaths = [x["TotalDeaths"] for x in data]
            total_recovered = [x["TotalRecovered"] for x in data]

            # Converting to DataFrame
            data = {
                "country": countries,
                "total_confirmed": total_confirmed,
                "total_deaths": total_deaths,
                "total_recovered": total_recovered,
            }

            country_status = pd.DataFrame(data)
            return country_status

        except:
            print("DataPreprocessing Error")

    def get_vaccination_status_by_country_timeseries(self, country="India"):
        url = "https://covid-1967.p.rapidapi.com/vaccine/stats/country/name/{}".format(
            country
        )

        headers = creds.credentials

        try:
            # Requesting API data
            response = requests.request("GET", url, headers=headers)
        except:
            pass

        try:
            # Preprocessing Data
            data = eval(response.text)["data"]

            # Feautures
            dates = [x["date"] for x in data]
            total_vaccinations = [x["total_vaccinations"] for x in data]
            people_vaccinated = [x["people_vaccinated"] for x in data]
            people_fully_vaccinated = [x["people_fully_vaccinated"] for x in data]

            # Converting to DataFrame
            vaccination_data = pd.DataFrame(
                {
                    "dates": dates,
                    "total_vaccinations": total_vaccinations,
                    "people_vaccinated": people_vaccinated,
                    "people_fully_vaccinated": people_fully_vaccinated,
                }
            )

        except:
            print("Cannot Return Vaccination Data")

        return vaccination_data

    def get_selected_country_state_data(self, country="India"):
        url = "https://covid-1967.p.rapidapi.com/latest/country/name/{}".format(country)

        headers = creds.credentials

        try:
            # Requesting API data
            response = requests.request("GET", url, headers=headers)
        except:
            pass

        try:
            # Data Preprocessing
            data = eval(response.text)["data"]

            # Features
            state = [x["state"] for x in data]
            confirmed = [x["confirmed"] for x in data]
            deaths = [x["deaths"] for x in data]
            recovered = [x["recovered"] for x in data]
            active = [x["active"] for x in data]
            incident_rate = [x["incident_Rate"] for x in data]
            case_fatality_ratio = [x["case_fatality_ratio"] for x in data]

            # Converting to dataframe
            data = {
                "state": state,
                "confirmed": confirmed,
                "deaths": deaths,
                "recovered": recovered,
                "active": active,
                "incident_rate": incident_rate,
                "case_fatality_ratio": case_fatality_ratio,
            }

            country_states_data = pd.DataFrame(data)

        except:
            print("Data Preprocessing Error")

        return country_states_data

    def get_global_status(self):
        url = "https://covid-1967.p.rapidapi.com/latest/country/all"

        headers = creds.credentials

        # Requesting API data
        response = requests.request("GET", url, headers=headers)

        # returning results(a dictionary with all data)
        return eval(response.text)["total"]

    def get_timeseries_data_by_country(self,country,category):
        from datetime import date
        today = date.today()
        url = "https://api.covid19api.com/total/country/{}/status/{}?from=2020-03-01T00:00:00Z&to={}T00:00:00Z".format(country,category,today)

        r = requests.get(url)

        data = eval(r.text)
        date = [x['Date'] for x in data]
        cases = [ x['Cases'] for x in data]

        # Converting to daatframe
        timeseries = pd.DataFrame({"Date":date,category:cases})
        return timeseries

    