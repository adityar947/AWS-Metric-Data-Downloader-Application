import streamlit as st
import subprocess
from datetime import datetime, time
import json
import csv
import os
import yaml

def save_aws_cli_output_to_file(cmd, output_file):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = result.stdout

        if not data:
            st.warning("No data returned by AWS CLI command.")
            return False

        with open(output_file, "w") as file:
            file.write(data)
        
        return True
    except subprocess.CalledProcessError as e:
        st.error("Error: Failed to execute AWS CLI command. Please check your AWS credentials and try again.")
        return False

def fetch_dimensions_from_file(output_file, metric_name):
    try:
        with open(output_file, "r") as file:
            data = json.load(file)

        metrics = data.get('Metrics', [])
        dimensions_set = set()

        for metric in metrics:
            if metric.get('MetricName') == metric_name:
                for dimension in metric.get('Dimensions', []):
                    dimensions_set.add((dimension.get('Name'), dimension.get('Value')))

        return sorted(list(dimensions_set))
    except Exception as e:
        st.error(f"Error: Failed to fetch dimensions from file. {str(e)}")
        return []

def fetch_related_dimensions(output_file, primary_dimension_value, metric_name):
    try:
        with open(output_file, "r") as file:
            data = json.load(file)

        metrics = data.get('Metrics', [])
        related_dimensions = []

        for metric in metrics:
            if metric.get('MetricName') == metric_name:
                for dimension in metric.get('Dimensions', []):
                    if dimension.get('Value') == primary_dimension_value:
                        for related_dimension in metric.get('Dimensions', []):
                            if related_dimension.get('Value') != primary_dimension_value:
                                related_dimensions.append({
                                    'Name': related_dimension.get('Name'),
                                    'Value': related_dimension.get('Value')
                                })

        return related_dimensions
    except Exception as e:
        st.error(f"Error: Failed to fetch related dimensions from file. {str(e)}")
        return []


def fetch_and_save_metric_data(start_time, end_time, period, service, metric_name, dimensions, aws_region, output_format, stat):
    with open("metrics.yaml", "r") as file:
        metrics_config = yaml.safe_load(file)

    metric_info = None
    for metric in metrics_config.get("metrics_to_be_collected", {}).get(service, []):
        if metric.get("name") == metric_name:
            metric_info = metric
            break

    if not metric_info:
        st.error("Error: Metric details not found in the YAML file.")
        return False

    namespace = metric_info.get("namespace")
    unit = metric_info.get("unit")

    cmd = [
        "aws",
        "cloudwatch",
        "get-metric-data",
        "--region", aws_region,
        "--metric-data-queries",
        json.dumps([{
            "Id": "metric_data",
            "MetricStat": {
                "Metric": {
                    "Namespace": namespace,
                    "MetricName": metric_name,
                    "Dimensions": [{"Name": d[0], "Value": d[1]} for d in dimensions]
                },
                "Period": period,
                "Stat": stat,
                "Unit": unit
            },
            "ReturnData": True
        }]),
        "--start-time", start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "--end-time", end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = result.stdout

        if not data:
            st.warning("No data returned by AWS CLI command.")
            return False
        elif "An error occurred" in data:
            st.warning(f"Error encountered while fetching data: {data}")
            return False

        data_json = json.loads(data)
        metric_data_results = data_json.get("MetricDataResults", [])
        if not metric_data_results:
            st.warning("No data available for the specified time range.")
            return False

        timestamps = metric_data_results[0].get("Timestamps", [])
        values = metric_data_results[0].get("Values", [])

        if not timestamps or not values:
            st.warning("No data available for the specified time range.")
            return False

        total_value = sum(values)
        average_value = total_value / len(values)
        formatted_average_value = f"{average_value:.2f}"

        st.write(f"Average value for the selected period is: {formatted_average_value}")

        if output_format == "csv":
            file_name = f"{metric_name}_{start_time.strftime('%Y-%m-%dT%H-%M-%S')}_{end_time.strftime('%Y-%m-%dT%H-%M-%S')}.csv"
            file_path = os.path.join("static", file_name)
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp (UTC)", "Value"])
                writer.writerows(zip(timestamps, values))
        else:
            file_name = f"{metric_name}_{start_time.strftime('%Y-%m-%dT%H-%M-%S')}_{end_time.strftime('%Y-%m-%dT%H-%M-%S')}.json"
            file_path = os.path.join("static", file_name)
            with open(file_path, "w") as file:
                file.write(json.dumps({
                    "Timestamps": timestamps,
                    "Values": values
                }, indent=4))

        return file_path
    except subprocess.CalledProcessError as e:
        st.error("Error: Failed to fetch metric data. Please check your AWS credentials and try again.")
        return False

def validate_json_input(json_input):
    try:
        return json.loads(json_input)
    except json.JSONDecodeError:
        return None

def fetch_instance_names(aws_region):
    cmd = [
        "aws", "ec2", "describe-instances",
        "--region", aws_region,
        "--query", "Reservations[*].Instances[*].[InstanceId, Tags[?Key=='Name'].Value | [0]]",
        "--output", "json"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = result.stdout

        if not data:
            st.warning("No data returned by AWS CLI command.")
            return []

        instances = json.loads(data)
        instance_list = []

        for reservation in instances:
            for instance in reservation:
                instance_id = instance[0]
                instance_name = instance[1] if len(instance) > 1 else 'Unnamed'
                instance_list.append(f"{instance_id} ({instance_name})")

        return instance_list
    except subprocess.CalledProcessError as e:
        st.error("Error: Failed to fetch EC2 instances. Please check your AWS credentials and try again.")
        return []
    
def main():
    st.title("AWS Metric Data Downloader")

    start_date = st.date_input("Select start date", value=datetime.utcnow().date())
    start_time = st.time_input("Select start time", value=time(0, 0))
    
    end_date = st.date_input("Select end date", value=datetime.utcnow().date())
    st.write(f"Current UTC time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    end_time = st.time_input("Select end time", value=time(23, 59))

    start_datetime = datetime.combine(start_date, start_time)
    end_datetime = datetime.combine(end_date, end_time)

    if end_datetime <= start_datetime:
        st.error("Error: End time must be after start time.")
        return

    period_options = {
        "1 second": 1,
        "5 seconds": 5,
        "10 seconds": 10,
        "30 seconds": 30,
        "1 minute": 60,
        "5 minutes": 300,
        "15 minutes": 900,
        "1 hour": 3600,
        "6 hours": 21600,
        "1 day": 86400,
        "7 days": 604800
    }

    period = st.selectbox("Select period", list(period_options.keys()), index=6)
    
    stat_options = ["Average", "Minimum", "Maximum", "Sum", "SampleCount"]
    stat = st.selectbox("Select statistic", stat_options, index=0)

    service = st.selectbox("Select AWS Service", ["ec2", "rds", "lambda", "alb", "nlb", "sqs", "apigateway", "elasticsearch", "eventbridge"], index=0)

    with open("metrics.yaml", "r") as file:
        metrics_config = yaml.safe_load(file)

    if not metrics_config or "metrics_to_be_collected" not in metrics_config:
        st.error("Error: Metrics configuration file is not properly loaded.")
        return

    service_metrics = metrics_config["metrics_to_be_collected"].get(service, [])
    if not service_metrics:
        st.error(f"Error: Configuration for service '{service}' not found in the YAML file.")
        return

    metric_names = [metric.get("name") for metric in service_metrics]
    metric_name = st.selectbox("Select Metric Name", metric_names)

    # Find the namespace of the selected metric name
    selected_metric = next((metric for metric in service_metrics if metric.get("name") == metric_name), None)
    if not selected_metric:
        st.error(f"Error: Metric '{metric_name}' not found in the configuration.")
        return

    namespace = selected_metric.get("namespace")

    aws_region = st.text_input("Enter AWS Region", value="us-east-1")

    output_file = f"{service}_metrics.json"
    cmd = [
        "aws", "cloudwatch", "list-metrics",
        "--namespace", namespace,
        "--region", aws_region
    ]

    if save_aws_cli_output_to_file(cmd, output_file):
        st.success(f"Metrics data saved to {output_file}")

        # Get all dimensions related to the selected metric name from the service_metric output file
        dimensions = fetch_dimensions_from_file(output_file, metric_name)
        
        if service == "ec2":
            instance_list = fetch_instance_names(aws_region)
            if instance_list:
                instance_id = st.selectbox("Select EC2 Instance", instance_list)
                instance_id_value = instance_id.split(' ')[0]
                dimensions.append(("InstanceId", instance_id_value))

        selected_primary_dimension = st.selectbox("Select Primary Dimension", [f"{d[0]}={d[1]}" for d in dimensions])

        if not selected_primary_dimension:
            st.warning("Please select a primary dimension.")
            return

        primary_dimension_name, primary_dimension_value = selected_primary_dimension.split('=', 1)

        # Check if there are related dimensions
        related_dimensions = fetch_related_dimensions(output_file, primary_dimension_value, metric_name)

        # Automatically select related dimensions
        all_dimensions = [(primary_dimension_name, primary_dimension_value)] + [(d.get('Name'), d.get('Value')) for d in related_dimensions]

        output_format = st.selectbox("Select Output Format", ["csv", "json"])
        if st.button("Fetch and Save Metric Data"):
            file_path = fetch_and_save_metric_data(start_datetime, end_datetime, period_options[period], service, metric_name, all_dimensions, aws_region, output_format, stat)
            if file_path:
                st.success(f"Metric data saved successfully at {file_path}")
                with open(file_path, "rb") as file:
                    st.download_button(
                        label="Download data",
                        data=file,
                        file_name=os.path.basename(file_path),
                        mime="text/csv" if output_format == "csv" else "application/json"
                    )

if __name__ == "__main__":
    main()
