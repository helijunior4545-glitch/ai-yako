import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ProductStructureTests(unittest.TestCase):
    def test_required_templates(self):
        for name in ('base.html','landing.html','workspace.html'):
            self.assertTrue((ROOT/'templates'/'app_qvac_financial'/name).is_file())
    def test_public_views_do_not_perform_financial_actions(self):
        source=(ROOT/'server/api/public/views.py').read_text()
        self.assertNotIn('sign_approved_transaction(',source)
        self.assertNotIn('prepare_transaction(',source)
    def test_models_do_not_reference_commercial_auth(self):
        source=(ROOT/'server/django/models/product.py').read_text()
        for forbidden in ('AUTH_USER_MODEL','app_config.Loja','app_billing'):
            self.assertNotIn(forbidden,source)
    def test_no_private_wallet_key_fields_in_metadata_models(self):
        source=(ROOT/'server/django/models/product.py').read_text()
        for forbidden in ('seed_phrase =','private_key =','mnemonic ='):
            self.assertNotIn(forbidden,source)
    def test_ui_explains_unavailable_integrations(self):
        page=(ROOT/'templates/app_qvac_financial/workspace.html').read_text()
        self.assertIn('No wallet, model, or blockchain is connected',page)
