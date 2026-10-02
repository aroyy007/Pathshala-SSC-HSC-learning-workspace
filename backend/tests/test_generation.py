import pytest
from eduapp.generation import validate

EVIDENCE = [{'id': 'source-one', 'page': 8, 'text': 'কল্যাণীর বয়স ছিল পনেরো বছর।'}]


def test_citation_page_comes_from_evidence():
    result = validate({'status': 'answered', 'answer': 'পনেরো বছর।', 'citations': [
        {'evidence_id': 'source-one', 'quote': 'পনেরো বছর', 'page': 999}
    ]}, EVIDENCE)
    assert result['citations'][0]['page'] == 8


@pytest.mark.parametrize('result', [None, [], {'status': 'answered', 'answer': 'x', 'citations': None},
    {'status': 'answered', 'answer': 'x', 'citations': ['bad']},
    {'status': 'answered', 'answer': 'x', 'citations': []},
    {'status': 'answered', 'answer': 'x', 'citations': [{'evidence_id': 'other-book', 'quote': 'পনেরো বছর'}]},
    {'status': 'answered', 'answer': 'x', 'citations': [{'evidence_id': 'source-one', 'quote': 'ষোলো বছর'}]},
])
def test_rejects_malformed_or_unsupported_answers(result):
    with pytest.raises(ValueError):
        validate(result, EVIDENCE)


def test_abstention_has_no_citations():
    assert validate({'status': 'insufficient_evidence', 'answer': 'এই বইয়ে পাইনি।', 'citations': []}, EVIDENCE)['citations'] == []
