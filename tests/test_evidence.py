import unittest
from surveyor.evidence import SourceReference, ResearchClaim, ResearchPackage, from_inference

class EvidenceTests(unittest.TestCase):
    def test_unverified_response_is_preserved_without_fabricated_sources(self):
        pkg = from_inference("EMERSON", "What is morna?", {"model": "test", "response": "A draft answer"})
        data = pkg.export()
        self.assertEqual(data["raw_response"], "A draft answer")
        self.assertEqual(data["claims"], [])
        self.assertEqual(data["sources"], [])
        self.assertEqual(len(data["content_sha256"]), 64)

    def test_claim_requires_registered_source(self):
        claim = ResearchClaim(statement="A test claim", suite="GOODALL", source_ids=("source-1",))
        pkg = ResearchPackage("GOODALL", "question", "draft", claims=[claim])
        with self.assertRaises(ValueError):
            pkg.validate()

    def test_suggested_source_is_not_verified(self):
        source = SourceReference("https://example.org/study", "Study title")
        claim = ResearchClaim("Test", "CHAKOTAY", source_ids=(source.identifier,),
                              verification_status="source_attached")
        pkg = ResearchPackage("CHAKOTAY", "question", "draft", claims=[claim], sources=[source])
        self.assertEqual(pkg.export()["sources"][0]["acquisition_status"], "suggested")

    def test_cannot_self_certify_reviewed_claim(self):
        with self.assertRaises(ValueError):
            ResearchClaim("Test", "BOURDAIN", verification_status="reviewed")

    def test_invalid_cross_suite_package_rejected(self):
        pkg = ResearchPackage("EMERSON", "question", "draft",
                              claims=[ResearchClaim("Test", "HADID")])
        with self.assertRaises(ValueError):
            pkg.validate()

    def test_retrieved_source_requires_timestamp(self):
        with self.assertRaises(ValueError):
            SourceReference("https://example.org/data", "Data", acquisition_status="retrieved")

    def test_duplicate_source_identifiers_rejected(self):
        source = SourceReference("https://example.org/data", "Data")
        pkg = ResearchPackage("GOODALL", "question", "draft", sources=[source, source])
        with self.assertRaises(ValueError):
            pkg.validate()

if __name__ == "__main__":
    unittest.main()
