from energy_analyzer import EnergyAnalyzer
from datetime import datetime

def main():
    """Main function to run the energy analysis."""
    # Use the current year as the base for inflation adjustment
    base_year = datetime.now().year
    analyzer = EnergyAnalyzer(base_year=base_year)

    # --- Load all data ---
    analyzer.load_data_from_csv('data.csv', data_type='record')
    analyzer.load_data_from_csv('prices.csv', data_type='price')
    analyzer.load_data_from_csv('inflation.csv', data_type='inflation')

    # --- Insight 1: Identify Primary Consumption Driver ---
    report_content = "--- Energy Consumption Analysis for SLO County ---\n\n"
    report_content += "Insight 1: Primary Consumption Driver (Electricity)\n"
    report_content += analyzer.generate_trend_report('Non-Residential', units_filter='GWh') + "\n"
    report_content += analyzer.generate_trend_report('Residential', units_filter='GWh') + "\n"

    # Add the text-based deviation report
    report_content += analyzer.generate_deviation_report('Residential', 'Non-Residential', units_filter='GWh')

    # --- Insight 2: Quantify Industrial vs. Public Scale ---
    report_content += "\nInsight 2: Industrial vs. Public Gas Consumption (2022)\n"
    consumption_2022 = analyzer.get_consumption_by_sector(2022)
    smr_gas = consumption_2022.get('SMR-InternalGas', 0)
    public_gas = consumption_2022.get('Public Gas', 0)

    report_content += f"Santa Maria Refinery Internal Gas Use (2022): {smr_gas} mmscf\n"
    report_content += f"Total County Public Gas Use (2022): {public_gas} mmscf\n"
    if smr_gas > public_gas:
        report_content += "Generated Insight: Most natural gas is used by the refinery, which could be a factor in regional pricing.\n"
    else:
        report_content += "Generated Insight: Public gas usage is higher than the refinery's internal usage.\n"

    # --- Insight 3: Inflation-Adjusted Price Analysis ---
    report_content += "\n--- Inflation-Adjusted Price Analysis ---\n"
    report_content += analyzer.generate_inflation_adjusted_report('Residential', 'Electricity')
    report_content += analyzer.generate_inflation_adjusted_report('Non-Residential', 'Electricity')

    # --- Save the report ---
    analyzer.save_analysis_report('analysis_report.txt', report_content)
    print("Analysis complete. Report saved to analysis_report.txt")
    print("\n--- Report Content ---")

    #Prints actual report
    print(report_content)


if __name__ == "__main__":
    main()
