import csv
import statistics
import sys  # Import sys for terminating the program

def read_csv_and_analyze(file_path):
    """ Reads a CSV file, checks for disconnections, and prepares data for further analysis. """
    try:
        with open(file_path, 'r', newline='') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Retrieve the header to initialize data structures
            num_strings = len(headers) - 1  # Number of strings, excluding 'Hour'
            string_data = {header: [] for header in headers[1:]}
            std_devs = []
            below_threshold_count = [0] * num_strings  # Initialize count array with zeros

            for row_index, row in enumerate(reader):
                if len(row) != len(headers):
                    raise ValueError(f"Data row {row_index + 2} is malformed: {row}")
                
                hour = row[0]
                values = list(map(float, row[1:]))
                check_for_disconnection(headers[1:], values)  # Check for disconnection immediately
                
                for i, value in enumerate(values):
                    string_data[headers[i + 1]].append(value)

                # Calculate standard deviation if enough data points are present
                if len(values) > 1:
                    hourly_std = statistics.stdev(values)
                else:
                    hourly_std = 0  # Assign 0 if not enough data points
                std_devs.append(round(hourly_std, 2))

                # Check each value against 1.5 times the standard deviation
                for j, value in enumerate(values):
                    if value < 1.5 * hourly_std:
                        below_threshold_count[j] += 1

    except Exception as e:
        print(f"Failed to process the CSV file: {e}")
        sys.exit("Terminating program due to data processing error.")

    return headers, string_data, std_devs, below_threshold_count

def check_for_disconnection(headers, values):
    """ Checks if any string value is 0, indicating disconnection, and terminates if so. """
    for header, value in zip(headers, values):
        if value == 0:
            print(f"Alert: {header} has been disconnected.")
            sys.exit("Terminating program due to disconnection.")  # Exit the program with a message

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

# Example usage
file_path = 'hourly_data.csv'  # Update to your file path
headers, string_data, std_devs, below_threshold_count = read_csv_and_analyze(file_path)
display_results(headers, string_data, std_devs, below_threshold_count)