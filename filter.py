import os
import fitz  # PyMuPDF
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def abbreviate_file_name(file_name, max_length=20):
    if len(file_name) <= max_length:
        return file_name
    else:
        return file_name[:max_length] + "..."

# def read_pdf(file_path):
#     text = ""
#     with open(file_path, 'rb') as pdf_file:
#         reader = PyPDF2.PdfReader(pdf_file)
#         num_pages = len(reader.pages)

#         for page_num in range(num_pages):
#             page = reader.pages[page_num]
#             text += page.extract_text()

#     return text


def read_pdf(file_path):
    text = ""
    try:
        pdf_document = fitz.open(file_path)

        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            text += page.get_text()

        pdf_document.close()
    except Exception as e:
        print(f"Error reading PDF '{file_path}': {str(e)}")

    return text

def find_similar_papers(folder_path, num_similar_papers,paper_path=None,keywords=None):
    # List all files in the folder
    file_names = os.listdir(folder_path)

    # Read the content of the specified paper and store it

    if paper_path:
        specified_paper_text = read_pdf(paper_path)
    else:
        specified_paper_text = keywords

    # Read the content of each file in the folder and store it in a list
    research_papers = []
    for file_name in file_names:
        file_path = os.path.join(folder_path, file_name)
        text = read_pdf(file_path)
        research_papers.append(text)

    # Combine the specified paper and all research papers
    all_texts = [specified_paper_text] + research_papers

    # Initialize the TF-IDF vectorizer
    if paper_path:
        vectorizer = TfidfVectorizer(stop_words='english')
    else:
        vectorizer = TfidfVectorizer()

    # Create the TF-IDF matrix
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # Calculate cosine similarity between the specified paper and all other papers
    cosine_similarities = cosine_similarity(tfidf_matrix)

    num_papers = len(research_papers)

    specified_paper_index = 0  # The specified paper will be the first in the list

    # Function to get top n most similar papers for the specified paper
    def get_similar_papers(paper_index, n):
        similar_indices = sorted(range(num_papers + 1), key=lambda i: cosine_similarities[paper_index][i], reverse=True)
        similar_indices.remove(paper_index)  # Remove the paper itself from the list
        return similar_indices[:n]

    # Find similar papers for the specified paper
    # similar_papers = get_similar_papers(specified_paper_index, num_similar_papers)

    # for index in similar_papers:
    #     print(index)
    #     print(f"Specified Paper is similar to Paper {file_names[index]} with similarity score {cosine_similarities[specified_paper_index][index]}")
    similar_papers = get_similar_papers(specified_paper_index, num_similar_papers)

    # Create lists to store file names and their corresponding similarity scores
    file_names_list = []
    similarity_scores_list = []

    for index in similar_papers:
        try:
            file_name = file_names[index]
            similarity_score = cosine_similarities[specified_paper_index][index]
            file_names_list.append(file_name)
            similarity_scores_list.append(similarity_score)

            print(f"Specified Paper is similar to Paper {file_name} with similarity score {similarity_score}")

        except IndexError as err:
            print(err)

    # Create a bar graph to visualize the similarity scores
    plt.figure(figsize=(10, 6))
    abbreviated_file_names = [abbreviate_file_name(file_name) for file_name in file_names_list]
    plt.bar(abbreviated_file_names, similarity_scores_list)
    plt.xlabel("Paper")
    plt.ylabel("Similarity Score")
    plt.title("Similarity Scores between Specified Paper and Other Papers")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Show the graph
    plt.show()


if __name__ == "__main__":
    folder_path = input("Enter the path to the folder containing research papers: ")
    specified_paper_path = input("Enter the path to the specified paper: ")
    keyword_input = input("Enter keywords (comma-separated): ")
    keywords = [kw.strip() for kw in keyword_input.split(",")]

    find_similar_papers(specified_paper_path, folder_path, keywords)

# import os
# import PyPDF2
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
#
# def read_pdf(file_path):
#     text = ""
#     with open(file_path, 'rb') as pdf_file:
#         reader = PyPDF2.PdfReader(pdf_file)
#         num_pages = len(reader.pages)
#
#         for page_num in range(num_pages):
#             page = reader.pages[page_num]
#             text += page.extract_text()
#
#     return text
#
# def find_similar_papers(paper_path, folder_path, num_similar_papers):
#     # List all files in the folder
#     file_names = os.listdir(folder_path)
#
#     # Read the content of the specified paper and store it
#     specified_paper_text = read_pdf(paper_path)
#
#     # Read the content of each file in the folder and store it in a list
#     research_papers = []
#     for file_name in file_names:
#         file_path = os.path.join(folder_path, file_name)
#         text = read_pdf(file_path)
#         research_papers.append(text)
#
#     # Initialize the TF-IDF vectorizer
#     vectorizer = TfidfVectorizer(stop_words='english')
#
#     # Create the TF-IDF matrix
#     tfidf_matrix = vectorizer.fit_transform([specified_paper_text] + research_papers)
#
#     # Calculate cosine similarity between the specified paper and all other papers
#     cosine_similarities = cosine_similarity(tfidf_matrix)
#
#     num_papers = len(research_papers)
#
#     specified_paper_index = 0  # The specified paper will be the first in the list
#
#     # Function to get top n most similar papers for the specified paper
#     def get_similar_papers(paper_index, n):
#         similar_indices = sorted(range(num_papers + 1), key=lambda i: cosine_similarities[paper_index][i], reverse=True)
#         similar_indices.remove(paper_index)  # Remove the paper itself from the list
#         return similar_indices[:n]
#
#     # Find similar papers for the specified paper
#     similar_papers = get_similar_papers(specified_paper_index, num_similar_papers)
#
#     for index in similar_papers:
#         print(f"Specified Paper is similar to Paper {research_papers[index]} with similarity score {cosine_similarities[specified_paper_index][index]}")
#
# if __name__ == "__main__":
#
#     # Usage example
#     folder_path = input("Enter the path to the folder containing research papers: ")
#     specified_paper_path = input("Enter the path to the specified paper: ")
#
#     find_similar_papers(specified_paper_path, folder_path)


# import os
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# import PyPDF2
#
# # Path to the folder containing research paper files
# folder_path = input("Enter the path: ")
#
# # List all files in the folder
# file_names = os.listdir(folder_path)
#
# def read_pdf(file_path):
#     text = ""
#     with open(os.path.join(folder_path,file_path), 'rb') as pdf_file:
#         reader = PyPDF2.PdfReader(pdf_file)
#         num_pages = len(reader.pages)
#
#         for page_num in range(num_pages):
#             page = reader.pages[page_num]
#             text += page.extract_text()
#
#     return text
#
#
# # Read the content of each file and store it in a list
# research_papers = []
# for file_name in file_names:
#     text = read_pdf(file_name)
#     research_papers.append(text)
# # Initialize the TF-IDF vectorizer
# vectorizer = TfidfVectorizer(stop_words='english')
#
# # Create the TF-IDF matrix
# tfidf_matrix = vectorizer.fit_transform(research_papers)
#
# # Calculate cosine similarity between all pairs of papers
# cosine_similarities = cosine_similarity(tfidf_matrix)
#
# # Assuming `cosine_similarities` is the cosine similarity matrix
# num_papers = len(research_papers)
#
# # Create a list of paper indices for reference
# paper_indices = list(range(num_papers))
#
# # Function to get top n most similar papers for a given paper index
#
# # Example usage
# paper_index_to_query = 0  # Index of the paper you want to find similar papers for
# num_similar_papers = 5
# similar_papers = get_similar_papers(paper_index_to_query, num_similar_papers)
#
# for index in similar_papers:
#     print(f"Paper {paper_index_to_query} is similar to Paper {index} with similarity score {cosine_similarities[paper_index_to_query][index]}")
