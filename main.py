import yaml
from ciscoconfparse import CiscoConfParse
from difflib import unified_diff
from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text
from rich.markdown import Markdown


# Instantiate the console with recording enabled
console = Console(record=True)

def normalize_config(config_lines):
    """
    Normalize configuration lines:
    - Strips leading/trailing whitespace.
    - Breaks down multiline blocks into individual lines.
    - Ensures consistent spacing to match golden standard format.
    """
    normalized_lines = []
    for line in config_lines:
        # Strip any leading or trailing spaces
        line = line.strip()
        if line:  # Ignore empty lines
            normalized_lines.append(line)
    return normalized_lines


def validate_section(config_parse, expected_lines):
    """
    Validate a section of the configuration against expected lines.
    Returns a tuple containing lists of matched lines and unmatched lines.
    """
    matched_lines = []
    unmatched_lines = []

    for expected_line in expected_lines:
        # Extract the prefix to handle wildcards
        match_prefix = expected_line.split('{{')[0].strip()
        matching_lines = [
            obj.text.strip()
            for obj in config_parse.find_objects(rf"^{match_prefix}")
        ]

        # Check if any of the matching lines align with the expected format
        matched = any(
            match_prefix in line
            for line in matching_lines
        )

        if matched:
            matched_lines.append(expected_line)
        else:
            unmatched_lines.append(expected_line)

    return matched_lines, unmatched_lines


def generate_diff(section, unmatched, config_lines):
    """
    Generate a unified diff for unmatched lines against the actual config.
    """
    section_title = f"## Section: {section}\n"
    expected = [section_title] + unmatched + ["\n"]
    actual = [section_title] + config_lines + ["\n"]
    return list(unified_diff(expected, actual, lineterm=""))


def validate_config(config_file, golden_standard_file):
    """
    Validate the configuration file against the golden standard.
    Outputs matched, unmatched lines into structured reports and shows a diff.
    """
    # Load the configuration file and golden standard
    with open(config_file, 'r') as f:
        raw_config = f.readlines()

    with open(golden_standard_file, 'r') as f:
        golden_standard = yaml.safe_load(f)

    # Normalize the configuration lines
    normalized_config = normalize_config(raw_config)
    parse = CiscoConfParse(normalized_config)

    validation_results = {}
    matches = {}
    terminal_diff = []

    # Validate each section
    for section, expected_lines in golden_standard.items():
        matched, unmatched = validate_section(parse, expected_lines)
        validation_results[section] = {
            "matched": matched,
            "unmatched": unmatched
        }
        matches[section] = matched

        # Generate diff for unmatched lines
        if unmatched:
            diff = generate_diff(section, unmatched, normalized_config)
            terminal_diff.extend(diff)

    # Write unmatched lines to a sectioned report
    with open(f'{reportname}-validation_failures.txt', 'w') as failure_report:
        failure_report.write("Validation Report for {reportname} - Lines from {config_file} that did NOT match Golden_Standard\n")
        for section, results in validation_results.items():
            if results["unmatched"]:
                failure_report.write(f"\n## Section: {section}\n")
                for line in results["unmatched"]:
                    failure_report.write(f"{line}\n")

    # Write matched lines to a sectioned report
    with open(f'{reportname}-validation_successes.txt', 'w') as success_report:
        success_report.write("Validation Report {reportname} - Lines from {config_file} that MATCHED Golden_Standard\n")
        for section, matched_lines in matches.items():
            if matched_lines:
                success_report.write(f"\n## Section: {section}\n")
                for line in matched_lines:
                    success_report.write(f"{line}\n")

    # Optional diff report
    with open(f'{reportname}-validation_differences.txt', 'w') as diff_report:
        diff_report.write(f"Validation Report for {reportname} - \n Differences between expected  and actual configuration ({config_file})\n")
        for section, results in validation_results.items():
            unmatched = results["unmatched"]
            if unmatched:
                diff_report.write(f"\n## Section: {section}\n")
                diff_report.write("Expected but not found:\n")
                for line in unmatched:
                    diff_report.write(f"{line}\n")
                diff_report.write("\n")

    # Display visual diff in terminal with rich
    if terminal_diff:
        console.print("\n[bold cyan]Visual Diff Report:[/bold cyan]")
        diff_output = "\n".join(terminal_diff)
        highlighted_diff = Syntax(diff_output, "diff", theme="monokai", line_numbers=False)
        console.print(highlighted_diff)

        # Save colorful diff to an HTML file
        html_diff_file = f'{reportname}-color_diff.html'
        diff_syntax = Syntax(diff_output, "diff", theme="monokai", line_numbers=False)
        console.print(diff_syntax)
        html_content = console.export_html(clear=False)  # Export recorded content to HTML
        with open(html_diff_file, 'w') as html_file:
            html_file.write(html_content)

        print(f"\n Your Pretty Colorful diff saved to {html_diff_file}")
    print(f"\nValidation completed. Reports saved as '{reportname}-validation_failures.txt', '{reportname}-validation_successes.txt', and '{reportname}-validation_differences.txt'.")

if __name__ == "__main__":
    """
    Print banner and advise:
    This tool is used  for convienence only and should be one of many
    tools used to help validate config complianec. NOT THE ONLY SOURCE
    OF VALIDATION! Use at your own right.
    How to:
        1:Ensure the "golden_standard.yaml" file is completed with the
            sections the config is to be against and make sure it lives
            in the same directory as the script file.
            validated against 
        2:Place the config file to be vali-diff-erated in the same
            directory as this script and the "golden_standard.yaml"
        3:Execute script, input project name or some identifier for the
            filenames as it will be used when saving output reports.
        4:With luck, the script will complete and output 4 reports...
            validation "matches", "failures", "differences" and finally
            an HTML version of an actual DIFF comparison for your enjoyment!
    # Example usage
        validate_config('config.txt', 'golden_standard.yaml')
    """
    print("""
         __          __    _                                _           _    _                    
         \ \        / /   | |                              | |         | |  | |                   
          \ \  /\  / /___ | |  ___  ___   _ __ ___    ___  | |_  ___   | |_ | |__    ___          
           \ \/  \/ // _ \| | / __|/ _ \ | '_ ` _ \  / _ \ | __|/ _ \  | __|| '_ \  / _ \         
            \  /\  /|  __/| || (__| (_) || | | | | ||  __/ | |_| (_) | | |_ | | | ||  __/         
             \/  \/__\___||_| \___|\___/_|_| |_| |_| \___|  \__|\___/   \__||_| |_| \___|         
                 / ____|              / _|(_)                                                     
                | |      ___   _ __  | |_  _   __ _                                               
                | |     / _ \ | '_ \ |  _|| | / _` |                                              
                | |____| (_) || | | || |  | || (_| |                                              
                 \_____|\___/ |_| |_||_|  |_| \__, |                                              
                                               __/ |                                              
         __      __     _  _             _  _ |___/  __                           _               
         \ \    / /    | |(_)           | |(_) / _| / _|                         | |              
          \ \  / /__ _ | | _  ______  __| | _ | |_ | |_  ______  ___  _ __  __ _ | |_  ___   _ __ 
           \ \/ // _` || || ||______|/ _` || ||  _||  _||______|/ _ \| '__|/ _` || __|/ _ \ | '__|
            \  /| (_| || || |       | (_| || || |  | |         |  __/| |  | (_| || |_| (_) || |   
             \/  \__,_||_||_|        \__,_||_||_|  |_|          \___||_|   \__,_| \__|\___/ |_|   
                 ___    ___    ___    ___                                                         
                |__ \  / _ \  / _ \  / _ \                                                        
                   ) || | | || | | || | | |                                                       
                  / / | | | || | | || | | |                                                       
                 / /_ | |_| || |_| || |_| |                                                       
                |____| \___/  \___/  \___/
                        Welcome to the Config Vali-Diff-erator 2000!
                    Brought  to you by a Network Engineer with way to much
                              time on his hands (gcaudle66)!
            """)
    print("To continue, please input a report name to associate the output to \n \
    ----------------------------------------------------------------------")
    reportname = input("Report Name Prefix: ")
    print(f'Ok....going with {reportname} prefix........')
    print("----------------------------------------------------------------------")
    print("Now enter the name of the config file to import and Vali-Diff-erate! \n \
    ----------------------------------------------------------------------")
    filename = input("Input Filename: ")
    config_file = f"./{filename}"
    report = validate_config(config_file, "./golden_standard.yaml")
                                                                                          

