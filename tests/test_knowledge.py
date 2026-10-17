import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from surveyor.presentation import present,save_presentation,record_decision
from surveyor.knowledge import KnowledgeCatalogue

def make_presentation(root):
    discovery=Path(root)/"source.json"
    discovery.write_text(json.dumps({"schema":"surveyor.discovery.v0","suite":"EMERSON",
        "query":"Morna","results":[{"index":1,"title":"UNESCO Morna",
        "url":"https://www.youtube.com/watch?v=test","provider":"youtube","creator":"UNESCO"}]}))
    return save_presentation(present(discovery),root)

class KnowledgeTests(unittest.TestCase):
    def test_requires_latest_review_approval(self):
        with TemporaryDirectory() as root:
            path=make_presentation(root)
            kb=KnowledgeCatalogue(Path(root)/"knowledge.sqlite")
            with self.assertRaises(ValueError):
                kb.add(path,1,root)
            record_decision(path,1,"approve","Operator","Relevant source",archive=root)
            result=kb.add(path,1,root)
            self.assertEqual(result["status"],"curated_candidate_unverified")
            self.assertEqual(len(kb.search("UNESCO")),1)
            self.assertEqual(len(kb.search("UNESCO")),1)
            kb.close()

    def test_rejection_blocks_subsequent_curate(self):
        with TemporaryDirectory() as root:
            path=make_presentation(root)
            record_decision(path,1,"approve","Operator","First review",archive=root)
            record_decision(path,1,"flag_correct","Operator","Incorrect attribution",archive=root)
            kb=KnowledgeCatalogue(Path(root)/"knowledge.sqlite")
            with self.assertRaises(ValueError):
                kb.add(path,1,root)
            kb.close()

    def test_never_promotes_truth(self):
        with TemporaryDirectory() as root:
            path=make_presentation(root)
            record_decision(path,1,"approve","Operator","For follow up",archive=root)
            kb=KnowledgeCatalogue(Path(root)/"knowledge.sqlite")
            kb.add(path,1,root)
            self.assertTrue(all(x["status"]=="curated_candidate_unverified" for x in kb.search("Morna")))
            kb.close()

if __name__=="__main__":
    unittest.main()
