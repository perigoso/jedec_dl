#!/usr/bin/env python3

import requests
import shutil
import argparse
import toml
import os

DOCS_URL = "https://www.jedec.org/system/files/docs"


def jedec_login(session: requests.Session, username: str, password: str) -> None:
    LOGIN_URL = "https://www.jedec.org/user/login"

    session.post(
        LOGIN_URL,
        data={
            "name": username,
            "pass": password,
            "form_id": "user_login",
            "op": "Sign+In",
        },
    )

    if "single_login" not in session.cookies:
        raise Exception("Failed to log in")


def jedec_download_doc(
    session: requests.Session, doc_id: str, output_dir: str = "./", try_variation: bool = True
) -> str:
    possible_names = []

    if doc_id != doc_id.upper():
        possible_names.append(doc_id)
        doc_id = doc_id.upper()

    possible_names.append(doc_id)

    if try_variation:
        if "." in doc_id:
            doc_id, doc_rev = doc_id.split(".")
            possible_names.append(doc_id)
            for sep in ["-", "_", ""]:
                possible_names.append(f"{doc_id}{sep}{doc_rev}")
        if "-" in doc_id:
            possible_names.append(doc_id.replace("-", ""))

    if try_variation:
        possible_names.extend([name.lower() for name in possible_names])

    if try_variation:
        # Reafirmed documents
        possible_names.append(doc_id + "_R")
        possible_names.append(doc_id + "_RA")

    local_filename = os.path.join(output_dir, f"{doc_id}.pdf")

    if os.path.isfile(local_filename):
        return doc_id

    for name in possible_names:
        url = f"{DOCS_URL}/{name}.pdf"
        with session.get(url, stream=True, allow_redirects=False) as request:
            if request.status_code == 404:
                continue
            if request.status_code == 403:
                raise Exception(f"Access denied for {doc_id}")
            if request.status_code != 200:
                raise Exception(f"Unexpected status code {request.status_code} for {doc_id}")
            with open(local_filename, "wb") as file:
                shutil.copyfileobj(request.raw, file)
                return doc_id

    raise Exception(f"Could not find {doc_id}")


def main():
    parser = argparse.ArgumentParser(
        prog="jedec_dl", description="Downloads JEDEC documents from their website"
    )
    parser.add_argument('-o', '--output', help='Output directory', type=str)
    parser.add_argument('-c', '--config', help='Path to config file', type=argparse.FileType('r'))
    parser.add_argument('-l', '--list', help='Path to list file of target documents', type=argparse.FileType('r'))
    parser.add_argument('-u', '--username', help='Username for JEDEC account', type=str)
    parser.add_argument('-p', '--password', help='Password for JEDEC account', type=str)
    parser.add_argument('--no-variations', help='Do not look for alternative document naming', type=bool)
    parser.add_argument('docs', nargs='*', help='List of documents to download', type=str)
    args = parser.parse_args()

    config = toml.load(args.config) if args.config else {}

    username = args.username or config.get("username")
    password = args.password or config.get("password")
    if not username or not password:
        print("Username and password are required")
        exit(1)

    docs = []
    docs.extend(args.docs)
    docs.extend(config.get("docs", []))
    docs.extend(args.list.readlines() if args.list else [])
    docs = [doc.strip() for doc in docs]
    if not docs:
        print("No documents specified")
        exit(1)

    output_dir = args.output or config.get("output_dir") or "./"
    no_variations = args.no_variations or bool(config.get("no_variations", False))

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    print(f"Downloading {len(docs)} documents to {output_dir} ...")

    with requests.Session() as session:
        try:
            print("Logging in...")
            jedec_login(session, username, password)
        except Exception as e:
            print(f"Failed to log in: {e}")
            exit(1)

        failed_docs = []
        for doc in docs:
            try:
                print(f"Downloading {doc}...")
                jedec_download_doc(session, doc, output_dir, not no_variations)
            except Exception as e:
                failed_docs.append(doc)
                print(f"Failed to Download {doc}: {e}")

        if failed_docs:
            print(f"Failed to download {len(failed_docs)} documents:")
            for doc in failed_docs:
                print(f"  {doc}")

        print("Done.")


if __name__ == "__main__":
    main()
