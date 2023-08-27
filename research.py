import requests
import os
import argparse
from api import api
import hashlib
from filter import read_pdf,find_similar_papers

apikey = api
CORE_API_BASE_URL = 'https://api.core.ac.uk/'


def parse_args():
    parser = argparse.ArgumentParser(description="Search tool with query and limit.")

    parser.add_argument('-Q',"--query", type=str, required=False, help="The search query.")
    parser.add_argument('-D',"--depth", type=int, required=False, help="The search limit depth.")
    parser.add_argument('-d',"--directory", type=str, required=False,help="The directory containing the files to process.")
    parser.add_argument('-s',"--similarity", type=str, required=False,help="Helps you if you want to find similar papers with the given paper.")
    parser.add_argument('-n',"--number", type=int,required=False,help="Number of results you want to find similar to the given paper.")

    parser.add_argument('-r', '--remove_duplicate_files', action='store_true', help="Remove duplicate files from a directory. Requires a directory argument if used independently.")

    args = parser.parse_args()
    return args

def get_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def remove_duplicate_files(directory):
    file_hashes = {}  # Store file hashes and their paths

    # Collect hashes of files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_hash = get_file_hash(file_path)
            if file_hash in file_hashes:
                # Remove duplicate file
                print(f"Removing duplicate: {file_path}")
                os.remove(file_path)
            else:
                file_hashes[file_hash] = file_path


def download_pdf_with_user_agent(title, pdf_url, path='.'):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(pdf_url, headers=headers)
        response.raise_for_status()  # Raise an exception if there's an error

        # Construct a safe filename for the PDF
        safe_title = "".join(c if c.isalnum() else "_" for c in title)
        pdf_filename = f"{safe_title}.pdf"
        pdf_path = os.path.join(path, pdf_filename)

        # Check if the file already exists and rename if necessary
        count = 1
        while os.path.exists(pdf_path):
            pdf_filename = f"{safe_title}_{count}.pdf"
            pdf_path = os.path.join(path, pdf_filename)
            count += 1
        try:
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(response.content)
        except OSError:
            pdf_filename = f"{safe_title[:50]}.pdf"
            pdf_path = os.path.join(path, pdf_filename)

            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(response.content)


        print(f"Downloaded '{title}' as '{pdf_filename}' to '{pdf_path}'")

    except requests.exceptions.RequestException as e:
        print(f"Error while downloading '{title}': {e}")


if __name__ == "__main__":

    headers={"Authorization":"Bearer "+apikey}
    args = parse_args()
    if args.similarity and not args.number:
        parser.error("Number of similar results must be specified when using the --similarity option by using -n use --help for more.")
    query = args.query
    dir = args.directory
    search_limit = str(args.depth)
    singlework = requests.get(f"https://api.core.ac.uk/v3/search/works?q={query}&limit={search_limit}",headers=headers)
    c = 0
    pdf = 0
    base_dir = "research_papers"
    final_dst = ""
    if (query and search_limit):
        for i in singlework.json()["results"]:
            print("[+]Type:", str(i["documentType"]),"\n[+]URL:", str(i["downloadUrl"]),"\n[+]Title:", str(i["title"]))
            if "pdf" in i["downloadUrl"]:
                print(f"[+] PDF Detected for work type: {i['documentType']} and title: {i['title']}")
                final_dst = os.path.join(base_dir, query)
                if not os.path.exists(final_dst):
                    os.makedirs(final_dst)
                    print(f"Directory '{final_dst}' created successfully.")
                if dir:
                    if not os.path.exists(dir):
                        os.makedirs(dir)
                    final_dst = dir
                download_pdf_with_user_agent(i['title'], i["downloadUrl"], path=final_dst)
                pdf += 1
                print("[+] PDF Downloaded",str(pdf))

            print("-"*45+"\n"*3+"-"*45)
            # os.system("clear")
            c += 1
            print("[+ Total Files Found:",str(c))
            print("[+]Pdf File Downloaded:", str(pdf))



    if args.remove_duplicate_files:
        if dir or final_dst:
            if not final_dst:
                final_dst = dir
            remove_duplicate_files(final_dst)
        else:
            print("[-] Enter The Directory By -d or --directory")
    if args.similarity:
        if dir or final_dst:
            if not final_dst:
                final_dst = dir
            print(args.similarity)
            print(args.number)
            find_similar_papers(args.similarity, final_dst, args.number)
