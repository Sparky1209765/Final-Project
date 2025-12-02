import csv
from datetime import datetime

class EnergyRecord:
    """Represents a single record of energy consumption."""
    def __init__(self, year, region, sector, consumption, units):
        self.year = int(year)
        self.region = region
        self.sector = sector
        self.consumption = float(consumption)
        self.units = units

    def __repr__(self):
        return f"EnergyRecord({self.year}, '{self.region}', '{self.sector}', {self.consumption}, '{self.units}')"

class EnergyPrice:
    """Represents a single record of energy price."""
    def __init__(self, year, sector, fuel_type, price, units):
        self.year = int(year)
        self.sector = sector
        self.fuel_type = fuel_type
        self.price = float(price)
        self.units = units

    def __repr__(self):
        return f"EnergyPrice({self.year}, '{self.sector}', '{self.fuel_type}', {self.price}, '{self.units}')"

class EnergyAnalyzer:
    """Analyzes energy consumption and price data."""
    def __init__(self, base_year=datetime.now().year):
        self.records = []
        self.prices = []
        self.inflation_data = {}
        self.base_year = base_year

    def load_data_from_csv(self, filename, data_type='record'):
        """Loads data from a CSV file into the appropriate list."""
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                if data_type == 'inflation':
                    for row in reader:
                        self.inflation_data[int(row['year'])] = float(row['inflation_rate'])
                else:
                    for row in reader:
                        if data_type == 'record':
                            record = EnergyRecord(row['year'], row['region'], row['sector'], row['consumption'], row['units'])
                            self.records.append(record)
                        elif data_type == 'price':
                            price = EnergyPrice(row['year'], row['sector'], row['fuel_type'], row['price'], row['units'])
                            self.prices.append(price)
        except FileNotFoundError:
            print(f"Error: {filename} not found.")
        except Exception as e:
            print(f"An error occurred while loading {filename}: {e}")

    def get_cpi_factor(self, year):
        """Calculates the cumulative price index factor to adjust a value from a given year to the base year."""
        if not self.inflation_data:
            return 1.0
        
        cpi_factor = 1.0
        for y in range(year, self.base_year):
            inflation_rate = self.inflation_data.get(y, 0) / 100
            cpi_factor *= (1 + inflation_rate)
        return cpi_factor

    def generate_inflation_adjusted_report(self, sector, fuel_type):
        """Generates a report showing nominal vs. inflation-adjusted prices."""
        sector_prices = [p for p in self.prices if p.sector == sector and p.fuel_type == fuel_type]
        if not sector_prices:
            return f"No price data found for {sector} {fuel_type}."

        report = f"\nInflation-Adjusted Price Report for {sector} {fuel_type} (Base Year: {self.base_year}):\n"
        report += "Year | Nominal Price | Adjusted Price (in {self.base_year} USD)\n"
        report += "---- | ------------- | ----------------------------------\n"

        for p in sorted(sector_prices, key=lambda x: x.year):
            cpi_factor = self.get_cpi_factor(p.year)
            adjusted_price = p.price * cpi_factor
            report += f"{p.year} | ${p.price:.4f}        | ${adjusted_price:.4f}\n"
        
        return report

    def get_consumption_by_sector(self, year):
        """Returns a dictionary mapping sectors to consumption values for a given year."""
        # ... (rest of the methods are unchanged)
        consumption_by_sector = {}
        for record in self.records:
            if record.year == year:
                if record.sector in consumption_by_sector:
                    consumption_by_sector[record.sector] += record.consumption
                else:
                    consumption_by_sector[record.sector] = record.consumption
        return consumption_by_sector

    def generate_trend_report(self, sector, units_filter=None):
        sector_records = [r for r in self.records if r.sector == sector]
        if units_filter:
            sector_records = [r for r in sector_records if r.units == units_filter]

        if not sector_records:
            return f"No data found for sector: {sector} with units: {units_filter or 'any'}"

        report = f"Trend Report for {sector} ({units_filter or 'All'}):\n"
        sector_records.sort(key=lambda r: r.year)
        first_year_record = sector_records[0]
        last_year_record = sector_records[-1]

        change = last_year_record.consumption - first_year_record.consumption
        report += f"Consumption in {first_year_record.year}: {first_year_record.consumption} {first_year_record.units}\n"
        report += f"Consumption in {last_year_record.year}: {last_year_record.consumption} {last_year_record.units}\n"
        report += f"Change over {last_year_record.year - first_year_record.year} years: {change:.2f} {last_year_record.units}\n"
        return report

    def generate_deviation_report(self, sector1, sector2, units_filter):
        s1_records = {r.year: r.consumption for r in self.records if r.sector == sector1 and r.units == units_filter}
        s2_records = {r.year: r.consumption for r in self.records if r.sector == sector2 and r.units == units_filter}

        all_years = sorted(list(set(s1_records.keys()) | set(s2_records.keys())))

        report = f"\nDeviation Gap Report ({sector2} vs {sector1} for {units_filter}):\n"
        report += "Year | Deviation (Non-Residential - Residential)\n"
        report += "---- | -----------------------------------------\n"

        for year in all_years:
            s1_val = s1_records.get(year, 0)
            s2_val = s2_records.get(year, 0)
            deviation = s2_val - s1_val
            report += f"{year} | {deviation:.2f} {units_filter}\n"
        
        return report

    def save_analysis_report(self, output_filename, report_content):
        with open(output_filename, "w") as f:
            f.write(report_content)
