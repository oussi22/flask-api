import os
import requests
import tarfile
from bs4 import BeautifulSoup
from lxml import etree as ET
from sqlalchemy.exc import SQLAlchemyError
from src.database import Decision, db
from src import create_app
from urllib.parse import urljoin
import logging

logging.basicConfig(level=logging.INFO)

def clean_content(content_elem):
    """Cleans and flattens XML content elements."""
    parts = []
    for elem in content_elem.iter():
        if elem.tag == 'br':
            parts.append('\n')
        if elem.text:
            parts.append(elem.text)
        if elem.tail:
            parts.append(elem.tail)
    return ''.join(parts).strip()

def fetch_tar_urls(base_url):
    """Fetch .tar.gz URLs from the provided base URL."""
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    tar_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.tar.gz')]
    return [urljoin(base_url, link) for link in tar_links]

def process_tar_file(tar_url):
    """Download and process a .tar.gz file containing decision XML files."""
    decisions = []
    try:
        response = requests.get(tar_url, stream=True)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch tar file: {e}")
        return
    
    with tarfile.open(fileobj=response.raw, mode="r|gz") as tar:
        for member in tar:
            if member.isfile() and member.name.endswith('.xml'):
                with tar.extractfile(member) as f:
                    xml_content = f.read()
                    root = ET.fromstring(xml_content)
                    
                    # Extract decision details
                    id_elem = root.find('.//META_COMMUN/ID')
                    title_elem = root.find('.//META_JURI/TITRE')
                    formation_elem = root.find('.//META_JURI_JUDI/FORMATION')
                    content_elem = root.find('.//CONTENU')
                    
                    id_text = id_elem.text if id_elem is not None else ''
                    title_text = title_elem.text if title_elem is not None else ''
                    formation_text = formation_elem.text if formation_elem is not None else ''
                    content_text = clean_content(content_elem) if content_elem is not None else ''
                    
                    decisions.append({
                        'id': id_text,
                        'title': title_text,
                        'formation': formation_text,
                        'content': content_text
                    })

    # Save decisions to database
    save_decisions_to_db(decisions)

def save_decisions_to_db(decisions):
    """Save a list of decisions to the database, avoiding duplicates."""
    try:
        with create_app().app_context():
            # Avoid adding duplicate decisions
            existing_ids = set(row[0] for row in db.session.query(Decision.id).all())
            new_decisions = [decision for decision in decisions if decision['id'] not in existing_ids]
            
            if new_decisions:
                db.session.bulk_insert_mappings(Decision, new_decisions)
                db.session.commit()
                logging.info(f"Added {len(new_decisions)} new decisions.")
            else:
                logging.info("No new decisions to add.")
    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        db.session.rollback()

def fetch_and_store_decisions(base_url):
    """Fetch and process all decisions from the provided base URL."""
    tar_urls = fetch_tar_urls(base_url)
    for tar_url in tar_urls:
        logging.info(f"Processing {tar_url}")
        process_tar_file(tar_url)

if __name__ == "__main__":
    BASE_URL = 'https://echanges.dila.gouv.fr/OPENDATA/CASS/'
    fetch_and_store_decisions(BASE_URL)
