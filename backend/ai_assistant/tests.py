from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.contrib.auth import get_user_model
from ai_assistant.services import GeminiService

User = get_user_model()


class AIAssistantTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_ai_team_builder_fallback_and_structure(self):
        url = reverse('ai_assistant:api_team_builder')
        data = {
            'title': 'AI Healthcare Platform',
            'description': 'Build an AI patient management system with medical summaries and React dashboard.',
            'budget': 3000,
            'category': 'Full-Stack Product'
        }
        res = self.client.post(url, data, content_type='application/json')
        self.assertEqual(res.status_code, 200)

        json_data = res.json()
        self.assertIn('analysis', json_data)
        self.assertIn('roles', json_data['analysis'])
        self.assertIn('required_skills', json_data['analysis'])
        self.assertGreater(len(json_data['analysis']['roles']), 0)

    @patch('ai_assistant.services.GeminiService.get_model')
    def test_ai_team_builder_with_mocked_gemini(self, mock_get_model):
        class MockModel:
            def generate_content(self, prompt):
                class MockResponse:
                    text = '{"project_summary": "AI Mock App", "recommended_squad_size": 3, "estimated_weeks": 4, "required_skills": ["Python", "React", "Gemini API"], "roles": [{"role": "AI Architect", "primary_skills": ["Python"], "responsibilities": "Lead AI", "estimated_allocation": "100%", "recommended_experience": "Expert"}]}'
                return MockResponse()

        mock_get_model.return_value = MockModel()

        res = GeminiService.build_team_recommendation(
            project_title='Mock Project',
            description='Build an AI system',
            budget=2000
        )
        self.assertTrue(res['is_ai_powered'])
        self.assertEqual(res['analysis']['recommended_squad_size'], 3)
        self.assertEqual(res['analysis']['roles'][0]['role'], 'AI Architect')

    def test_ai_chatbot_endpoint(self):
        url = reverse('ai_assistant:api_chatbot')
        res = self.client.post(url, {'message': 'How does AdvIT form teams?', 'session_id': 'test_sess_123'}, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertIn('reply', res.json())
