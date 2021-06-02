import json
import os
import subprocess
import tempfile
import urllib.parse
from collections import defaultdict
from subprocess import CalledProcessError

import requests
from cloudaux.aws.sts import boto3_cached_conn
from service import Service
from service_action import ServiceAction

federation_base_url = "https://signin.aws.amazon.com/federation"
account_number = os.environ["AWS_ACCOUNT_ID"]
role_name = os.environ["AWS_ROLE_NAME"]


def _get_creds():
    """
    Assumes into the target account and obtains Access Key, Secret Key, and Token
    :return: URL-encoded dictionary containing Access Key, Secret Key, and Token
    """
    _, credentials = boto3_cached_conn(
        "iam",
        account_number=account_number,
        assume_role=role_name,
        return_credentials=True,
    )

    # For local dev, comment out the line above
    # and then put the data into this format:
    # credentials = {
    #     'AccessKeyId': '',
    #     'SecretAccessKey': '',
    #     'SessionToken': ''
    # }

    creds = json.dumps(
        dict(
            sessionId=credentials["AccessKeyId"],
            sessionKey=credentials["SecretAccessKey"],
            sessionToken=credentials["SessionToken"],
        )
    )

    creds = urllib.parse.quote(creds, safe="")
    return creds


def _get_signin_token(creds):
    """
    Exchanges credentials dictionary for a signin token.
    1) Creates URL using credentials dictionary.
    2) Sends a GET request to that URL and parses the response looking for
    a signin token.
    :return: Signin Token
    """
    url = "{base}?Action=getSigninToken&Session={creds}"
    url = url.format(base=federation_base_url, creds=creds)
    return requests.get(url).json()["SigninToken"]


def call_phantom(token, output_file):
    """Shells out to phantomjs to login to the AWS console and gather data"""
    path = os.path.dirname(__file__)
    console_js = os.path.join(path, "awsconsole.js")

    try:
        # print("Calling Phantom!")
        p = subprocess.Popen(
            [
                "/home/runner/work/policyuniverse/policyuniverse/phantomjs-2.1.1-linux-x86_64/bin/phantomjs",
                console_js,
                token,
                output_file,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        output, errs = p.communicate(timeout=120)
        # print("Output: ", output)
        if errs:
            print("Errors: ", errs)
    except subprocess.TimeoutExpired:
        print("PhantomJS timed out")
        return 1  # return code 1 for timeout
    except CalledProcessError:
        print("PhantomJS exited: {}".format(p.returncode))
        return p.returncode
    else:
        # print("PhantomJS exited: 0")
        return 0


def parse_service_data(data):
    """Create a map of service objects from the weird JSON we get from the console."""
    services = defaultdict()
    for service_url, service_details in data["services"]["_embedded"].items():
        service = Service(service_url, service_details)
        services[service.service_name] = service
    return services


def parse_service_action_data(data, services):
    """Add service actions to the map created by `parse_service_data()`"""
    for service in data["actions"].keys():
        for _, action_details in data["actions"][service]["_embedded"].items():
            action = ServiceAction(services[service], action_details)
            services[service].actions[action.action_name] = action


def gather_data_from_console():
    """Login to AWS Console and gather data on all AWS Services and Service Actions (Permissions)"""
    creds = _get_creds()
    token = _get_signin_token(creds)
    with tempfile.NamedTemporaryFile() as f:
        ret_code = call_phantom(token, f.name)
        service_data = f.read()
        if ret_code == 0:
            service_data = json.loads(service_data)
        else:
            print(
                "Phantom process returned non-zero exit code: {ret_code}".format(
                    ret_code=ret_code
                )
            )
            print("File contents:\n{service_data}".format(service_data=service_data))
            raise Exception(
                "Phantom returned non-zero exit code: {ret_code}".format(
                    ret_code=ret_code
                )
            )
    return service_data


def process_data(service_data):
    """Build a map of services and permissions and format it nicely."""
    services = parse_service_data(service_data)
    parse_service_action_data(service_data, services)

    output = dict()
    for _, service in services.items():
        output[service.display_name] = service.toJSON()

    return output


def _print_updated_actions(service, actions, verb):
    """Prints any added/removed actions."""
    if actions:
        print('**Service "{service}" {verb}:**'.format(service=service, verb=verb))
        for action in sorted(list(actions)):
            print("- {action}".format(action=action))
        print("")


def updates_available(service_data):
    """
    Using our version of policyuniverse, determine if there are significant updates to the service data.
    Should also do some sanity checking so we don't send a PR that removes all services or something crazy.
    """
    from policyuniverse import service_data as deployed_data

    if deployed_data == service_data:
        print("No changes whatsoever.")
        return False

    services_added = set(service_data.keys()) - set(deployed_data.keys())
    services_removed = set(deployed_data.keys()) - set(service_data.keys())

    if services_added:
        print("**Services Added:**   ", sorted(list(services_added)))
    if services_removed:
        print("**Services Removed:** ", sorted(list(services_removed)))

    services_in_both = set(service_data.keys()).intersection(set(deployed_data.keys()))

    # Now lets look at the actions under each service
    actions_modified = False
    for service in services_in_both:
        service_body = service_data[service]

        old_actions = set(deployed_data[service].get("actions").keys())
        new_actions = set(service_body.get("actions").keys())

        actions_added = new_actions - old_actions
        actions_removed = old_actions - new_actions

        _print_updated_actions(service, actions_added, "Added")
        _print_updated_actions(service, actions_removed, "Removed")

        if actions_added or actions_removed:
            actions_modified = True

    # Sanity Check
    if len(services_removed) > 20:
        print(
            "There were {services_removed} services removed. Too many for a PR".format(
                services_removed=len(services_removed)
            )
        )
        return False

    if services_added or services_removed:
        return True

    # Don't return inside the loop because we want to print out all the changes.
    if actions_modified:
        return True

    # This could be a category or a doc change or a regex change as well.
    print(
        "Dicts don't match but no service/action changes found. Maybe a doc URL or Regex or Action Category?"
    )
    return True


def main():
    """Gather Data, Parse Data, Format Data, Save to disk."""
    service_data = gather_data_from_console()
    service_data = process_data(service_data)

    # For local dev on the PR logic:
    # with open('output_formatted.json') as infile:
    #     service_data = json.load(infile)

    updates_available(service_data)

    with open("output_formatted.json", "w") as outfile:
        json.dump(service_data, outfile, indent=2, sort_keys=True)
        outfile.write("\n")

    # print(json.dumps(service_data, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
