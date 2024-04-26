import csv
import statistics
import sys  # Import sys for terminating the program

# Set to keep track of disconnected strings
disconnected_strings = set()
def read_csv_and_analyze(file_path):
    try:
        with open(file_path, 'r', newline='') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Retrieve the header
            num_strings = len(headers) - 1
            string_data = {header: [] for header in headers[1:]}
            std_devs = []
            below_threshold_count = [0] * num_strings

            for row_index, row in enumerate(reader):
                if len(row) != len(headers):
                    raise ValueError(f"Data row {row_index + 2} is malformed: {row}")

                hour = row[0]
                values = list(map(float, row[1:]))
                disconnections = check_for_disconnection(headers[1:], values)
                
                # Loop through each value, checking disconnection status
                for i, value in enumerate(values):
                    if disconnections[i]:  # Check if the current string is disconnected
                        string_data[headers[i + 1]].append(0)
                    else:
                        string_data[headers[i + 1]].append(value)

                # Filter valid values for standard deviation calculation
                valid_values = [value for i, value in enumerate(values) if not disconnections[i]]
                if len(valid_values) > 1:
                    hourly_std = statistics.stdev(valid_values)
                else:
                    hourly_std = 0
                std_devs.append(round(hourly_std, 2))

                # Threshold check based on valid values
                for j, value in enumerate(values):
                    if not disconnections[j] and value < 1.5 * hourly_std:
                        below_threshold_count[j] += 1

    except Exception as e:
        print(f"Failed to process the CSV file: {e}")
        return None

    return headers, string_data, std_devs, below_threshold_count

def check_for_disconnection(headers, values):
    """ Identifies if any string value is 0, indicating disconnection. """
    global disconnected_strings
    disconnections = [value == 0 for value in values]
    for header, disconnected in zip(headers, disconnections):
        if disconnected and header not in disconnected_strings:
            print(f"Alert: {header} has been disconnected.")
            disconnected_strings.add(header)
    return disconnections


def calculate_hourly_sums(string_data):
    """ Calculate the sum of all string outputs for each hour. """
    hourly_sums = []
    num_hours = len(next(iter(string_data.values())))  # Assuming all strings have the same number of hours recorded
    for i in range(num_hours):
        hourly_sum = sum(data[i] for data in string_data.values() if data[i] is not None)  # Ensure to skip any None values
        hourly_sums.append(hourly_sum)
    return hourly_sums

def display_results(headers, string_data, std_devs, below_threshold_count):
    """ Prints the string data, standard deviations, and counts of low values. """
    print("String Data (Column-wise):")
    for string, data in string_data.items():
        print(f"{string}: {['{:.2f}'.format(x) for x in data]}")
    print("\nHourly Standard Deviations:")
    for std in std_devs:
        print(f"{std:.2f}")
    print("\nCounts of values below 1.5 times the hourly std deviation:")
    for i, count in enumerate(below_threshold_count):
        print(f"{headers[i+1]}: {count}")

def calculate_daily_sums(string_data):
    """ Calculate the total sum of each string's output for the entire day. """
    daily_sums = {}
    for string, data in string_data.items():
        daily_sum = sum(data)  # Sum all the data points for each string
        daily_sums[string] = daily_sum
    return daily_sums

def calculate_string_totals(string_data):
    """ Calculate the total output for each string over the entire dataset. """
    string_totals = {string: sum(data) for string, data in string_data.items()}
    return string_totals

def calculate_grand_total(string_totals):
    """ Calculate the grand total of all outputs across all strings. """
    grand_total = sum(string_totals.values())
    return grand_total

def calculate_percentage_difference(standard_total, hourly_total):
    """ Calculate the percentage difference between standard and hourly totals. """
    try:
        percentage_difference = ((standard_total - hourly_total) / standard_total) * 100
    except ZeroDivisionError:
        return 0  # Avoid division by zero if standard_total is zero
    return percentage_difference

def main():
    try:
        error_threshold = 6.26
        file_path = 'hourly_data.csv'
        filestandardpath = 'standarddata.csv'
        
        results = read_csv_and_analyze(file_path)
        standardresults = read_csv_and_analyze(filestandardpath)
        
        if results and standardresults:
            # Hourly Data Analysis
            headers, string_data, std_devs, below_threshold_count = results
            hourly_sums = calculate_hourly_sums(string_data)
            string_totals = calculate_string_totals(string_data)
            grand_total_hourly = calculate_grand_total(string_totals)
            
            # Standard Data Analysis
            _, standard_string_data, _, _ = standardresults
            standard_string_totals = calculate_string_totals(standard_string_data)
            grand_total_standard = calculate_grand_total(standard_string_totals)
            
            # Display Results
            display_results(headers, string_data, std_devs, below_threshold_count)
            print("\nHourly Sums of All Strings:")
            print(hourly_sums)
            print("\nTotal Output for Each String:")
            for string, total in string_totals.items():
                print(f"{string}: {total:.2f}")
            print(f"\nGrand Total of All Outputs: {grand_total_hourly:.2f}")

            # Calculate and Check Performance
            percentage_difference = calculate_percentage_difference(grand_total_standard, grand_total_hourly)
            if percentage_difference > error_threshold:
    # Gather underperforming strings excluding disconnected ones for clear separation
                underperforming_strings = [header for i, header in enumerate(headers[1:]) if below_threshold_count[i] > 0 and header not in disconnected_strings]
                disconnected_string_list = list(disconnected_strings)  # Convert to list for easier manipulation
    
    # Construct the message
                underperformance_message = f"Hourly data is underperforming by {percentage_difference:.2f}%."
            if underperforming_strings:
                underperformance_message += f" Key contributors to the inefficiency are {', '.join(underperforming_strings)}."
            if disconnected_string_list:
                underperformance_message += f" Disconnected strings: {', '.join(disconnected_string_list)}."
    
    # Print the comprehensive message
            print(underperformance_message)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
