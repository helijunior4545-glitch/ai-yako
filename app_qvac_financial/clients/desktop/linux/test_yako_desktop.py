import unittest
from yako_desktop import analyze_offline

class DesktopTests(unittest.TestCase):
    def test_flags(self):
        result=analyze_offline('Urgent guaranteed leverage')
        self.assertEqual(len(result['flags']),3)
        self.assertEqual(result['risk'],'REVIEW REQUIRED')
    def test_no_claims(self):
        result=analyze_offline('What is a wallet?')
        self.assertEqual(result['risk'],'NOT ASSESSED')
        self.assertIn('not QVAC',result['mode'])
    def test_empty(self):
        with self.assertRaises(ValueError): analyze_offline('  ')

if __name__=='__main__': unittest.main()
