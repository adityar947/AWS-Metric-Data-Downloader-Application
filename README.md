# AWS Metric Data Downloader Application

## Table of Contents:
1. **Overview**
2. **Installation**
3. **Application Workflow**
4.  **Functions Description**
    - **Save_aws_cli_output_to_file**
    - **Fetch_dimensions_from_file**
    - **Fetch_related_dimensions**
    - **Fetch_and_save_metric_data**
    - **Validate_json_input**
    - **fetch_instance_names**
5. **User Interface**
6. **YAML Configuration**
7. **How to Use**

## 1. Overview:
The AWS Metric Data Downloader is a Streamlit-based web application that allows users to fetch and save AWS CloudWatch metric data for various AWS services. Users can specify a time range, metric name, dimensions, and other parameters to retrieve and save metric data in either CSV or JSON format.

## 2. Installation:
To install and run this application, follow these steps:

Configure AWS CLI:
`aws configure`

Create Directory and place project files:
`mkdir /opt/streamlit`
`cd /opt/streamlit`

Create virtual environment:
`python3 -m venv env`
`source /opt/streamlit/env/bin/activate`

Install dependencies:
`pip install streamlit`
`pip install pyyaml`

Run the Streamlit application:
`nohup streamlit run app.py &`

## 3. Application Workflow
    1. User selects the start and end date/time for the metric data.
    2. User selects the period and statistic for the data.
    3. User selects the AWS service and metric name.
    4. The application fetches the list of dimensions for the selected metric.
    5. User selects the primary dimension and any related dimensions.
    6. The application fetches the metric data and saves it to a file.
    7. User can download the file in the selected format (CSV or JSON).

## 4. Functions Description:

### save_aws_cli_output_to_file

    def save_aws_cli_output_to_file(cmd, output_file):
        ...
    **Purpose:** Executes an AWS CLI command and saves the output to a specified file.
    **Parameters:**
    cmd: List of strings representing the AWS CLI command.
    output_file: Path to the file where the output will be saved.
    Returns: True if the command is executed successfully and the output is saved, False otherwise.

### fetch_dimensions_from_file

    def fetch_dimensions_from_file(output_file, metric_name):
        ...
    **Purpose:** Fetches the dimensions of a specified metric from a JSON file.
    **Parameters:**
    output_file: Path to the JSON file containing metric data.
    metric_name: Name of the metric for which dimensions are to be fetched.
    Returns: List of tuples representing the dimensions.

### fetch_related_dimensions
    def fetch_related_dimensions(output_file, primary_dimension_value, metric_name):
        ...
    **Purpose:** Fetches dimensions related to a specified primary dimension value from a JSON file.
    **Parameters:**
    output_file: Path to the JSON file containing metric data.
    primary_dimension_value: Value of the primary dimension.
    metric_name: Name of the metric.
    Returns: List of dictionaries representing related dimensions.

### fetch_and_save_metric_data
    def fetch_and_save_metric_data(start_time, end_time, period, service, metric_name, dimensions, aws_region, output_format, stat):
        ...
    **Purpose:** Fetches metric data from AWS CloudWatch and saves it to a file.
    **Parameters:**
    start_time: Start time for the metric data.
    end_time: End time for the metric data.
    period: Period for the metric data.
    service: AWS service name.
    metric_name: Metric name.
    dimensions: List of tuples representing dimensions.
    aws_region: AWS region.
    output_format: Output format (CSV or JSON).
    stat: Statistic type.
    Returns: Path to the saved file if successful, False otherwise.

### validate_json_input
    def validate_json_input(json_input):
        ...
    **Purpose:** Validates JSON input.
    **Parameters:** json_input: JSON input string.
    Returns: Parsed JSON object if valid, None otherwise.

### fetch_instance_names
    def fetch_instance_names(aws_region):
        ...
    **Purpose:** Fetches the names of EC2 instances in a specified AWS region.
    **Parameters:** aws_region: AWS region.
    Returns: List of instance names.

## 5. User Interface:
The user interface is built using Streamlit and includes the following components:

    **Title:** Displays the title "AWS Metric Data Downloader".
    **Date and Time Inputs:** Allows the user to select the start and end date/time.
    **Period and Statistic Selection:** Dropdowns to select the period and statistic for the data.
    **Service and Metric Selection:** Dropdowns to select the AWS service and metric name.
    **Dimension Selection:** Dropdown to select the primary dimension and any related dimensions.
    **Output Format Selection:** Dropdown to select the output format (CSV or JSON).
    **Fetch and Save Button:** Button to fetch and save the metric data.

## 6. YAML Configuration:
    The application uses a YAML configuration file (metrics.yaml) to store details of the metrics to be collected for each service. The structure of the YAML file is as follows:
    
    metrics_to_be_collected:
      ec2:
        - name: "CPUUtilization"
          namespace: "AWS/EC2"
          unit: "Percent"
          dimensions:
            - Name: "InstanceId"
              Example: "i-05bcffabccdeee00b"
      rds:
        - name: "DatabaseConnections"
          namespace: "AWS/RDS"
          unit: "Count"
          dimensions:
            - Name: "DBInstanceIdentifier"
              Example: "my-rds-instance"
        <!-- Add other services and metrics as needed -->

## 7. How to Use:

    **Access Application:** Access the application over the url.
    **Select Date and Time:** Use the date and time inputs to select the start and end date/time.
    **Select Period and Statistic:** Use the dropdowns to select the period and statistic.
    **Select Service and Metric:** Use the dropdowns to select the AWS service and metric name.
    **Select Dimensions:** Use the dropdowns to select the primary dimension and any related dimensions.
    **Select Output Format:** Use the dropdown to select the output format (CSV or JSON).
    **Fetch and Save Data:** Click the "Fetch and Save Metric Data" button to fetch the data and save it to a file.
    **Download Data:** Use the download button to download the saved file.

    By following these steps, users can easily fetch and save AWS CloudWatch metric data for various AWS services using the AWS Metric Data Downloader application.