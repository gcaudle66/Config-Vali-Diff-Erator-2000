# Config Vali-Diff-erator 2000

## Overview

The Config Vali-Diff-erator 2000 is a Python-based tool designed for network engineers to validate configuration files (based on configuration files on a Cisco IOS device but could be adapted to any config really!) against a predefined "golden standard." It provides detailed reports of matched, unmatched, and differing lines in various formats, including plain text and a visually appealing HTML diff. Basically, the intent is to provide a tool to help provide config compliance in an environment. You define what the sections of a config should look like...hostname, AAAA policy, interfaces, routing protocol....whatever. You define the sections of config to check in the "golden_standard.yaml" and if done correctly, this script will kick out reports telling you all you need to know!

---

## Features

- **Normalization:** Automatically formats configuration files for consistent comparison.
- **Validation Reports:** Generates reports for matched, unmatched, and differing lines in the config.
- **Visual Diff:** Creates an HTML file with a color-coded diff for easy analysis.
- **Placeholder Support:** Use placeholders (e.g., `{{regex}}`) in your `golden_standard.yaml` for more flexible comparisons.
- **Rich Output:** Leverages the `Rich` library for visually appealing terminal output and diff reports.

---

## Usage Instructions

### Prerequisites

1. **Install Python dependencies**:
   ```bash
   pip install ciscoconfparse pyyaml rich
Prepare Files:
Ensure the golden_standard.yaml file contains the configuration sections and expected values for comparison.
Place the configuration file (config.txt) to be validated in the same directory as the script.
How to Use
Run the script using the command line:

bash
Copy code
python main.py
Follow the prompts:

Report Name Prefix: Provide a name or identifier to associate with the output reports.
Config File Name: Specify the filename of the configuration to validate.
The tool will generate the following reports:

<prefix>-validation_failures.txt: Contains unmatched lines.
<prefix>-validation_successes.txt: Contains matched lines.
<prefix>-validation_differences.txt: Summarizes differences between the actual and expected configurations.
<prefix>-color_diff.html: A colorful diff visualization in HTML format.
Open the HTML diff in your browser for a detailed comparison:

bash
Copy code
open <prefix>-color_diff.html
Placeholder Values and Regex
In the golden_standard.yaml, you can use placeholders like {{regex}} for flexible comparisons. For example:

yaml
Copy code
access-lists:
  - "ip access-list standard 10"
  - "10 permit {{10\\.0\\.0\\.\\d{1,3}}}"
The placeholder {{10\\.0\\.0\\.\\d{1,3}}} acts as a regex to match any IP addresses in the 10.0.0.x range. This feature is useful for validating configurations with dynamic or variable values.

Example Workflow
Prepare the golden_standard.yaml:

yaml
Copy code
vrfs:
  - "vrf definition clinical"
  - " description ClinicalTraffic"
  - " address-family ipv4"
  - " exit-address-family"

access-lists:
  - "ip access-list standard 10"
  - "10 permit {{10\\.0\\.0\\.\\d{1,3}}}"
Run the tool:

Input a report name like test_project.
Provide the configuration filename, e.g., config.txt.
Analyze Results:

Check text reports for unmatched or matched lines.
Open the HTML diff for an interactive visualization.
Outputs
Matched Lines Report (<prefix>-validation_successes.txt): Lists all lines that matched between the configuration and the golden standard.

Unmatched Lines Report (<prefix>-validation_failures.txt): Highlights configuration lines that were expected but not found.

Differences Report (<prefix>-validation_differences.txt): Summarizes key differences in a structured format.

HTML Diff Report (<prefix>-color_diff.html): A color-coded diff for visually comparing actual and expected configurations.

Acknowledgments
This project would not have been possible without the incredible tools and libraries provided by the open-source community, including:

CiscoConfParse
PyYAML
Rich
Special thanks to gcaudle66 (Me) for his contributions, inspiration, and thorough testing of this tool to ensure its effectiveness and robustness.

Additionally, a shoutout to OpenAI's ChatGPT for supporting the development and documentation process.

License
This project is open-source and available under the MIT License.
