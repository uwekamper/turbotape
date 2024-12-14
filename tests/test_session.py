import json
import os
from unittest.mock import patch
from unittest import TestCase

from turbotape.session import (
    try_environment_token,
    create_tape_session,
)

class TestSession(TestCase):

    def test_try_environment_token(self):
        # Set environment variable
        vars = {
            "TAPE_API_KEY": 'user_key_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiLvv73vv73vv73vv73vv73vv71IXHUwMDAxK28iLCJzY29wZSI6InVrX3YxIiwidHlwZSI6IlVTRVJfQVBJX0tFWSJ9.KtVPcZXwRnlCsI-Nih4M9-PxL8kwpufyif8ltryGzJM',
        }
        with patch.dict('os.environ', vars):
            self.assertEqual(
                "abc123456789",
                try_environment_token()["access_token"]
            )
            self.assertEqual(
                "testclientid",
                try_environment_token()["client_id"]
            )
            self.assertEqual(
                "bearer",
                try_environment_token()["token_type"]
            )

    def test_try_environment_token_not_set(self):
        self.assertEqual(None, try_environment_token())