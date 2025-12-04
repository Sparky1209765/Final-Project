import unittest
import os
from energy_analyzer import EnergyAnalyzer, EnergyRecord, EnergyPrice

class TestEnergyAnalyzer(unittest.TestCase):
    def setUp(self):
        """Set up a new EnergyAnalyzer instance for each test."""
        self.analyzer = EnergyAnalyzer(base_year=2023)


    def test_load_data_from_csv(self):
        """Test loading data from CSV files."""
        # Create dummy files
        with open('test_records.csv', 'w') as f:
            f.write('year,region,sector,consumption,units\n')
            f.write('2022,SLO,Residential,100,GWh\n')
        with open('test_prices.csv', 'w') as f:
            f.write('year,sector,fuel_type,price,units\n')
            f.write('2022,Residential,Electricity,0.15,USD/kWh\n')
        with open('test_inflation.csv', 'w') as f:
            f.write('year,inflation_rate\n')
            f.write('2022,8.0\n')
        # Test records file
        self.analyzer.load_data_from_csv('test_records.csv', data_type='record')
        self.assertEqual(len(self.analyzer.records), 1)
        self.assertIsInstance(self.analyzer.records[0], EnergyRecord)
        self.assertEqual(self.analyzer.records[0].year, 2022)
        # Test prices file
        self.analyzer.load_data_from_csv('test_prices.csv', data_type='price')
        self.assertEqual(len(self.analyzer.prices), 1)
        self.assertIsInstance(self.analyzer.prices[0], EnergyPrice)
        self.assertEqual(self.analyzer.prices[0].price, 0.15)
        # Test inflation data file
        self.analyzer.load_data_from_csv('test_inflation.csv', data_type='inflation')
        self.assertEqual(len(self.analyzer.inflation_data), 1)
        self.assertEqual(self.analyzer.inflation_data[2022], 8.0)
        # Test FileNotFoundError. Yeah....
        self.analyzer.load_data_from_csv('non_existent_file.csv', data_type='record')
    # remove the stuff that was made for the test
        os.remove('test_records.csv')
        os.remove('test_prices.csv')
        os.remove('test_inflation.csv')


    def test_get_cpi_factor(self):
        self.analyzer.inflation_data = {2022: 8.0}
        cpi_factor = self.analyzer.get_cpi_factor(2022)
        self.assertAlmostEqual(cpi_factor, 1.08)


    def test_generate_inflation_adjusted_report(self):
        self.analyzer.prices.append(EnergyPrice(2022, 'Residential', 'Electricity', 0.15, 'USD/kWh'))
        self.analyzer.inflation_data = {2022: 8.0}
        report = self.analyzer.generate_inflation_adjusted_report('Residential', 'Electricity')
        self.assertIn('Inflation-Adjusted Price Report', report)
        self.assertIn('0.1620', report) # 0.15 * 1.08


    def test_generate_trend_report(self):
        self.analyzer.records.append(EnergyRecord(1990, 'SLO', 'Residential', 80, 'GWh'))
        self.analyzer.records.append(EnergyRecord(2024, 'SLO', 'Residential', 120, 'GWh'))
        report = self.analyzer.generate_trend_report('Residential', units_filter='GWh')
        self.assertIn('Trend Report for Residential', report)
        self.assertIn('Change over 34 years: 40.00 GWh', report)


    def test_generate_deviation_report(self):
        self.analyzer.records.append(EnergyRecord(2022, 'SLO', 'Residential', 100, 'GWh'))
        self.analyzer.records.append(EnergyRecord(2022, 'SLO', 'Non-Residential', 150, 'GWh'))
        report = self.analyzer.generate_deviation_report('Residential', 'Non-Residential', units_filter='GWh')
        self.assertIn('Deviation Gap Report', report)
        self.assertIn('50.00 GWh', report)


    def test_save_analysis_report(self):
        report_content = "Test report content."
        output_filename = 'test_report.txt'
        self.analyzer.save_analysis_report(output_filename, report_content)
        with open(output_filename, 'r') as f:
            content = f.read()
        self.assertEqual(content, report_content)
        os.remove(output_filename)


if __name__ == '__main__':
    unittest.main()