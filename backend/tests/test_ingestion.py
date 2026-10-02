import pymupdf
from eduapp.ingest import extract, chunk_pages
from eduapp import ocr


def test_native_gibberish_is_quarantined_and_ocr_retains_original(tmp_path, monkeypatch):
    path = tmp_path / 'legacy.pdf'
    with pymupdf.open() as pdf:
        page = pdf.new_page()
        page.insert_text((72,72), 'evsjv legacy font content cannot be indexed as Bengali')
        pdf.save(path)
    native = extract(path)
    assert native[0]['status'] == 'review'
    recognized = 'বাংলা ভাষার ব্যাকরণ সম্পর্কে এই পাঠে আলোচনা করা হয়েছে। ভাষার নিয়মের সমষ্টি হলো ব্যাকরণ।'
    monkeypatch.setattr(ocr, 'recognize', lambda *args: recognized)
    pages = extract(path, ocr=True)
    assert pages[0]['status'] == 'ok'
    assert pages[0]['method'] == 'tesseract-ben-eng'
    assert pages[0]['raw_text'] == native[0]['text']
    assert pages[0]['text'] == recognized


class Tokenizer:
    def encode(self, text, **kwargs):
        return list(text)
    def decode(self, ids, **kwargs):
        return ''.join(ids)


def test_chunking_is_deterministic_page_scoped_and_excludes_review():
    pages = [
        {'page':1,'status':'ok','text':'বাংলা ভাষার ব্যাকরণ সম্পর্কে এই পাঠে আলোচনা করা হয়েছে।'},
        {'page':2,'status':'review','text':'Unreadable source must not be retrieved.'},
    ]
    first = chunk_pages(pages, Tokenizer(), 'ssc-2026-bangla-2', 'hash-one')
    assert first == chunk_pages(pages, Tokenizer(), 'ssc-2026-bangla-2', 'hash-one')
    assert {c['page'] for c in first} == {1}
    assert first[0]['text'] in pages[0]['text']
    assert first[0]['id'] != chunk_pages(pages, Tokenizer(), 'ssc-2026-bangla-2', 'hash-two')[0]['id']
