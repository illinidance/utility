import os
from typing import List

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_credentials() -> Credentials:
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def get_sheet_data(sheet_id: str, range: str, creds: Credentials) -> List:
    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range=range).execute()
        values = result.get("values", [])
        return values
    except HttpError as err:
        print(err)


def reconcile():
    creds = get_credentials()

    signup_sheet_id = "1nkrob9EKXhS9VrNxMTo_tzOekOzJv69M8U35j4UW41Q"
    membership_sheet_id = "1PDDOfzf3ggA4x-ghDqZ5ft9uM51EICbSOfRbSfJDAkI"

    # Get sign up sheet and deduplicate on name and email. This sheet contains
    # of all people who ever wanted to get on our mailing list.
    df_signup = get_sheet_data(signup_sheet_id, "Form Responses 1", creds)
    df_signup = pd.DataFrame(df_signup[1:], columns=df_signup[0], dtype="string")
    df_signup["First Name"] = df_signup["First Name"].str.capitalize().str.strip()
    df_signup["Last Name"] = df_signup["Last Name"].str.capitalize().str.strip()
    df_signup["Email"] = df_signup["Email"].str.lower().str.strip()
    df_signup = df_signup.dropna(subset=["Email"])
    df_signup = df_signup.drop_duplicates(subset=["Email"], keep="first")
    df_signup.to_csv("sheet_signup.csv", header=True, index=False)

    # Get mailing list subscription status sheet. We don't deduplicate this
    # sheet as it's an operation log because people may change their
    # subscription many times. By walking through this sheet against the sign-up
    # sheet, we can reconcile who's still subscribing.
    df_membership = get_sheet_data(membership_sheet_id, "Form Responses 1", creds)
    df_membership = pd.DataFrame(
        df_membership[1:], columns=df_membership[0], dtype="string"
    )
    df_membership["First Name"] = (
        df_membership["First Name"].str.capitalize().str.strip()
    )
    df_membership["Last Name"] = df_membership["Last Name"].str.capitalize().str.strip()
    df_membership["Email"] = df_membership["Email"].str.lower().str.strip()
    df_membership = df_membership.dropna(subset=["Email"])
    df_membership = df_membership.sort_values(by=["Timestamp"])
    df_membership.to_csv("sheet_membership.csv", header=True, index=False)

    df_signup["subscribing"] = True
    for _, row in df_membership.iterrows():
        if row["Status"] == "Unsubscribe: You will stop receiving emails from us.":
            df_signup.loc[
                (df_signup["Email"] == row["Email"]),
                "subscribing",
            ] = False
        else:
            if not (df_signup["Email"] == row["Email"]).any():
                new_row = list(row.values)
                new_row[-1] = True
                df_signup.loc[len(df_signup)] = new_row
            else:
                df_signup.loc[
                    (df_signup["Email"] == row["Email"]),
                    "subscribing",
                ] = True

    df_subscribing = df_signup[df_signup["subscribing"]]
    df_subscribing.to_csv("sheet_subscribing.csv", header=True, index=False)
    print("Done.")


if __name__ == "__main__":
    reconcile()
