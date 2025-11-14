from docx import Document
from docx.opc.exceptions import PackageNotFoundError
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from datetime import datetime
from docx.shared import Inches
import os


D_ROUTE = "documents/"


class NewParagraphDeclined(Exception): pass

class WordDoc:
    def __init__(self, name: str | None = None):
        if not name:
            name = datetime.now().strftime("%d-%m-%Y")
        self.name = name
        
        try:
            self.document = Document(D_ROUTE + self.name + ".docx")
        except (FileNotFoundError, PackageNotFoundError):
            self.document = Document()

    def save(self):
        # логировать создание файла после импорта утилиты
        self.document.save(D_ROUTE + self.name + ".docx")

    def heading_exists(self, headline: str) -> bool:
        for paragraph in self.document.paragraphs:
            if paragraph.text.strip() == headline.strip() and paragraph.style.name.startswith('Heading'):
                return True
        return False

    def new_paragraph(self, headline: str = "?", text: str = "..."):
        """returns false if the paragraph was declined"""
        if self.heading_exists(headline):
            raise NewParagraphDeclined()
        self.document.add_heading(headline, level=1)
        self.document.add_paragraph(text)
    
    def find_heading_index(self, headline: str) -> int:
        for i, paragraph in enumerate(self.document.paragraphs):
            if paragraph.text.strip() == headline.strip() and paragraph.style.name.startswith('Heading'):
                return i
        return -1
    
    def remove_paragraph(self, headline: str):
        heading_index = self.find_heading_index(headline)
        
        if heading_index == -1:
            return
        
        heading_element = self.document.paragraphs[heading_index]._element
        heading_element.getparent().remove(heading_element)
        
        if heading_index < len(self.document.paragraphs):
            text_element = self.document.paragraphs[heading_index]._element
            text_element.getparent().remove(text_element)
        
        self.save()

    def extract_all_content(self, filename: str | None = None):
        """
        Извлекает все содержимое документа в виде XML-строки
        """
        if filename:
            doc = Document(f"{filename}.docx")
        else:
            doc = self.document
            
        return doc.element.body.xml
            

def extract_text(file: WordDoc):
    full_text = []
    for paragraph in file.document.paragraphs:
        if paragraph.text.strip():
            full_text.append(paragraph.text)
    return '\n'.join(full_text)

def merge_files(donor: WordDoc, target: WordDoc):
    for element in donor.document.element.body:
        new_element = parse_xml(element.xml)
        target.document.element.body.append(new_element)
    
    target.save()
    print(f"Все содержимое из '{donor.name}.docx' скопировано в '{target.name}.docx'")
    

if __name__ == "__main__":
    try:
        t = WordDoc("conclusion")
        d = WordDoc("lavrova")

        merge_files(d, t)
        
    except Exception as e:
        print(e)