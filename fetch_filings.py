from wsgiref import headers
import requests

cik = "0001318605"
def get_latest_10k(cik):
    headers = {'User-Agent': 'Marco Sison marcosison.1558@gmail.com'}
    url = f"http://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=headers)
    data = response.json()
    forms = data['filings']['recent']['form']
    dates = data['filings']['recent']['filingDate']
    accession_numbers = data['filings']['recent']['accessionNumber']
    primary_documents = data['filings']['recent']['primaryDocument']
    target_index = None
    for i,form in enumerate(forms):
        if form == '10-K':
            print(f"Form: {form}, Filing Date: {dates[i]}, Accession Number: {accession_numbers[i]},Primary Document: {primary_documents[i]}")
            target_index = i
            break
    accession_number = accession_numbers[target_index].replace("-", "")
    doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{primary_documents[target_index]}"
    doc_response = requests.get(doc_url, headers=headers)
    return doc_response.text
print(get_latest_10k(cik)[:500])
from bs4 import BeautifulSoup
raw_html = get_latest_10k(cik)
def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    for tag in soup.find_all(style=lambda s: s and 'display:none' in s.replace(' ', '')):
        tag.decompose()
    clean_text = soup.get_text(separator=' ', strip=True)
    return clean_text
clean_text = clean_html(raw_html)
print(clean_text[:500])
import os
def save_filing_text(text, filepath):
    os.makedirs('data', exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)
save_filing_text(clean_text, 'data/tsla_10k_2025.txt')
def chunk_text(data, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(data):
        end = start + chunk_size
        chunk = data[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks
chunks = chunk_text(clean_text)
print(len(chunks))
print(chunks[0][-250:])
print("---")
print(chunks[1][:250])
