from pathlib import Path
import os
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[2]
if os.getenv('EDUAPP_SKIP_DOTENV') != '1':
 load_dotenv(ROOT / '.env')
DATA = Path(os.getenv('EDUAPP_DATA_DIR', str(ROOT / 'data')))
DATA.mkdir(parents=True, exist_ok=True)
MODEL = os.getenv('EMBEDDING_MODEL', 'Qwen/Qwen3-Embedding-0.6B')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-3.5-flash-lite')
BOOKS = [
 {'id':'ssc-2026-bangla-1','level':'SSC','paper':1,'title':'বাংলা সাহিত্য','subtitle':'Bangla · First paper','color':'blue','description':'গল্প, কবিতা আর সাহিত্যের জগৎ।','source_note':'NCTB textbook mirror. Exam-edition alignment pending verification.'},
 {'id':'ssc-2026-bangla-2','level':'SSC','paper':2,'title':'বাংলা ব্যাকরণ','subtitle':'Bangla · Second paper','color':'green','description':'ভাষার নিয়ম, ব্যাকরণ ও নির্মিতি।','source_note':'NCTB textbook mirror. Exam-edition alignment pending verification.'},
 {'id':'hsc-2026-bangla-1','level':'HSC','paper':1,'title':'সাহিত্যপাঠ','subtitle':'Bangla · First paper','color':'purple','description':'সাহিত্যের গভীরে, নতুন ভাবনায়।','source_note':'NCTB textbook mirror. Supplementary volume is outside this four-book collection.'},
 {'id':'hsc-2026-bangla-2','level':'HSC','paper':2,'title':'বাংলা দ্বিতীয় পত্র','subtitle':'Bangla · Second paper','color':'orange','description':'শুদ্ধ ভাষা, সুন্দর প্রকাশ।','source_note':'Bangladesh Open University textbook. General-board HSC26 syllabus equivalence is not verified.'},
]

def book_by_id(book_id):
 return next((b for b in BOOKS if b['id']==book_id), None)
